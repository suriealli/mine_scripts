#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RechargeEveryday.RechargeEveryday")
#===============================================================================
# 今日首充
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
import cComplexServer
from Game.Role import Event
from Game.Role.Mail import Mail
from Game.Persistence import Contain
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from Game.Role.Data import EnumInt8, EnumInt16
from Game.Activity.RechargeEveryday import RechargeEverydayConfig

if "_HasLoad" not in dir():
	RecgaregeValue = 100
	#消息
	SyncRechargeEverydayRewardStatu = AutoMessage.AllotMessage("SyncRechargeEverydayRewardStatu", "同步今日首充奖励领取状态")
	#日志
	TraRechargeEverydayAward = AutoLog.AutoTransaction("TraRechargeEverydayAward", "每日首充奖励")


def AfterChangeUnbindRMB_Q(role, param):
	'''
	充值神石改变后触发
	'''
	#五日首充尚未完成
	enums = [EnumInt8.DayFirstPayReward1, EnumInt8.DayFirstPayReward2,
	EnumInt8.DayFirstPayReward3, EnumInt8.DayFirstPayReward4,
	EnumInt8.DayFirstPayReward5]
	
	for theEnum in enums:
		if role.GetI8(theEnum) != 2:
			return
	
	#必须要五日首充完成第二天及以后才能开启今日首充
	nowDays = cDateTime.Days()
	theDays = role.GetI16(EnumInt16.DayFirstPayIconShowTime)
	if nowDays - theDays < 1:
		return
	
	oldValue, newValue = param
	chargeValue = newValue - oldValue
	#充值不达标
	if chargeValue < RecgaregeValue:
		return
	
	roleID = role.GetRoleID()
	roleLevel = role.GetLevel()
	global RechargeEverydayRoleDict
	if roleID in RechargeEverydayRoleDict:
		return
	
	RechargeEverydayRoleDict[roleID] = [roleLevel, False]
	
	role.SendObj(SyncRechargeEverydayRewardStatu, (True, False))


def CallBeforeNewDay():
	'''
	跨天前发奖
	'''
	global RechargeEverydayRoleDict
	roleDict = dict(RechargeEverydayRoleDict.data)
	RechargeEverydayRoleDict.clear()
	
	RRG = RechargeEverydayConfig.RechargeEverydayConfigDict.get
	MSM = Mail.SendMail
	with TraRechargeEverydayAward:
		for roleID, (roleLevel, hasReawrd) in roleDict.iteritems():
			if hasReawrd is True:
				continue
			config = RRG(roleLevel)
			if config is None:
				continue
			MSM(roleID,
				GlobalPrompt.RechargeEverydayTitle,
				GlobalPrompt.RechargeEverydaySender,
				GlobalPrompt.RechargeEverydayContent,
				items=config.items)


def RequestGetReward(role, msg):
	'''
	客户端请求领奖
	'''
	roleID = role.GetRoleID()
	
	global RechargeEverydayRoleDict
	if roleID not in RechargeEverydayRoleDict:
		return
	
	_, hasReward = RechargeEverydayRoleDict[roleID]
	if hasReward is True:
		return
	
	roleLevel = role.GetLevel()
	config = RechargeEverydayConfig.RechargeEverydayConfigDict.get(roleLevel)
	if config is None:
		print "GE_EXC,error while config = RechargeEverydayConfig.RechargeEverydayConfigDict.get(%s)" % roleLevel
		return
	
	with TraRechargeEverydayAward:
		RechargeEverydayRoleDict[roleID][1] = True
		
		for item in config.items:
			role.AddItem(*item)
	
	role.SendObj(SyncRechargeEverydayRewardStatu, (True, True))
	cRoleMgr.Msg(1, 0, GlobalPrompt.RechargeEverydayGlobalTell % role.GetRoleName())


def SyncRoleOtherData(role, param):
	'''
	同步角色其它数据
	'''
	roleID = role.GetRoleID()
	data = RechargeEverydayRoleDict.get(roleID, None)
	if data is None:
		canReward = False
		hasReward = False
	else:
		canReward = True
		hasReward = data[1]
		
	role.SendObj(SyncRechargeEverydayRewardStatu, (canReward, hasReward))

def RoleDayClear(role, param):
	SyncRoleOtherData(role, param)

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#roleID --> [roleLevel,hasReward]
		RechargeEverydayRoleDict = Contain.Dict("RechargeEverydayRoleDict", (2038, 1, 1), None, None)
	
	if Environment.HasLogic and not Environment.IsCross and (not Environment.EnvIsPL()):
		#波兰屏蔽今日首充
		cComplexServer.RegBeforeNewDayCallFunction(CallBeforeNewDay)
		
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetReward_RechargeEveryday", "客户端请求今日充值领奖"), RequestGetReward)
	
	
