#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SpringFestival.GodWealth")
#===============================================================================
# 天降财神
#===============================================================================
import Environment
import cRoleMgr
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumObj, EnumInt32
from Game.Role import Event
from Game.Activity.SpringFestival import SpringFestivalConfig
from Game.Activity import CircularDefine
import cRoleDataMgr

if "_HasLoad" not in dir():
	IsOpen = False #开启标志
	#日志
	GodWealthReward = AutoLog.AutoTransaction("GodWealthReward", "天降财神奖励")
#===============活动开启和关闭===================
def OpenAct(param1, param2):
	#开启活动
	if param2 != CircularDefine.CA_SpringFGodWealth:
		return
	
	global IsOpen
	if IsOpen:
		print 'GE_EXC, SpringFGodWealth is already open'
	IsOpen = True

def CloseAct(param1, param2):
	#关闭活动
	if param2 != CircularDefine.CA_SpringFGodWealth:
		return
	
	global IsOpen
	if not IsOpen:
		print 'GE_EXC, SpringFGodWealth is already close'
	IsOpen = False
#============================================

def RequestGetGodWealthReward(role, param):
	'''
	客户端请求领取天降财神奖励
	@param role:
	@param param:
	'''
	index = param
	
	if not IsOpen:
		return
	
	if role.GetLevel() < EnumGameConfig.Spring_Festival_NeedLevel:
		return
	
	cfg = SpringFestivalConfig.GOD_WEALTH_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in SpringFestivalConfig.GOD_WEALTH_DICT" % index
		return
	
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	GetData = SpringFestivalData.get(3, set())
	if index in GetData:
		return
	
	if role.GetI32(EnumInt32.DayConsumeUnbindRMB_Q) < cfg.needCostRMB:
		return
	
	with GodWealthReward:
		#加入已领取和增加总的领取数
		SpringFestivalData[3].add(index)
		SpringFestivalData[4] = SpringFestivalData.get(4, 0) + 1
		
		tips = GlobalPrompt.Reward_Tips
		if cfg.rewardRMB_S:
			role.IncUnbindRMB_S(cfg.rewardRMB_S)
			tips += GlobalPrompt.UnBindRMB_Tips % cfg.rewardRMB_S
			role.Msg(2, 0, tips)
			
		role.SendObj(Sync_GodWealthReward_Data, [SpringFestivalData.get(3), SpringFestivalData.get(4)])
	
def AfterLogin(role, param):
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	role.SendObj(Sync_GodWealthReward_Data, [SpringFestivalData.get(3), SpringFestivalData.get(4)])
	
def SyncRoleOtherData(role, param):
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	role.SendObj(Sync_GodWealthReward_Data, [SpringFestivalData.get(3), SpringFestivalData.get(4)])
	
def RoleDayClear(role, param):
	#清除每日消费的充值神石
	role.SetI32(EnumInt32.DayConsumeUnbindRMB_Q, 0)
	
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	#清空已领取的
	SpringFestivalData[3] = set()
	role.SendObj(Sync_GodWealthReward_Data, [SpringFestivalData.get(3), SpringFestivalData.get(4)])
	
def OnChangeUnbindRMB_Q(role, param):
	#充值神石
	oldValue, newValue = param
	if newValue >= oldValue:
		return
	role.IncI32(EnumInt32.DayConsumeUnbindRMB_Q, oldValue - newValue)

def AfterDayConsumeUnbindRMB_Q(role, oldValue, newValue):
	Event.TriggerEvent(Event.Eve_AfterChangeDayConsumeUnbindRMB_Q, role, (oldValue, newValue))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, OnChangeUnbindRMB_Q)
		cRoleDataMgr.SetInt32Fun(EnumInt32.DayConsumeUnbindRMB_Q, AfterDayConsumeUnbindRMB_Q)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OpenAct)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseAct)
		
		
		Sync_GodWealthReward_Data = AutoMessage.AllotMessage("Sync_GodWealthReward_Data", "同步春节活动天降财神数据")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_Get_GodWealth_Reward", "客户端请求领取天降财神奖励"), RequestGetGodWealthReward)
		
