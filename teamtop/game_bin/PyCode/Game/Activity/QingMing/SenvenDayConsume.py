#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.SenvenDayConsume")
#===============================================================================
# 七日消费活动
#===============================================================================
import cDateTime
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt32
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity import CircularDefine
from Game.Activity.QingMing import QingMingConfig

if "_HasLoad" not in dir():
	IsStart = False
	
	TraQingMingSevenDayConsumeReward = AutoLog.AutoTransaction("TraQingMingSevenDayConsumeReward", "清明节七日消费奖励")
	
	#消息
	SyncQingMingSevenDayConsumeData = AutoMessage.AllotMessage("SyncQingMingSevenDayConsumeData", "同步客户端清明节活动七日消费活动消费数据")
	SyncQingMingSevenDayConsumeRewardData = AutoMessage.AllotMessage("SyncQingMingSevenDayConsumeRewardData", "同步客户端清明节活动七日消费活动领奖情况")

def Start(*param):
	'''
	活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingSevenDayConsume != circularType:
		return
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open QingMingSevenDayConsume"
		return
		
	IsStart = True
	

def End(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingSevenDayConsume != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end QingMingSevenDayConsume while not start"
		return
		
	IsStart = False


def RequestGetReward(role, msg):
	'''
	客户端请求获取七日充值奖励
	 @param role:
	 @param msg: (year, month, day)
	'''
	if IsStart is False:
		return	
	
	if role.GetLevel() < EnumGameConfig.QingMingConsumeNeedLevel:
		return
	
	key = msg
	
	gotSet = role.GetObj(EnumObj.QingMingData).setdefault(6, set())
	if key in gotSet:
		return
	
	consumeDict = role.GetObj(EnumObj.QingMingData).get(4, {})
	
	consume = consumeDict.get(key)
	if consume is None:
		return
	
	roleLevel = role.GetLevel()
	levelrangeID = QingMingConfig.SenvenDayConsumeLevelRangeDict.get(roleLevel)
	
	config = QingMingConfig.SenvenDayConsumeConfigDict.get((key, levelrangeID))
	if config is None:
		return
	
	if consume < config.needConsumeUnbindRMB:
		return
	
	tips = GlobalPrompt.Reward_Tips
	with TraQingMingSevenDayConsumeReward:
		gotSet.add(key)
		for item in config.items:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	role.SendObj(SyncQingMingSevenDayConsumeRewardData, gotSet)
	role.Msg(2, 0, tips)


def OnAfterDayConsumeUnbindRMB(role, param):
	'''
	监听神石变化
	'''
	if IsStart is False:
		return
	
	_, newValue = param
	day = cDateTime.Day()
	month = cDateTime.Month()
	year = cDateTime.Year()
	key = (year, month, day)
	
	consumeDict = role.GetObj(EnumObj.QingMingData).setdefault(4, {})
	consumeDict[key] = newValue
	
	role.SendObj(SyncQingMingSevenDayConsumeData, consumeDict)


def SyncRoleOtherData(role, param):
	if IsStart is False:
		return
	gotSet = role.GetObj(EnumObj.QingMingData).get(6, set())
	consumeDict = role.GetObj(EnumObj.QingMingData).get(4, {})
	role.SendObj(SyncQingMingSevenDayConsumeRewardData, gotSet)
	role.SendObj(SyncQingMingSevenDayConsumeData, consumeDict)


def AfterRoleLogin(role, param):
	if IsStart is False:
		return
	
	day = cDateTime.Day()
	month = cDateTime.Month()
	year = cDateTime.Year()
	key = (year, month, day)
	
	consumeDict = role.GetObj(EnumObj.QingMingData).setdefault(4, {})
	consumeDict[key] = role.GetI32(EnumInt32.DayConsumeUnbindRMB)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetQingMingSevenDayConsumeReward", "客户端请求获取清明节七日消费奖励"), RequestGetReward)
		Event.RegEvent(Event.Eve_AfterChangeDayConsumeUnbindRMB, OnAfterDayConsumeUnbindRMB)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLogin, AfterRoleLogin)
		
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
