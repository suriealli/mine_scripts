#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionLianChongGift")
#===============================================================================
# 激情活动连冲豪礼
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from Game.Role.Data import EnumObj, EnumDayInt1, EnumInt8
from Game.Activity.PassionAct import  PassionDefine, PassionLianChongGiftConfig
from Game.Activity import CircularDefine

if "_HasLoad" not in dir():
	IsStart = False
	NeedRechargeUnbindRMB = 200
	#消息
	SyncPassionLianChongGiftGotSet = AutoMessage.AllotMessage("SyncPassionLianChongGiftGotSet", "同步激情活动连充豪礼已领取天数")
	#日志
	TraPassionLianChongGiftDays = AutoLog.AutoTransaction("TraPassionLianChongGiftDays", "激情活动连充豪礼连充天数")
	TraPassionLianChongGiftAward = AutoLog.AutoTransaction("TraPassionLianChongGiftAward", "激情活动连充豪礼奖励")


def Start(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionLianChongGift != circularType:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open CA_PassionLianChongGift"
		return
		
	IsStart = True
	

def End(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionLianChongGift != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end CA_PassionLianChongGift while not start"
		return
		
	IsStart = False


def RequestLianChongReward(role, msg):
	'''
	'''
	if not IsStart:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.PassionMinLevel:
		return
	
	days = msg
	if role.GetI8(EnumInt8.PassionLianChongGiftDays) < days:
		return
	
	gotSet = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionLianchongDays, set())
	if days in gotSet:
		return
	
	config = PassionLianChongGiftConfig.PassionLianChongGiftConfigDict.get((roleLevel, days))
	if not config:
		print "GE_EXC, error while config = PassionLianChongGiftConfig.PassionLianChongGiftConfigDict.get((%s, %s))" % (roleLevel, days) 
		return
	
	with TraPassionLianChongGiftAward:
		gotSet.add(days)
		for item in config.rewardItems:
			role.AddItem(*item)
	
	role.SendObj(SyncPassionLianChongGiftGotSet, gotSet)


def AfterChangeDayBuyUnbindRMB_Q(role, param):
	if not IsStart:
		return
	if role.GetDayBuyUnbindRMB_Q() < NeedRechargeUnbindRMB:
		return
	if role.GetDI1(EnumDayInt1.PassionLianChongRec):
		return
	
	with TraPassionLianChongGiftDays:
		role.SetDI1(EnumDayInt1.PassionLianChongRec, True)
		role.IncI8(EnumInt8.PassionLianChongGiftDays, 1)
	

def OnSyncRoleOtherData(role, param):
	if not IsStart:
		return
	
	if role.GetDayBuyUnbindRMB_Q() > 200:
		if not role.GetDI1(EnumDayInt1.PassionLianChongRec):
			with TraPassionLianChongGiftDays:
				role.SetDI1(EnumDayInt1.PassionLianChongRec, True)
				role.IncI8(EnumInt8.PassionLianChongGiftDays, 1)
		
	gotSet = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionLianchongDays, set())
	role.SendObj(SyncPassionLianChongGiftGotSet, gotSet)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeDayBuyUnbindRMB_Q)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLianChongReward_PassionLianChongGift", "客户端请求激情活动连充豪礼领奖"), RequestLianChongReward)
