#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.SevenDayRecharge")
#===============================================================================
# 七日充值活动
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt32
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Game.Activity.QingMing import QingMingConfig

if "_HasLoad" not in dir():
	IsStart = False
	
	TraQingMingSevenDayRechargeReward = AutoLog.AutoTransaction("TraQingMingSevenDayRechargeReward", "清明节七日充值奖励")

	#消息
	SyncQingMingSevenDayRechargeRewardData = AutoMessage.AllotMessage("SyncQingMingSevenDayRechargeRewardData", "同步客户端清明节活动七日充值活动领奖情况")
	SyncQingMingSevenDayRechargeData = AutoMessage.AllotMessage("SyncQingMingSevenDayRechargeData", "同步客户端清明节活动七日充值充值情况 ")


def Start(*param):
	'''
	活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingSevenDayRecharge != circularType:
		return
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open QingMingSevenDayRecharge"
		return
		
	IsStart = True
	

def End(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingSevenDayRecharge != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end QingMingSevenDayRecharge while not start"
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
	
	if role.GetLevel() < EnumGameConfig.QingMingRechargeNeedLevel:
		return
	
	key = msg
	
	gotSet = role.GetObj(EnumObj.QingMingData).setdefault(5, set())
	if key in gotSet:
		return
	
	rechargeDict = role.GetObj(EnumObj.QingMingData).get(3, {})
	recharge = rechargeDict.get(key)
	if recharge is None:
		return
	
	roleLevel = role.GetLevel()
	levelrangeID = QingMingConfig.SenvenDayRechargeLevelRangeDict.get(roleLevel)
	
	if levelrangeID is None:
		return
	
	config = QingMingConfig.SenvenDayRechargeConfigDict.get((key, levelrangeID))
	if config is None:
		return
	
	if recharge < config.needDayBuyUnbindRMB_Q:
		return
	
	tips = GlobalPrompt.Reward_Tips
	with TraQingMingSevenDayRechargeReward:
		gotSet.add(key)
		for item in config.items:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	role.SendObj(SyncQingMingSevenDayRechargeRewardData, gotSet)
	role.Msg(2, 0, tips)


def OnChangeDayBuyUnbindRMB_Q(role, param):
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
	
	rechargeDict = role.GetObj(EnumObj.QingMingData).setdefault(3, {})
	rechargeDict[key] = newValue
	
	role.SendObj(SyncQingMingSevenDayRechargeData, rechargeDict)


def SyncRoleOtherData(role, param):
	if IsStart is False:
		return
	gotSet = role.GetObj(EnumObj.QingMingData).get(5, set())
	rechargeDict = role.GetObj(EnumObj.QingMingData).get(3, {})
	role.SendObj(SyncQingMingSevenDayRechargeRewardData, gotSet)
	role.SendObj(SyncQingMingSevenDayRechargeData, rechargeDict)


def AfterRoleLogin(role, param):
	if IsStart is False:
		return
	
	day = cDateTime.Day()
	month = cDateTime.Month()
	year = cDateTime.Year()
	key = (year, month, day)
	
	rechargeDict = role.GetObj(EnumObj.QingMingData).setdefault(3, {})
	rechargeDict[key] = role.GetI32(EnumInt32.DayBuyUnbindRMB_Q)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetQingMingSevenDayRechargeReward", "客户端请求获取清明节七日充值奖励"), RequestGetReward)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, OnChangeDayBuyUnbindRMB_Q)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLogin, AfterRoleLogin)

		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
