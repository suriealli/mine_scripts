#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveGift.DayFirstPayMgr")
#===============================================================================
# 每日首充管理
#===============================================================================
import cDateTime
import cRoleMgr
import Environment
from Util import Time
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumSysData
from ComplexServer.Log import AutoLog
from Game.Activity.FiveGift import FiveGiftConfig, FiveGiftDefine
from Game.Role import Event
from Game.Role.Data import EnumDayInt1, EnumInt8, EnumInt16
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	DAY_FIRST_PAY_DAYS_MAX = 5		#每日首充最大天数

def GetDayFirstPayReward(role):
	fpDays = role.GetI8(EnumInt8.DayFirstPayDays)
	
	rewardConfig = FiveGiftConfig.DAY_FIRST_PAY_REWARD.get(fpDays)
	if not rewardConfig:
		return
	
	rewardEnum = FiveGiftDefine.DAY_TO_FIRST_PAY_REWARD_ENUM.get(fpDays)
	if not rewardEnum:
		return
	
	#是否可以领取奖励
	if role.GetI8(rewardEnum) != 1:
		return
	
	#设置为已领取
	role.SetI8(rewardEnum, 2)
	
	#设定每日首充图标出现的时间(保存时间的第二天出现图标)
	role.SetI16(EnumInt16.DayFirstPayIconShowTime, cDateTime.Days())
	
	#如果领奖的时候还没完成今日首充，领取奖励默认完成了今日的首充，需要明天才可以继续每日首充
	if not role.GetDI1(EnumDayInt1.DayFirstPay):
		role.SetDI1(EnumDayInt1.DayFirstPay, 1)
	
	#是否合服(合服后奖励不同)
	rewardMoney = rewardConfig.rewardMoney
	rewardBindRMB = rewardConfig.rewardBindRMB
	rewardItem = rewardConfig.rewardItem
	if WorldData.IsHeFu():
		rewardMoney = rewardConfig.rewardMoney_hefu
		rewardBindRMB = rewardConfig.rewardBindRMB_hefu
		rewardItem = rewardConfig.rewardItem_hefu
	
	#奖励
	prompt = ""
	if rewardMoney:
		#金币奖励
		role.IncMoney(rewardMoney)
		#提示
		prompt = GlobalPrompt.Money_Tips % rewardMoney
	if rewardBindRMB:
		#魔晶奖励
		role.IncBindRMB(rewardBindRMB)
		#提示
		prompt += GlobalPrompt.BindRMB_Tips % rewardBindRMB
	
	for item in rewardItem:
		role.AddItem(*item)
		#提示字符串
		prompt += GlobalPrompt.Item_Tips % (item[0], item[1])
		
	#提示
	role.Msg(2, 0, prompt)
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.DAY_FP_REWARD_HEARSAY % role.GetRoleName())

#===============================================================================
# Event
#===============================================================================
def AfterEve_QPoint(role, param):
	'''
	消费Q点后调用
	@param role:
	@param param:
	'''
	#是否完成了首充五重礼
	for rewardEnum in FiveGiftDefine.GIFTID_TO_REWARD_ENUM.itervalues():
		#需要全部领取才算完成五重礼
		if role.GetI8(rewardEnum) != 2:
			return
	
	if role.GetDI1(EnumDayInt1.DayFirstPay) == 0:
		#今日完成了首充
		role.SetDI1(EnumDayInt1.DayFirstPay, 1)
		
		dayFirstPayDays = role.GetI8(EnumInt8.DayFirstPayDays)
		if dayFirstPayDays == DAY_FIRST_PAY_DAYS_MAX:
			#是否已经达到最大首充天数
			return
		elif dayFirstPayDays == 0:
			#是否未完成过每日首充
			role.IncI8(EnumInt8.DayFirstPayDays, 1)
			
			rewardEnum = FiveGiftDefine.DAY_TO_FIRST_PAY_REWARD_ENUM.get(1)
			if not rewardEnum:
				return
			if role.GetI8(rewardEnum) != 0:
				return
			#设置每日首充奖励可领取
			role.SetI8(rewardEnum, 1)
		else:
			rewardEnum = FiveGiftDefine.DAY_TO_FIRST_PAY_REWARD_ENUM.get(dayFirstPayDays)
			if not rewardEnum:
				return
			#以前完成的每日首充奖励是否已经领取
			if role.GetI8(rewardEnum) != 2:
				return
			
			nextRewardEnum = FiveGiftDefine.DAY_TO_FIRST_PAY_REWARD_ENUM.get(dayFirstPayDays + 1)
			if not nextRewardEnum:
				return
			role.IncI8(EnumInt8.DayFirstPayDays, 1)
			#设置每日首充奖励可领取
			role.SetI8(nextRewardEnum, 1)
			
def OnRoleHeFu(role, param):
	'''
	合服调用
	@param role:
	@param param:
	'''
	#计算合服当天的时间天数
	hefuTime = WorldData.WD.get(EnumSysData.HeFuKey)
	hefuDays = (Time.DateTime2UnitTime(hefuTime) + cDateTime.TimeZoneSeconds()) / 86400
	
	#重置每日首充
	#设定每日首充图标出现的时间(保存时间的第二天出现图标)
	role.SetI16(EnumInt16.DayFirstPayIconShowTime, hefuDays)
	#重置每日首充天数
	role.SetI8(EnumInt8.DayFirstPayDays, 0)
	#设定合服当天已经完成首充
	role.SetDI1(EnumDayInt1.DayFirstPay, 1)
	#清空所有每日首充奖励
	for enum in FiveGiftDefine.DAY_TO_FIRST_PAY_REWARD_ENUM.itervalues():
		role.SetI8(enum, 0)

#===============================================================================
# 客户端请求
#===============================================================================
def RequestGetDayFirstPayReward(role, msg):
	'''
	客户端请求领取每日首充奖励
	@param role:
	@param msg:
	'''
	#日志
	with TraDayFirstPayReward:
		GetDayFirstPayReward(role)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_GamePoint, AfterEve_QPoint)
		#合服后调用
		Event.RegEvent(Event.Eve_AfterRoleHeFu, OnRoleHeFu)
	
		#日志
		TraDayFirstPayReward = AutoLog.AutoTransaction("TraDayFirstPayReward", "每日首充奖励")
	
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Day_First_Pay_Reward", "客户端请求领取每日首充奖励"), RequestGetDayFirstPayReward)
	
	
	