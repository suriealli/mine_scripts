#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.ProcessMgr")
#===============================================================================
# 进程管理
#===============================================================================
from Common import CValue
from Common.Connect import Who
from ComplexServer import Connect
from ComplexServer.Plug.Control import ControlProxy
from World import Define

class ControlProcess(object):
	def __init__(self, sessionid, processid):
		self.session_id = sessionid
		self.processid = processid
		self.control_roles = {}
	
	def __str__(self):
		return "ControlProcess-%s" % self.session_id

def OnNewProcess(sessionid, processid):
	ControlProcesssSessions[sessionid] = cp = ControlProcess(sessionid, processid)
	if processid in ControlProcesssIds:
		print "GE_EXC, repeat processid(%s) in OnNewProcess" % processid
	ControlProcesssIds[processid] = cp

def OnLostProcess(sessionid):
	control_process = ControlProcesssSessions.get(sessionid)
	if control_process is None:
		return
	processid = control_process.processid
	# 通知断线（需是非关服状态）
	from ComplexServer import Init
	if not Init.IsStopState:
		from Control import RoleMgr
		for role_id in control_process.control_roles.keys():
			RoleMgr.OnRoleExit(CValue.MAX_UINT32, role_id)
	# 删除进程
	del ControlProcesssSessions[sessionid]
	
	if processid in ControlProcesssIds:
		del ControlProcesssIds[processid]


def GetCrossServerSessionId():
	#获取跨服服务器的sessionId
	cp = ControlProcesssIds.get(Define.GetDefaultCrossID())
	if not cp:
		return None
	return cp.session_id

def GetSessionId(processId):
	#根据进程Id获取连接sessionId
	cp = ControlProcesssIds.get(processId)
	if not cp:
		return None
	return cp.session_id

if "_HasLoad" not in dir():
	ControlProcesssSessions = {}
	ControlProcesssIds = {}
	Connect.NewConnectCallBack.RegCallbackFunction(Who.enWho_Control_, OnNewProcess)
	Connect.LostConnectCallBack.RegCallbackFunction(Who.enWho_Control_, OnLostProcess)
	# 如果是本地进程，伪造进程连接
	if ControlProxy.IsLocal():
		OnNewProcess(CValue.MAX_UINT32, 0)

