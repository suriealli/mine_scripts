#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.ControlCall")
#===============================================================================
# 进程间调用
#===============================================================================
import sys
import cComplexServer
from Common import CValue
from Common.Message import PyMessage
from Control import ProcessMgr
from ComplexServer.Plug.Control import ControlProxy


def OnServerCall(sessionid, msg):
	processId, modulename, funname, param = msg
	param = (modulename, funname, param)
	if processId == 0:
		#所有的逻辑进程,不包括跨服进程
		CS = ControlProxy.SendLogicMsg
		PC = PyMessage.Control_OnServerCall
		for sessionId, cp in ProcessMgr.ControlProcesssSessions.iteritems():
			if cp.processid >= 30000:
				continue
			CS(sessionId, PC, param)
	else:
		#非0，指定的单个逻辑进程
		sessionId = ProcessMgr.GetSessionId(processId)
		if sessionId is None or sessionId == CValue.MAX_UINT32:
			print "GE_EXC OnServerCall error processId(%s)" % processId 
			return
		ControlProxy.SendLogicMsg(sessionId, PyMessage.Control_OnServerCall, param)

def OnSuperServerCall(sessionid, msg):
	processId, modulename, funname, param = msg
	param = (modulename, funname, param)
	if processId == 0:
		#所有的逻辑进程.不包括跨服进程
		CS = ControlProxy.SendLogicBigMsg
		PC = PyMessage.Control_OnSuperServerCall
		for sessionId, cp in ProcessMgr.ControlProcesssSessions.iteritems():
			if cp.processid >= 30000:
				continue
			CS(sessionId, PC, param)
	else:
		#非0，指定的单个逻辑进程
		sessionId = ProcessMgr.GetSessionId(processId)
		if sessionId is None or sessionId == CValue.MAX_UINT32:
			print "GE_EXC OnSuperServerCall error processId(%s)" % processId 
			return
		ControlProxy.SendLogicBigMsg(sessionId, PyMessage.Control_OnSuperServerCall, param)


def OnControlServerCall(sessionid, msg):
	moduleName, funName, param = msg
	module = sys.modules.get(moduleName)
	if not module:
		print "GE_EXC, OnControlServerCall not find module(%s)." % moduleName
		return
	fun = getattr(module, funName, None)
	if not fun:
		print "GE_EXC, OnControlServerCall module(%s) not find fun(%s)." % (moduleName, funName)
		return
	fun(param)

def LogicServerCall(processId, moduleName, funName, param):
	msg = (moduleName, funName, param)
	if processId == 0:
		#所有的逻辑进程, 不包括跨服进程
		CS = ControlProxy.SendLogicMsg
		PC = PyMessage.Control_OnServerCall
		for sessionId, cp in ProcessMgr.ControlProcesssSessions.iteritems():
			if cp.processid >= 30000:
				continue
			CS(sessionId, PC, msg)
	else:
		#非0，指定的单个逻辑进程
		sessionId = ProcessMgr.GetSessionId(processId)
		if sessionId is None or sessionId == CValue.MAX_UINT32:
			print "GE_EXC OnServerCall error processId(%s)" % processId 
			return
		ControlProxy.SendLogicMsg(sessionId, PyMessage.Control_OnServerCall, msg)


if "_HasLoad" not in dir():
	cComplexServer.RegDistribute(PyMessage.Control_ServerCall, OnServerCall)
	cComplexServer.RegDistribute(PyMessage.Control_ControlServerCall, OnControlServerCall)
	cComplexServer.RegDistribute(PyMessage.Control_SuperServerCall, OnSuperServerCall)
	