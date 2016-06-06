#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# QQ发货确认
#===============================================================================
import time
import Queue
import urllib
import httplib
import threading
from ComplexServer.API import QQHttp
from ComplexServer.Plug.DB import DBHelp
from Integration.Help import OtherHelp

CONFIRM_URI = "/v3/pay/confirm_delivery"
CONFIRM_SQL = "update charge set confirm = CONCAT(confirm, '(%s-%s)') where token = '%s';"
CT = None

def GetConfirmThread():
	global CT
	if CT is None:
		CT = ConfirmThread()
		CT.start()
	return CT

class Confirm(object):
	def __init__(self, openid, openkey, pf, ts, payitem, token_id, billno, version, zoneid, providetype, provide_errno, amt, payamt_coins, pubacct_payamt_coins):
		get = {"openid":openid, "openkey":openkey, "appid":QQHttp.APP_ID, "pf":pf,
			"ts":ts, "payitem":payitem, "token_id":token_id, "billno":billno,
			"version":version, "zoneid":zoneid, "providetype":providetype,
			"provide_errno":0, "amt":amt, "payamt_coins":payamt_coins,
			"pubacct_payamt_coins":pubacct_payamt_coins}
		QQHttp.make_sig(CONFIRM_URI, get, {})
		self.dbid = zoneid
		self.token_id = token_id
		self.url = CONFIRM_URI + "?" + urllib.urlencode(get)
		self.unix_time = int(time.time())
		GetConfirmThread().put(self)
	
	def confirm(self):
		con = httplib.HTTPSConnection(QQHttp.HOST)
		con.request("GET", self.url)
		response = con.getresponse()
		# 访问失败, 再次确认
		if response.status != 200:
			return
		body = eval(response.read())
		# 保存结果
		con = DBHelp.ConnectMasterDBByID(self.dbid)
		with con as cur:
			cur.execute(CONFIRM_SQL % (body["ret"], body["msg"], self.token_id))

class ConfirmThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.queue = Queue.Queue()
	
	def put(self, confirm):
		self.queue.put(confirm)
	
	def run(self):
		while True:
			try:
				confirm = self.queue.get_nowait()
			except:
				time.sleep(1)
				continue
			# 已经超时了，不确认了
			pass_time = int(time.time()) - confirm.unix_time
			if pass_time > 300:
				continue
			# 等待10秒
			if 0 < pass_time < 10:
				time.sleep(10 - pass_time)
			try:
				confirm.confirm()
			except:
				OtherHelp.PrintTraceback(__name__)

