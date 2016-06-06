#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.CouplesGoalMgr")
#===============================================================================
# 情人目标 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumDayInt8
from Game.Activity import CircularDefine
from Game.Activity.ValentineDay import CouplesGoalConfig

IDX_TARGET = 5
V_COMPLETED = 1
V_REWARDED = 0
if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_CouplesGoal_GoalReward = AutoLog.AutoTransaction("Tra_CouplesGoal_GoalReward", "情人目标_目标奖励")
	
	CouplesGoal_GoalData_S = AutoMessage.AllotMessage("CouplesGoal_GoalData_S", "情人目标_同步目标完成及领奖记录数据")

#### 活动控制  start ####
def OnStartCouplesGoal(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_CouplesGoal != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open CouplesGoal"
		return
		
	IS_START = True

def OnEndCouplesGoal(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_CouplesGoal != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end CouplesGoal while not start"
		return
		
	IS_START = False

#### 客户端请求start
def OnGetGoalReward(role, msg):
	'''
	情人目标_请求领取目标奖励
	@param msg: goalId 
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.CouplesGoal_NeedLevel:
		return
	
	goalId = msg
	goalCfg = CouplesGoalConfig.CouplesGoal_GoalID2Cfg_Dict.get(goalId)
	if not goalCfg:
		return
	
	#对应目标不是完成可领取奖励状态
	couplesGoalData = role.GetObj(EnumObj.ValentineDayData)[IDX_TARGET]
	if not (goalId in couplesGoalData and couplesGoalData[goalId] == V_COMPLETED):
		return
	
	prompt = GlobalPrompt.CouplesGoal_Tips_Head
	with Tra_CouplesGoal_GoalReward:
		#写领奖记录
		couplesGoalData[goalId] = V_REWARDED
		role.GetObj(EnumObj.ValentineDayData)[IDX_TARGET] = couplesGoalData
		#奖励物品
		for coding, cnt in goalCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.CouplesGoal_Tips_Item % (coding, cnt)
	
	#更新同步客户端
	role.SendObj(CouplesGoal_GoalData_S, couplesGoalData)
	#奖励提示
	role.Msg(2, 0, prompt)

#### 事件 start
def OnRoleInit(role, param):
	'''
	初始角色相关Obj的key
	'''
	valentineDayData = role.GetObj(EnumObj.ValentineDayData)
	if IDX_TARGET not in valentineDayData:
		valentineDayData[IDX_TARGET] = {}

def OnSyncRoleOtherData(role, param):
	'''
	上线同步数据
	'''
	if not IS_START:
		return
	
	#更新前已经佩戴了订婚戒指 直接完成情人目标
	if len(role.GetObj(EnumObj.En_RoleRing)):
		OnTryCouplesGoal(role,(EnumGameConfig.GoalType_EngageRing, 1))
	
	#更新前已完成今日派对 直接完成情人目标
	if 3 == role.GetDI8(EnumDayInt8.PartyStatus):
		OnTryCouplesGoal(role,(EnumGameConfig.GoalType_QinmiParty, 1))
	
	#同步目标奖励领取记录
	couplesGoalData = role.GetObj(EnumObj.ValentineDayData)[IDX_TARGET]
	role.SendObj(CouplesGoal_GoalData_S, couplesGoalData)

def OnTryCouplesGoal(role, param):
	'''
	情人目标项动作触发对应目标逻辑处理是否完成目标
	'''
	if not IS_START:
		return
	
	goalType, curValue = param
#	print "GE_EXC,OnTryCouplesGoal::goalType(%s), curValue(%s)" % (goalType, curValue)
	goalTypeCfgDict = CouplesGoalConfig.CouplesGoal_GoalConfig_Dict.get(goalType)
	if not goalTypeCfgDict:
		return
	
	hasChange = False
	couplesGoalData = role.GetObj(EnumObj.ValentineDayData)[IDX_TARGET]
	for goalId, goalCfg in goalTypeCfgDict.iteritems():
		if goalId in couplesGoalData:
			continue
		elif curValue < goalCfg.needValue:
			continue
		else:
			hasChange = True
			couplesGoalData[goalId] = V_COMPLETED
	
	#有更新 同步客户端
	if hasChange:
		role.GetObj(EnumObj.ValentineDayData)[IDX_TARGET] = couplesGoalData
		role.SendObj(CouplesGoal_GoalData_S, couplesGoalData)
#		print "GE_EXC, OnTryCouplesGoal::couplesGoalData(%s)" %couplesGoalData

def OnRoleDayClear(role, param):
	'''
	每日清理 根据配置目标是否需要清理来清理角色数据
	'''
	if not IS_START:
		return
	
	hasChange = False
	couplesGoalData = role.GetObj(EnumObj.ValentineDayData)[IDX_TARGET]
	for _, goalTypeCfgDict in CouplesGoalConfig.CouplesGoal_GoalConfig_Dict.iteritems():
		for goalId, goalCfg in goalTypeCfgDict.iteritems():
			if goalCfg.needDayClear and goalId in couplesGoalData:
				hasChange = True
				del couplesGoalData[goalId]
	
	#有更新 同步客户端
	if hasChange:
		role.GetObj(EnumObj.ValentineDayData)[IDX_TARGET] = couplesGoalData
		role.SendObj(CouplesGoal_GoalData_S, couplesGoalData)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartCouplesGoal)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndCouplesGoal)
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_TryCouplesGoal, OnTryCouplesGoal)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesGoal_OnGetGoalReward", "情人目标_请求领取目标奖励"), OnGetGoalReward)