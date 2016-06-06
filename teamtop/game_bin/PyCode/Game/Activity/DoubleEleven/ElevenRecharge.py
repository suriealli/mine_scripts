#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.ElevenRecharge")
#===============================================================================
# 双十一活动 -- 充值返利
#===============================================================================
import Environment
import cRoleMgr
from Common.Other import EnumGameConfig
from Common.Message import AutoMessage
from Game.Role import Event
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj
from Common.Other import GlobalPrompt
from Game.Activity.DoubleEleven import ElevenRechargeConfig, ElevenActivityDefine


if "_HasLoad" not in dir():
	IsStart = False
	
	ElevenRechargeRMBData = AutoMessage.AllotMessage("ElevenRechargeRMBData", "双十一充值累计充值神石数据")
	ElevenRechargeData = AutoMessage.AllotMessage("ElevenRechargeData", "双十一充值大放返利数据")
	ElevenRechargeRewardLog = AutoLog.AutoTransaction("ElevenRechargeRewardLog", "双十一充值大放送领奖")
	
def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_ElevenRecharge:
		return
	if IsStart:
		print 'GE_EXC, ElevenRecharge is already start'
	IsStart = True

def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_ElevenRecharge:
		return
	if not IsStart:
		print 'GE_EXC, ElevenRecharge is already end'
	IsStart = False	
	
def ElevenRechargeReward(role, msg):
	'''
	请求充值返利奖励
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	callBackId, index = msg
	
	if EnumGameConfig.ElevenRecharge_NeedLevel > role.GetLevel():
		return
	
	cfg = ElevenRechargeConfig.ElevenRechargeDict.get(index)
	if not cfg:
		return
	
	if role.GetObj(EnumObj.ElevenActData).get(ElevenActivityDefine.ElevenRechargeALLRMB, 0) < cfg.needRechargeRMB:
		return
	
	rechargeSet = role.GetObj(EnumObj.ElevenActData).get(ElevenActivityDefine.ElevenRecharge, set())
	
	if index in rechargeSet:
		return
	
	with ElevenRechargeRewardLog:
		rechargeSet.add(index)
		role.GetObj(EnumObj.ElevenActData)[ElevenActivityDefine.ElevenRecharge] = rechargeSet
		
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
	
def SyncRoleOtherData(role, param):
	global IsStart
	if not IsStart: return
	
	if EnumGameConfig.ElevenRecharge_NeedLevel > role.GetLevel():
		return
	
	role.SendObj(ElevenRechargeData, role.GetObj(EnumObj.ElevenActData).get(ElevenActivityDefine.ElevenRecharge, set()))
	role.SendObj(ElevenRechargeRMBData, role.GetObj(EnumObj.ElevenActData).get(ElevenActivityDefine.ElevenRechargeALLRMB, 0))
	
def AfterChangeUnbindRMB_Q(role, param=None):
	'''
	@param role:
	@param param: None 
	'''
	global IsStart
	if not IsStart: return
	oldValue, newValue = param
	if oldValue > newValue:
		return
	newCharge = newValue - oldValue
	
	ElevenDict = role.GetObj(EnumObj.ElevenActData)
	
	ElevenDict[ElevenActivityDefine.ElevenRechargeALLRMB] = ElevenDict.get(ElevenActivityDefine.ElevenRechargeALLRMB, 0) + newCharge
	
	#同步双十一充值个人数据
	
	role.SendObj(ElevenRechargeRMBData, ElevenDict.get(ElevenActivityDefine.ElevenRechargeALLRMB, 0))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElevenRechargeReward", "双十一充值大放送请求充值奖励"), ElevenRechargeReward)
	
