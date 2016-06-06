#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveOneDay.FiveOneCostReward")
#===============================================================================
# 五一消费送惊喜
#===============================================================================
import Environment
import cRoleMgr
from Game.Role import Event
from Game.Activity import CircularDefine
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumObj
from Game.Activity.FiveOneDay import FiveOneDayConfig

if "_HasLoad" not in dir():
	IS_START = False	#活动开启标志
	
	FiveOneCostReward_Sync_reward = AutoMessage.AllotMessage("FiveOneCostReward_Sync_reward", "同步已领取的五一消费送惊喜奖励ID")
	#日志
	FiveOneCostReward = AutoLog.AutoTransaction("FiveOneCostReward", "五一消费送惊喜")
	
#=======活动开关==========
def StartCostReward(*param):
	#开启五一消费送惊喜
	_, circularType = param
	if circularType != CircularDefine.CA_FiveOneCost:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open FiveOneCostReward Act"
		return
	
	IS_START = True
	
def CloseCostReward(*param):
	#关闭五一消费送惊喜
	_, circularType = param
	if circularType != CircularDefine.CA_FiveOneCost:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC, FiveOneCostReward is already close"
		return
	
	IS_START = False
	
def RequestGetCostReward(role, param):
	'''
	客户端请求领取五一消费
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	if role.GetLevel() < EnumGameConfig.FIVE_ONE_NEED_LEVEL:
		return
	
	index = param
	GetList = role.GetObj(EnumObj.FiveOneDayObj).get(1, set())
	if index in GetList:
		return
	
	cfg = FiveOneDayConfig.FIVEONE_COST_REWARD.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in RequestGetCostReward" % index
		return
	
	totalCost = role.GetDayConsumeUnbindRMB()
	if totalCost < cfg.costRMB:
		return
	
	with FiveOneCostReward:
		GetList.add(index)
		tips = ""
		if cfg.itemReward:
			for coding, cnt in cfg.itemReward:
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
		role.Msg(2, 0, tips)
		role.SendObj(FiveOneCostReward_Sync_reward, GetList)
#===================================================
def AfterLogin(role, param):
	FiveOneDayObj = role.GetObj(EnumObj.FiveOneDayObj)
	if 1 not in FiveOneDayObj:
		FiveOneDayObj[1] = set()
	if 2 not in FiveOneDayObj:
		FiveOneDayObj[2] = -1
	if 3 not in FiveOneDayObj:
		FiveOneDayObj[3] = {}
	if 4 not in FiveOneDayObj:
		FiveOneDayObj[4] = {}
		
def RoleDayClear(role, param):
	if not IS_START:
		return
	FiveOneDayObj = role.GetObj(EnumObj.FiveOneDayObj)
	FiveOneDayObj[1] = set()
	role.SendObj(FiveOneCostReward_Sync_reward, FiveOneDayObj[1])
	
def SyncRoleOtherData(role, param):
	if not IS_START:
		return
	role.SendObj(FiveOneCostReward_Sync_reward, role.GetObj(EnumObj.FiveOneDayObj).get(1, set()))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCostReward)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseCostReward)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FiveOne_Get_CostReward", "客户端请求领取五一消费"), RequestGetCostReward)