#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OpenYear.OpenYearMgr")
#===============================================================================
# 开年连续登陆礼包
#===============================================================================
import datetime
import cRoleMgr
import cDateTime
import Environment
from Game.Role import Event
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumInt8, EnumDisperseInt32, EnumObj, EnumInt1
from Game.Activity.OpenYear import OpenYearConfig

if "_HasLoad" not in dir():
	StartTime = datetime.datetime(2015, 2, 25, 0, 0, 0)
	EndTime = datetime.datetime(2015, 3, 4, 0, 0, 0)

	#消息
	SyncTotalLoginGiftGotData = AutoMessage.AllotMessage("OpenYearSyncTotalLoginGiftGotData", "同步开年活动累计登录礼包领取情况")
	SyncContinueLoginGiftGotData = AutoMessage.AllotMessage("OpenYearSyncContinueLoginGiftGotData", "同步连开年活动续登录礼包领取情况")
	SyncConsumeGiftGotData = AutoMessage.AllotMessage("OpenYearSyncConsumeGiftGotData", "同步连开年活动消费礼包领取情况")
	#日志
	TraOpenYearGift = AutoLog.AutoTransaction("TraOpenYearGift", "开年礼包")
	TraOpenYearContinueLoginGift = AutoLog.AutoTransaction("TraOpenYearContinueLoginGift", "开年连续登陆礼包")
	TraOpenYearTotalLoginGift = AutoLog.AutoTransaction("TraOpenYearTotalLoginGift", "开年累计登陆礼包")
	TraOpenYearConsumGift = AutoLog.AutoTransaction("TraOpenYearConsumGift", "开年消费礼包")

def IsStart():
	now = cDateTime.Now()
	if StartTime <= now <= EndTime:
		return True
	return False


def AfterConsume(role, param):
	#消费充值神石
	oldValue, newValue = param
	if newValue > oldValue:
		return
	role.IncDI32(EnumDisperseInt32.DayConsumeRMB_Q, oldValue - newValue)


def AfterLogin(role, param):
	if IsStart() is False:
		return
	#增加活动期间累计登录天数
	nowDays = cDateTime.Days()
	lastLoginDays = role.GetDI32(EnumDisperseInt32.OpenYearLoginDays)
	if nowDays <= lastLoginDays:
		return
	
	role.IncI8(EnumInt8.OpenYearTotalLoginDay, 1)
	
	if nowDays - lastLoginDays > 1:
		role.SetI8(EnumInt8.OpenYearContinueLoginDay, 1)
		
	elif nowDays - lastLoginDays == 1:
		role.IncI8(EnumInt8.OpenYearContinueLoginDay, 1)
		
	role.SetDI32(EnumDisperseInt32.OpenYearLoginDays, nowDays)
	

def RoleDayClear(role, param):
	role.SetDI32(EnumDisperseInt32.DayConsumeRMB_Q, 0)
	gotData = role.GetObj(EnumObj.OpenYear)
	gotData[3] = set()
	gotSet3 = gotData.get(3, set())
	AfterLogin(role, param)
	role.SendObj(SyncConsumeGiftGotData, gotSet3)
	
	
def SyncRoleOtherData(role, param):
	'''
	同步角色其它数据
	'''	
	if not IsStart():
		return
	gotData = role.GetObj(EnumObj.OpenYear)
	gotSet1 = gotData.get(1, set())
	gotSet2 = gotData.get(2, set())
	gotSet3 = gotData.get(3, set())
	role.SendObj(SyncContinueLoginGiftGotData, gotSet1)
	role.SendObj(SyncTotalLoginGiftGotData, gotSet2)
	role.SendObj(SyncConsumeGiftGotData, gotSet3)
	

#===============================================================================
# 开年大礼包
#===============================================================================
def RequestOpenYearGift(role, msg):
	'''
	客户端请求获取开年礼包
	'''
	if not IsStart():
		return
	#已经领取过
	if role.GetI1(EnumInt1.OpenYearGift):
		return
	
	if role.GetLevel() < EnumGameConfig.OpenYearNeedLevel:
		return
	
	with TraOpenYearGift:
		role.SetI1(EnumInt1.OpenYearGift, 1)
		role.AddItem(EnumGameConfig.OpenYearGift, 1)
	
	role.Msg(2, 0, GlobalPrompt.Item_Tips % (EnumGameConfig.OpenYearGift, 1))
		

#===============================================================================
# 开年连续登录礼包
#===============================================================================
def RequestContinueLoginGift(role, msg):
	'''
	客户端请求获取开年连续登陆礼包
	'''
	if not IsStart():
		return
	
	if role.GetLevel() < EnumGameConfig.OpenYearNeedLevel:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.OpenYear).setdefault(1, set())
	#如果已经领取过
	if index in gotSet:
		return
	
	config = OpenYearConfig.ContinueLoginConfigDict.get(index)
	if config is None:
		return
	#连续登陆天数不符合条件
	if role.GetI8(EnumInt8.OpenYearContinueLoginDay) < config.Days:
		return
	
	tips = GlobalPrompt.Reward_Tips
	with TraOpenYearContinueLoginGift:
		gotSet.add(index)
		if config.Items:
			for item in config.Items:
				if item[1] > 0:
					role.AddItem(*item)
					tips += GlobalPrompt.Item_Tips % item
		if config.Money:
			role.IncMoney(config.Money)
			tips += GlobalPrompt.Money_Tips % config.Money
		if config.BindRMB:
			role.IncBindRMB(config.BindRMB)
			tips += GlobalPrompt.BindRMB_Tips % config.BindRMB
		
	role.SendObj(SyncContinueLoginGiftGotData, gotSet)
	role.Msg(2, 0, tips)

#===============================================================================
# 开年累计登录礼包
#===============================================================================
def RequestTotalLoginGift(role, msg):
	'''
	客户端请求获取开年累计登陆礼包
	'''
	if not IsStart():
		return
	
	if role.GetLevel() < EnumGameConfig.OpenYearNeedLevel:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.OpenYear).setdefault(2, set())
	#如果已经领取过
	if index in gotSet:
		return
	
	config = OpenYearConfig.TotalLoginConfigDict.get(index)
	if config is None:
		return
	#连续登陆天数不符合条件
	if role.GetI8(EnumInt8.OpenYearTotalLoginDay) < config.Days:
		return
	
	tips = GlobalPrompt.Reward_Tips
	with TraOpenYearTotalLoginGift:
		gotSet.add(index)
		if config.Items:
			for item in config.Items:
				if item[1] > 0:
					role.AddItem(*item)
					tips += GlobalPrompt.Item_Tips % item
		if config.Money:
			role.IncMoney(config.Money)
			tips += GlobalPrompt.Money_Tips % config.Money
		if config.BindRMB:
			role.IncBindRMB(config.BindRMB)
			tips += GlobalPrompt.BindRMB_Tips % config.BindRMB
		
	role.SendObj(SyncTotalLoginGiftGotData, gotSet)
	role.Msg(2, 0, tips)

#===============================================================================
# 开年消费礼包
#===============================================================================
def RequestConsumGift(role, msg):
	'''
	客户端请求获取开年消费礼包
	'''
	if not IsStart():
		return
	if role.GetLevel() < EnumGameConfig.OpenYearNeedLevel:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.OpenYear).setdefault(3, set())
	#如果已经领取过
	if index in gotSet:
		return
	
	config = OpenYearConfig.ConsumeConfigDict.get(index)
	if config is None:
		return
	#连续登陆天数不符合条件
	if role.GetDI32(EnumDisperseInt32.DayConsumeRMB_Q) < config.Consume:
		return
	
	tips = GlobalPrompt.Reward_Tips
	with TraOpenYearConsumGift:
		gotSet.add(index)
		if config.Items:
			for item in config.Items:
				if item[1] > 0:
					role.AddItem(*item)
					tips += GlobalPrompt.Item_Tips % item
		if config.Money:
			role.IncMoney(config.Money)
			tips += GlobalPrompt.Money_Tips % config.Money
		if config.BindRMB:
			role.IncBindRMB(config.BindRMB)
			tips += GlobalPrompt.BindRMB_Tips % config.BindRMB
		
	role.SendObj(SyncConsumeGiftGotData, gotSet)
	role.Msg(2, 0, tips)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		if not Environment.IsCross:
			Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterConsume)
			Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
			Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenYearGift", "客户端请求获取开年礼包"), RequestOpenYearGift)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenYearTotalLoginGift", "客户端请求获取开年累积登录礼包"), RequestTotalLoginGift)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenYearContinueLoginGift", "客户端请求获取开年连续登录礼包"), RequestContinueLoginGift)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenYearConsumGift", "客户端请求获取开年消费礼包"), RequestConsumGift)
