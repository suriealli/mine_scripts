#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionConsume")
#===============================================================================
# 激情活动 -- 消费返利
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Game.Role import Event
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Game.Activity.PassionAct import PassionConsumeConfig, PassionDefine
from Game.Role.Data import EnumObj, EnumInt32
from Common.Other import GlobalPrompt, EnumGameConfig


if "_HasLoad" not in dir():
	IsStart = False
	
	PassionConsumeData = AutoMessage.AllotMessage("PassionConsumeData", "激情活动消费返利数据")
	
	PassionConsumeReward_Log = AutoLog.AutoTransaction("PassionConsumeReward_Log", "激情活动消费返利领取奖励日志")
	
def RequestConsumeReward(role, msg):
	'''
	请求消费返利奖励
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	
	callBackId, index = msg
	
	level = GetCloseValue(role.GetLevel(), PassionConsumeConfig.PassionConsumeLevel_List)
	if not level:
		return
	
	cfg = PassionConsumeConfig.PassionConsume_Dict.get((index, level))
	if not cfg:
		return
	
	if role.GetI32(EnumInt32.DayConsumeUnbindRMB_Q) < cfg.needConsumeRMB:
		return
	
	if PassionDefine.PassionConsume not in role.GetObj(EnumObj.PassionActData):
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionConsume] = consumeSet = set()
	else:
		consumeSet = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionConsume)
	
	if index in consumeSet:
		return
	
	with PassionConsumeReward_Log:
		consumeSet.add(index)
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionConsume] = consumeSet
		
		tips = GlobalPrompt.Reward_Tips
		for item in cfg.rewardItems:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	role.CallBackFunction(callBackId, (index, consumeSet))
	
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
	if param2 != CircularDefine.CA_PassionConsume:
		return
	if IsStart:
		print 'GE_EXC, PassionConsume is already start'
	IsStart = True

def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionConsume:
		return
	if not IsStart:
		print 'GE_EXC, PassionConsume is already end'
	IsStart = False
	
def SyncRoleOtherData(role, param):
	global IsStart
	if not IsStart: return
	
	role.SendObj(PassionConsumeData, role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionConsume, set()))
	
def RoleDayClear(role, param):
	global IsStart
	if not IsStart: return
	
	if PassionDefine.PassionConsume not in role.GetObj(EnumObj.PassionActData):
		return
	
	role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionConsume] = set()
	
	role.SendObj(PassionConsumeData, set())
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionConsume_Reward", "请求消费返利奖励"), RequestConsumeReward)
	
