#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionRecharge")
#===============================================================================
# 激情活动 -- 充值返利
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.PassionAct import PassionRechargeConfig, PassionDefine
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj
from Common.Other import GlobalPrompt, EnumGameConfig



if "_HasLoad" not in dir():
	IsStart = False
	
	PassionRechargeData = AutoMessage.AllotMessage("PassionRechargeData", "激情活动充值返利数据")
	
	PassionRechargeReward_Log = AutoLog.AutoTransaction("PassionRechargeReward_Log", "激情活动充值返利领取奖励日志")
	
def RequestRechargeReward(role, msg):
	'''
	请求充值返利奖励
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	
	callBackId, index = msg
	
	level = GetCloseValue(role.GetLevel(), PassionRechargeConfig.PassionRechargeLevel_List)
	if not level:
		return
	
	cfg = PassionRechargeConfig.PassionRecharge_Dict.get((index, level))
	if not cfg:
		return
	
	if role.GetDayBuyUnbindRMB_Q() < cfg.needRechargeRMB:
		return
	
	if PassionDefine.PassionRecharge not in role.GetObj(EnumObj.PassionActData):
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionRecharge] = rechargeSet = set()
	else:
		rechargeSet = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionRecharge)
	
	if index in rechargeSet:
		return
	
	with PassionRechargeReward_Log:
		rechargeSet.add(index)
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionRecharge] = rechargeSet
		
		tips = GlobalPrompt.Reward_Tips
		for item in cfg.rewardItems:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	role.CallBackFunction(callBackId, (index, rechargeSet))
	
	role.Msg(2, 0, tips)
	
def GetCloseValue(value, valueList):
	tmp_level = 0
	for i in valueList:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		return tmp_level
	
def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionRecharge:
		return
	if IsStart:
		print 'GE_EXC, PassionRecharge is already start'
	IsStart = True

def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionRecharge:
		return
	if not IsStart:
		print 'GE_EXC, PassionRecharge is already end'
	IsStart = False

def SyncRoleOtherData(role, param):
	global IsStart
	if not IsStart: return
	
	role.SendObj(PassionRechargeData, role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionRecharge, set()))
	
def RoleDayClear(role, param):
	global IsStart
	if not IsStart: return
	
	if PassionDefine.PassionRecharge not in role.GetObj(EnumObj.PassionActData):
		return
	
	role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionRecharge] = set()
	
	role.SendObj(PassionRechargeData, set())
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionRecharge_Reward", "请求充值返利奖励"), RequestRechargeReward)
	
	
