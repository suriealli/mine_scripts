#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.DB.DBReverse")
#===============================================================================
# 数据进程反向模块
# 注意这个模块所有的函数有要注意线程安全
#===============================================================================
from Common.Connect import Who
from ComplexServer import Connect

def OnNewLogic(sessionid, processid):
	if processid in ProcessIDToSessionID:
		print "GE_EXC process(%s) with session id(%s) but receive new session id(%s)." % (processid, ProcessIDToSessionID[processid], sessionid)
	ProcessIDToSessionID[processid] = sessionid

def OnLostLogic(sessionid):
	for processid, sid in ProcessIDToSessionID.items():
		if sid == sessionid:
			del ProcessIDToSessionID[processid]
			break
	else:
		print "GE_EXC can't find session id(%s) on lost logic." % (sessionid)

if "_HasLoad" not in dir():
	ProcessIDToSessionID = {}
	Connect.NewConnectCallBack.RegCallbackFunction(Who.enWho_Logic_, OnNewLogic)
	Connect.LostConnectCallBack.RegCallbackFunction(Who.enWho_Logic_, OnLostLogic)
