#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.Gateway.ClientMgr")
#===============================================================================
# 客户端管理
#===============================================================================
import traceback
import cGatewayForward

if "_HasLoad" not in dir():
	ClientMsgDispatch = {}
	ClientNew = lambda clientKey: None
	ClientLost = lambda clientKey: None

def OnClientNew(clientkey):
	'''
	通知有新的客户端到来
	@param clientkey:
	'''
	#print "OnClientNew", clientkey
	ClientNew(clientkey)

def OnClientLost(clientkey):
	'''
	通知有客户端失去了
	@param clientkey:
	'''
	#print "OnClientLost", clientkey
	ClientLost(clientkey)

def OnClientMsg(clientkey, msgtype, msgobj):
	'''
	有客户端发来消息(登录相关的消息)
	@param clientkey:
	@param msgtype:消息类型
	@param msgobj:消息对象
	'''
	fun = ClientMsgDispatch.get(msgtype)
	if not fun:
		cGatewayForward.KickClient(clientkey)
		print "GE_EXC, Gateway recv unknown client msg(%s)" % msgtype
		return
	try:
		if not fun(clientkey, msgobj):
			cGatewayForward.KickClient(clientkey)
			print "GE_EXC, Gateway recv undeal client msg(%s) by fun(%s) kickckient" % (msgtype, fun.__name__)
	except:
		traceback.print_exc()

def SetClientNewFun(fun):
	'''
	设置新客户端连接处理函数
	@param fun:函数
	'''
	global ClientNew
	ClientNew = fun

def SetClientLostFun(fun):
	'''
	设置新客户端断开连接处理函数
	@param fun:函数
	'''
	global ClientLost
	ClientLost = fun

def RegClientMsgDistribute(msgtype, fun):
	'''
	注册客户端消息处理函数
	@param msgtype:消息类型
	@param fun:处理函数 def fun(clientkey, msgobj)
	'''
	if msgtype in ClientMsgDispatch:
		print "GE_EXC, repeat client msg(%s) distribute fun(%s)." % (msgtype, str(fun))
		return
	ClientMsgDispatch[msgtype] = fun

