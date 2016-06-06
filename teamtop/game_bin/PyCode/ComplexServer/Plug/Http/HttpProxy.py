#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# Http访问代理
#===============================================================================
import cComplexServer
from Common import CValue
from Common.Message import PyMessage
from Common.Connect import Who
from ComplexServer import Connect
from ComplexServer.Plug.Http import HttpWork

def __HttpRequest_Local(host, port, uri, get, post = None, waittime = 10, backfun = None, regparam = None):
	'''
	HTTP本地直接访问
	@param host:域名或者ip
	@param port:端口
	@param uri:地址
	@param get:get参数字典
	@param post:post参数字典（如果post is None 者是get访问否则是post访问）
	@param waittime:等待时间
	@param backfun:回调函数 def fun(responser, regparam)
	@param regparam:回调参数
	'''
	HttpWork.OnHttpRequest_MainThread(host, port, uri, get, post, waittime, (backfun, regparam))

def __HttpsRequest_Local(host, port, uri, get, post = None, waittime = 10, backfun = None, regparam = None):
	'''
	HTTPs本地直接访问
	@param host:域名或者ip
	@param port:端口
	@param uri:地址
	@param get:get参数字典
	@param post:post参数字典（如果post is None 者是get访问否则是post访问）
	@param waittime:等待时间
	@param backfun:回调函数 def fun(responser, regparam)
	@param regparam:回调参数
	'''
	HttpWork.OnHttpsRequest_MainThread(host, port, uri, get, post, waittime, (backfun, regparam))

def __HttpRequest_Net(host, port, uri, get, post = None, waittime = 10, backfun = None, regparam = None):
	'''
	HTTP远程代理访问
	@param host:域名或者ip
	@param port:端口
	@param uri:地址
	@param get:get参数字典
	@param post:post参数字典（如果post is None 者是get访问否则是post访问）
	@param waittime:等待时间
	@param backfun:回调函数 def fun(responser, regparam)
	@param regparam:回调参数
	'''
	cComplexServer.SendPyMsgAndBack(HTTP_SESSION, PyMessage.Http_Request, (host, port, uri, get, post, waittime), waittime, backfun, regparam)

def __HttpsRequest_Net(host, port, uri, get, post = None, waittime = 10, backfun = None, regparam = None):
	'''
	HTTPs远程代理访问
	@param host:域名或者ip
	@param port:端口
	@param uri:地址
	@param get:get参数字典
	@param post:post参数字典（如果post is None 者是get访问否则是post访问）
	@param waittime:等待时间
	@param backfun:回调函数 def fun(responser, regparam)
	@param regparam:回调参数
	'''
	cComplexServer.SendPyMsgAndBack(HTTP_SESSION, PyMessage.Https_Request, (host, port, uri, get, post, waittime), waittime, backfun, regparam)

def OnHttpRequest_Net(sessionid, msg):
	'''
	HTTP远程代理收到访问消息，真正访问HTTP
	@param sessionid: 连接的sessionid
	@param msg: 请求访问消息
	'''
	backfunid, (host, port, uri, get, post, waittime) = msg
	HttpWork.OnHttpRequest_MainThread(host, port, uri, get, post, waittime, (sessionid, backfunid))

def OnHttpsRequest_Net(sessionid, msg):
	'''
	HTTPs远程代理收到访问消息，真正访问HTTPs
	@param sessionid: 连接的sessionid
	@param msg: 请求访问消息
	'''
	backfunid, (host, port, uri, get, post, waittime) = msg
	HttpWork.OnHttpsRequest_MainThread(host, port, uri, get, post, waittime, (sessionid, backfunid))

def NetMethod(ip, port):
	'''
	默认情况下，HTTP是本地直接范围的。
	该函数将HTTP访问模式改为远程代理访问。
	@param ip:远程代理的ip
	@param port:远程代理的端口
	'''
	# 设置代理参数
	global HTTP_SESSION, HTTP_IP, HTTP_PORT, HttpRequest, HttpsRequest
	HTTP_SESSION = CValue.MAX_UINT32
	HTTP_IP = ip
	HTTP_PORT = port
	HttpRequest = __HttpRequest_Net
	HttpsRequest = __HttpsRequest_Net
	# 连接远程代理
	ConnectHttpServer()

def ConnectHttpServer(argv = None, param = None):
	'''
	真正的连接远程代理
	@param owner:兼容tick系统的占位参数
	@param argv:兼容tick系统的占位参数
	@param param:兼容tick系统的占位参数
	'''
	global HTTP_SESSION
	HTTP_SESSION = cComplexServer.Connect(HTTP_IP, HTTP_PORT, Who.enWho_Http, 1000, CValue.MAX_UINT16, 1000, CValue.MAX_UINT16)

def OnLost(sessionid):
	'''
	当远程代理断开连接的时候，自动重连
	@param sessionid:
	'''
	global HTTP_SESSION
	HTTP_SESSION = CValue.MAX_UINT32
	cComplexServer.RegTick(5, ConnectHttpServer)

def IAMHttpServer():
	'''
	对于远程代理，注册好HTTP代理请求的处理函数
	'''
	cComplexServer.RegDistribute(PyMessage.Http_Request, OnHttpRequest_Net)
	cComplexServer.RegDistribute(PyMessage.Https_Request, OnHttpsRequest_Net)

if "_HasLoad" not in dir():
	HTTP_SESSION = None
	HTTP_IP = None
	HTTP_PORT = None
	HttpRequest = __HttpRequest_Local
	HttpsRequest = __HttpsRequest_Local
	# 设置远程代理端口连接的时候重连机制
	Connect.LostConnectCallBack.RegCallbackFunction(Who.enWho_Http, OnLost)

