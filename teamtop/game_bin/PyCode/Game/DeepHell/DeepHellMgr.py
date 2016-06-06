#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DeepHell.DeepHellMgr")
#===============================================================================
# 深渊炼狱 Mgr
#===============================================================================
import cRoleMgr
import cNetMessage
import cComplexServer
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from Game.SysData import WorldData
from Game.Role import Event, Status
from Game.Role.Data import EnumInt1
from Game.GlobalData import ZoneName
from Game.DeepHell import DeepHellScene, DeepHellDefine
import cProcess
import cDateTime


if "_HasLoad" not in dir():
	#活动图标开关
	IS_START = False
	#活动开关
	IS_INIT = False
	#活动ID
	ACTIVEID = 0
	#可进入时间戳
	CANIN_TIMESTAMP = 0
	#深渊炼狱_活动状态_同步 格式：(IS_START, IS_INIT, ACTIVEID)
	DeepHell_ActiveState_S = AutoMessage.AllotMessage("DeepHell_ActiveState_S", "深渊炼狱_活动状态_同步")
	
	#深渊炼狱_通知客户端倒计时_同步 格式：(timeStamp)
	DeepHell_CanInTimeStamp_S = AutoMessage.AllotMessage("DeepHell_CanInTimeStamp_S", "深渊炼狱_可进入时间戳_同步")

#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgvs = None, regParams = None):
	'''
	深渊炼狱_开启活动_本服
	'''
	#开服天数不足
	if not Environment.IsCross and WorldData.GetWorldKaiFuDay() < DeepHellDefine.DeepHell_NeedKaiFuDay:
		return
	
	global IS_START, ACTIVEID
	if IS_START:
		print "GE_EXC,repeat open DeepHellMgr"
		return
	
	IS_START = True
	ACTIVEID = regParams
	
	cNetMessage.PackPyMsg(DeepHell_ActiveState_S, (IS_START, IS_INIT, ACTIVEID))
	cRoleMgr.BroadMsg()	


def CloseActive(callArgvs = None, regParams = None):
	'''
	深渊炼狱_结束活动_本服
	'''
	global IS_START, IS_INIT, ACTIVEID
	if not IS_START:
		print "GE_EXC,repeat close DeepHellMgr"
		return
	
	IS_START = False
	IS_INIT = False
	ACTIVEID = regParams
	
	cNetMessage.PackPyMsg(DeepHell_ActiveState_S, (IS_START, IS_INIT, ACTIVEID))
	cRoleMgr.BroadMsg()	


def InitActive(callArgvs = None, regParams = None):
	'''
	深渊炼狱_启动_本服
	'''
	global IS_START, ACTIVEID, IS_INIT
	if not IS_START:
		print "GE_EXC,can not InitActive while IS_START is False"
		return
	
	if ACTIVEID != regParams:
		print "GE_EXC, can not InitActive while ACTIVEID(%s) != regParams(%s)" % (ACTIVEID, regParams)
		return 
	
	if IS_INIT:
		print "GE_EXC,DeepHell::InitActive,repeat init active"
		return
	
	
	#根据区服ID分流先后进入 并同步广播提示
	waitMin = cProcess.ProcessID % 8 + 1 
	cRoleMgr.Msg(1, 0, GlobalPrompt.DeepHell_Msg_ManyMinBefore % waitMin)
	
	global CANIN_TIMESTAMP
	CANIN_TIMESTAMP = cDateTime.Seconds() + waitMin * 60
	cNetMessage.PackPyMsg(DeepHell_CanInTimeStamp_S, CANIN_TIMESTAMP)
	cRoleMgr.BroadMsg()
	#tick可进入
	cComplexServer.RegTick(waitMin * 60, RealInitActive)
	#注册活动真正结束tick
	cComplexServer.RegTick(DeepHellDefine.DeepHell_ActiveSeconds, EndDeepHell)

	
#===============================================================================
# 客户端请求
#===============================================================================
def OnOpenPanel(role, msg = None):
	'''
	深渊炼狱_请求打开面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < DeepHellDefine.DeepHell_NeedLevel:
		return
	

def OnEnterDeepHell(role, msg = None):
	'''
	深渊炼狱_请求进入战场
	'''
	if not IS_START:
		return
	
	if not IS_INIT:
		return
	
	if role.GetLevel() < DeepHellDefine.DeepHell_NeedLevel:
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_DeepHell):
		return
	
	#传送到一个过渡场景
	role.GotoCrossServer(None, DeepHellDefine.DeepHell_TempSceneId, DeepHellDefine.DeepHell_TempPos_X, DeepHellDefine.DeepHell_TempPos_Y, DeepHellScene.AfterRevive, ZoneName.ZoneName)


#===============================================================================
# 辅助
#===============================================================================
def RealInitActive(callArgvs = None, regParams = None):
	'''
	启动活动
	'''
	global IS_INIT
	IS_INIT = True
	
	#开启提示
	cRoleMgr.Msg(1, 0, GlobalPrompt.DeepHell_Msg_RealActive)
	#同步活动状态
	cNetMessage.PackPyMsg(DeepHell_ActiveState_S, (IS_START, IS_INIT, ACTIVEID))
	cRoleMgr.BroadMsg()


def EndDeepHell(callArgvs = None, regParams = None):
	'''
	深渊炼狱 结束
	'''
	global IS_INIT, CANIN_TIMESTAMP
	IS_INIT = False
	CANIN_TIMESTAMP = 0
	
	
	cNetMessage.PackPyMsg(DeepHell_ActiveState_S, (IS_START, IS_INIT, ACTIVEID))
	cRoleMgr.BroadMsg()

	cNetMessage.PackPyMsg(DeepHell_CanInTimeStamp_S, CANIN_TIMESTAMP)
	cRoleMgr.BroadMsg()
	

#===============================================================================
# 事件
#===============================================================================
def OnSyncRoleOtherData(role, param = None):
	'''
	角色上限同步活动状态
	'''
	if IS_START:
		role.SendObj(DeepHell_ActiveState_S, (IS_START, IS_INIT, ACTIVEID))
	
	role.SendObj(DeepHell_CanInTimeStamp_S, CANIN_TIMESTAMP)
		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DeepHell_OnOpenPanel", "深渊炼狱_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DeepHell_OnEnterDeepHell", "深渊炼狱_请求进入战场"), OnEnterDeepHell)