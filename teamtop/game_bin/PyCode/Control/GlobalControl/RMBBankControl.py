#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.RMBBankControl")
#===============================================================================
# 神石银行控制模块
#===============================================================================
import Environment
import cComplexServer
from Common.Other import GlobalDataDefine
from Common.Message import PyMessage
from Control import ProcessMgr
from ComplexServer.API import GlobalHttp
from ComplexServer.Plug.Control import ControlProxy


if "_HasLoad" not in dir():
	HasChange = False
	BankLogCache = []


def GetBankLog():
	GlobalHttp.GetGlobalData(GlobalDataDefine.RMBBank_Key, AfterGetBankLog, None)


def AfterGetBankLog(response, regparam):
	if not response:
		return
	global BankLogCache
	BankLogCache = response
	SyncBankLogToLogic()

def SyncBankLogToLogic():
	#同步给所有的逻辑进程
	global BankLogCache
	for sessionid in ProcessMgr.ControlProcesssSessions.iterkeys():
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateBankLog, BankLogCache)

def AfterNewHour():
	global BankLogCache, HasChange
	if HasChange is True:
		HasChange = False
		GlobalHttp.SetGlobalData(GlobalDataDefine.RMBBank_Key, BankLogCache)
		SyncBankLogToLogic()


def AddBankLog(sessionId, msg):
	global BankLogCache, HasChange
	HasChange = True
	BankLogCache.append(msg)
	if len(BankLogCache) >= 200:
		BankLogCache.pop(0)


if "_HasLoad" not in dir():
	if Environment.HasControl:
		GetBankLog()
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		cComplexServer.RegDistribute(PyMessage.Control_AddBankLog, AddBankLog)
	
	