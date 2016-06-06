#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.Http.HttpWork")
#===============================================================================
# HTTP服务模块
#===============================================================================
import time
import datetime
import urllib
import urllib2
import httplib
import HttpCode
import threading
import Queue
import cComplexServer
from ThirdLib import PrintHelp
from ComplexServer import Thread

#import ComplexServer.Plug.Http.HttpWork as A;A.ShowDebug = True

# Http请求
class HttpRequest(object):
	def __init__(self, host, port, uri, get, post, waittime, back):
		self.host = host
		self.port = port
		self.uri = uri
		self.get = get
		self.post = post
		self.waittime = waittime
		self.back = back
		self.beginTime = datetime.datetime.now()
	
	def Execute(self):
		# 计算时间差
		delta = datetime.datetime.now() - self.beginTime
		# 计算剩余时间
		remaintime = self.waittime - delta.total_seconds()
		if remaintime <= 0:
			self.DoResult(HttpCode.HTTP_WAIT_TIME_OVER, None)
			return
		if ShowDebug:
			DoShowDebug("request", self.host, self.port, self.uri, self.get, self.post)
		# http访问
		try:
			if not self.post:
				if self.get:
					url = "http://%s:%s%s?%s" % (self.host, self.port, self.uri, urllib.urlencode(self.get))
				else:
					url = "http://%s:%s%s" % (self.host, self.port, self.uri)
				response = urllib2.urlopen(url, None, remaintime)
			else:
				url = "http://%s:%s%s" % (self.host, self.port, self.uri)
				response = urllib2.urlopen(url, urllib.urlencode(self.post), remaintime)
			if ShowDebug:
				DoShowDebug("request_url", url)
				
			self.DoResult(response.code, response.read())
		except urllib2.HTTPError, e:
			if ShowDebug:
				DoShowDebug("except_request_url", url)
			self.DoResult(e.code,  str(e.msg))
		except urllib2.URLError, e:
			if ShowDebug:
				DoShowDebug("except_request_url", url)
			self.DoResult(HttpCode.HTTP_EXCEPT, str(e.reason))
		except Exception, e:
			if ShowDebug:
				DoShowDebug("except_request_url", url)
			self.DoResult(HttpCode.HTTP_EXCEPT, str(e))
	
	def DoResult(self, code, body):
		if ShowDebug:
			DoShowDebug("response", self.uri, code, body)
		back1, back2 = self.back
		# 如果第一个返回信息是整数，则认为是网络模式
		if type(back1) is int or type(back1) is long:
			# back2就是回调函数id了，如果为0就是不需要回调的
			if back2:
				Thread.ThreadApply(OnHttpResponse_Net_MainThread, (back1, back2, (code, body)))
		# 否则认为是本地模式
		else:
			# back1就是回调函数了，如果为None说明不需要回调
			if back1 is not None:
				Thread.ThreadApply(OnHttpResponse_Local_MainThread, (back1, back2, (code, body)))

# Https请求
class HttpsRequest(object):
	def __init__(self, host, port, uri, get, post, waittime, back):
		self.host = host
		self.port = port
		self.uri = uri
		self.get = get
		self.post = post
		self.waittime = waittime
		self.back = back
		self.beginTime = datetime.datetime.now()
	
	def Execute(self):
		# 计算时间差
		delta = datetime.datetime.now() - self.beginTime
		# 计算剩余时间
		remaintime = self.waittime - delta.total_seconds()
		if remaintime <= 0:
			self.DoResult(HttpCode.HTTP_WAIT_TIME_OVER, None)
			return
		# https访问
		try:
			con = httplib.HTTPSConnection(self.host)
			if self.get:
				con.request("GET", "%s?%s" % (self.uri, urllib.urlencode(self.get)))
			else:
				con.request("POST", self.uri, urllib.urlencode(self.post))
			response = con.getresponse()
			self.DoResult(response.status, response.read())
		except Exception, e:
			self.DoResult(HttpCode.HTTP_EXCEPT, str(e))
	
	def DoResult(self, code, body):
		back1, back2 = self.back
		# 如果第一个返回信息是整数，则认为是网络模式
		if type(back1) is int or type(back1) is long:
			# back2就是回调函数id了，如果为0就是不需要回调的
			if back2:
				Thread.ThreadApply(OnHttpResponse_Net_MainThread, (back1, back2, (code, body)))
		# 否则认为是本地模式
		else:
			# back1就是回调函数了，如果为None说明不需要回调
			if back1 is not None:
				Thread.ThreadApply(OnHttpResponse_Local_MainThread, (back1, back2, (code, body)))

# 工作线程
class WrokThread(threading.Thread):
	def __init__(self, threadQueue):
		threading.Thread.__init__(self)
		self.threadQueue = threadQueue
	
	def run(self):
		self.isrun = True
		while self.isrun:
			try:
				task = self.threadQueue.get_nowait()
				task.Execute()
			except Queue.Empty:
				time.sleep(0.01)
	
	def start(self):
		threading.Thread.start(self)
		# 保存进程信息
		Thread.ThreadID_Name[self.ident] = "DBWorkThread"
	
	def stop(self):
		self.isrun = False
			
if "_HasLoad" not in dir():
	HTTP_THREAD_NUM = 3
	HTTP_QUEUE = Queue.Queue(0)
	HTTP_THREAD_LIST = []
	ShowDebug = False
	ShowDebugLock = threading.Lock()

def DoShowDebug(name, *argv):
	with ShowDebugLock:
		print "===========%s==========" % name
		for o in argv:
			PrintHelp.pprint(o)

def StartWorkThread():
	'''
	开启工作线程
	'''
	for _ in xrange(HTTP_THREAD_NUM):
		thread = WrokThread(HTTP_QUEUE)
		thread.start()
		HTTP_THREAD_LIST.append(thread)

def StopWorkThread():
	'''
	关闭工作线程
	'''
	# 1关闭线程
	for thread in HTTP_THREAD_LIST:
		thread.stop()
	# 2等待线程返回
	for thread in HTTP_THREAD_LIST:
		thread.join(5)
	print "RED, http thread is join."

def OnHttpRequest_MainThread(host, port, uri, get, post, waittime, back):
	'''
	进行Http访问
	@param host:host（域名或IP）
	@param port:port（端口）
	@param uri:地址
	@param get:get字典
	@param post:post字典（not get的时候才生效）
	@param waittime:等待时间
	@param back:返回信息（如何返回）
	'''
	HTTP_QUEUE.put(HttpRequest(host, port, uri, get, post, waittime, back))

def OnHttpsRequest_MainThread(host, port, uri, get, post, waittime, back):
	'''
	进行Https访问
	@param host:host（域名或IP）
	@param port:port（端口）
	@param uri:地址
	@param get:get字典
	@param post:post字典（not get的时候才生效）
	@param waittime:等待时间
	@param back:返回信息（如何返回）
	'''
	HTTP_QUEUE.put(HttpsRequest(host, port, uri, get, post, waittime, back))


def OnHttpResponse_Local_MainThread(backfun, regparam, httpresponse):
	'''
	Http请求返回，本地模式下（主线程调用）
	@param backfun:回调函数
	@param regparam:回调注册参数
	@param httpresponse:Http返回结果
	'''
	backfun(httpresponse, regparam)

def OnHttpResponse_Net_MainThread(sessionid, backfunid, httpresponse):
	'''
	Http请求返回，网络模式下（主线程调用）
	@param sessionid:回调函数
	@param backfunid:回调注册参数
	@param httpresponse:Http返回结果
	'''
	cComplexServer.CallBackFunction(sessionid, backfunid, httpresponse)


