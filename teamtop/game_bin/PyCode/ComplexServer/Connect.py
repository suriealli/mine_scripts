#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Connect")
#===============================================================================
# 连接管理
#===============================================================================
from Common.Connect import Who
from Util import Callback

if "_HasLoad" not in dir():
	# 默认只能接受GM连接
	ICanWho = set([Who.enWho_GM_])
	# Connect连接字典
	ConnectDict = {}

def RegICanWho(who):
	'''
	注册可接受的连接类型
	@param who:
	'''
	ICanWho.add(who)

def OnNewConnect(sessionid, who, processid):
	'''
	
	有新的连接来了
	@param sessionid:连接的sessionid
	@param who:连接的类型
	'''
	#print "OnNewConnect", sessionid, who
	if who not in ICanWho:
		print "GE_EXC, i can who(%s) but has who(%s)" % (str(ICanWho), who)
		return False
	ConnectDict[sessionid] = {"who":who}
	NewConnectCallBack.CallAllFunctions(who, sessionid, processid)
	return True

def OnLostConnect(sessionid, who):
	'''
	有新的连接失去了
	@param sessionid:连接的sessionid
	@param who:连接的类型
	'''
	#print "OnLostConnect", sessionid, who
	if sessionid in ConnectDict: del ConnectDict[sessionid]
	LostConnectCallBack.CallAllFunctions(who, sessionid)

if "_HasLoad" not in dir():
	NewConnectCallBack = Callback.LocalCallbacks()
	LostConnectCallBack = Callback.LocalCallbacks()

