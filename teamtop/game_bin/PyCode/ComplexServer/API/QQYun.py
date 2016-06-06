#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.API.QQYun")
#===============================================================================
# 腾讯云API
#===============================================================================
import hmac
import time
import json
import random
import urllib
import hashlib
import httplib
from ThirdLib import PrintHelp

HOST = "gz-api.tencentyun.com"
ID = None
KEY = None

def get_id():
	global ID
	if ID is None:
		with open("/data/mima/id") as f:
			ID = f.read()
			if ID.endswith("\n"):
				ID = ID[:-1]
			if ID.endswith("\r"):
				ID = ID[:-1]
	return ID

def get_key():
	global KEY
	if KEY is None:
		with open("/data/mima/key") as f:
			KEY = f.read()
			if KEY.endswith("\n"):
				KEY = KEY[:-1]
			if KEY.endswith("\r"):
				KEY = KEY[:-1]
	return KEY

def make_sig(body, method, uri, nonce, timestamp):
	orignal = "body=%s&method=%s&uri=%s&x-txc-cloud-secretid=%s&x-txc-cloud-nonce=%s&x-txc-cloud-timestamp=%s" % (body, method, uri, get_id(), nonce, timestamp)
	hashed = hmac.new(get_key(), orignal, hashlib.sha1)
	# 这里多了换行符，要去掉
	sig = hashed.digest().encode("base64")[:-1]
	return sig

def api_query(uri, method = "GET", **kwgv):
	nonce = random.randint(0, 999999999)
	timestamp = int(time.time())
	if method == "GET":
		body = ""
		if kwgv:
			url = "%s?%s" % (uri, urllib.urlencode(kwgv))
		else:
			url = uri
	else:
		body = json.dumps(kwgv)
		url = uri
	sig = make_sig(body, method, url, nonce, timestamp)
	headers = {"Content-type": "application/json;charset=utf-8",
		"x-txc-cloud-secretid": get_id(), "x-txc-cloud-nonce": nonce,
		"x-txc-cloud-timestamp": timestamp, "x-txc-cloud-signature": sig}
	con = httplib.HTTPConnection(HOST)
	con.request(method, url, body, headers)
	response = con.getresponse()
	return eval(response.read())

def get_token():
	return api_query("/v1/cvms/token", "GET")

def get_cvm_info(lanips):
	return api_query("/v1/cvms", "GET", lanips = lanips)

def get_cvm_bind_info(lanip):
	return api_query("/v1/cvms/domains", "GET", lanip = lanip)

def get_instance_id(domains):
	return api_query("/v1/domains/query_instance_id", "GET", domains = domains)

def cvm_unbind(instanceId, ip, port):
	uri = "/v1/domains/%s/cvm_unbind" % instanceId
	return api_query(uri, "POST", devicesList = [{"lanIp":ip,"port":port}])

def cvm_bind(instanceId, ip, port):
	uri = "/v1/domains/%s/cvm_bind" % instanceId
	return api_query(uri, "POST", lanIps = [ip], port = port)

def request_result(requestId):
	uri = "/v1/requests/%s" % requestId
	return api_query(uri, "GET")

def unbind(instanceId, ip, port):
	response = cvm_unbind(instanceId, ip, port)
	if response["httpCode"] != 200:
		PrintHelp.pprint(response)
		return False
	requestId = response["requestId"]["id"]
	for idx in xrange(9):
		result = request_result(requestId)
		print result["httpCode"]
		if result["httpCode"] == 200:
			return True
		if result["httpCode"] == 202:
			time.sleep(idx)
			continue
		PrintHelp.pprint(result)
		return False

def bind(instanceId, ip, port):
	response = cvm_bind(instanceId, ip, port)
	if response["httpCode"] != 200:
		PrintHelp.pprint(response)
		return False
	requestId = response["requestId"]["id"]
	for idx in xrange(9):
		result = request_result(requestId)
		print result["httpCode"]
		if result["httpCode"] == 200:
			return True
		if result["httpCode"] == 202:
			time.sleep(idx)
			continue
		PrintHelp.pprint(result)
		return False

class Group(object):
	def __init__(self):
		self.bind_once = set()
		self.binds = {}
		self.unbinds = {}
	
	def can_bind(self, instanceid):
		return instanceid not in self.bind_once
	
	def bind(self, instanceid, ip, port):
		if not self.can_bind(instanceid):
			return
		self.binds[(instanceid, ip, port)] = None
	
	def unbind(self, instanceid, ip, port):
		self.unbinds[(instanceid, ip, port)] = None
	
	def execute(self):
		# 先执行绑定
		for key in self.binds.keys():
			response = cvm_bind(*key)
			if response["httpCode"] != 200:
				self.binds[key] = response
			else:
				self.binds[key] = int(response["requestId"]["id"])
		for key in self.unbinds.keys():
			response = cvm_unbind(*key)
			if response["httpCode"] != 200:
				self.unbinds[key] = response
			else:
				self.unbinds[key] = int(response["requestId"]["id"])
		# 再等待结果
		for idx in xrange(4, 10):
			need_wait = False
			for key, requestId in self.binds.items():
				if requestId is True:
					continue
				if not isinstance(requestId, (int, long)):
					continue
				result = request_result(requestId)
				if result["httpCode"] == 200:
					self.binds[key] = True
				elif result["httpCode"] == 202:
					need_wait = True
				else:
					self.binds[key] = result
			for key, requestId in self.unbinds.items():
				if requestId is True:
					continue
				if not isinstance(requestId, (int, long)):
					continue
				result = request_result(requestId)
				if result["httpCode"] == 200:
					self.unbinds[key] = True
				elif result["httpCode"] == 202:
					need_wait = True
				else:
					self.unbinds[key] = result
			if need_wait:
				time.sleep(idx)
			else:
				break

if __name__ == "__main__":
	HOST = "api.yun.qq.com"
	#PrintHelp.pprint(get_token())
	#PrintHelp.pprint(get_cvm_info("10.207.149.29"))
	#PrintHelp.pprint(get_cvm_bind_info("10.207.149.29"))
	#PrintHelp.pprint(get_instance_id("banben1.app100718848.twsapp.com"))
	#print(unbind(100000056609, "10.207.149.29", 8008))
	#print(bind(100000056609, "10.207.149.29", 8008))
	#g = Group()
	#g.bind()

