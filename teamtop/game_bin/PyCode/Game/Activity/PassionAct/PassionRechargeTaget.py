#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionRechargeTaget")
#===============================================================================
# 每日购买神石返好礼
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Role.Data import EnumObj
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from Game.Activity.PassionAct import PassionRechargeTargetConfig, PassionDefine
from Game.Activity import CircularDefine

if "_HasLoad" not in dir():
	IsStart = False
	#消息
	SyncPassionRechargeTagetGotSet = AutoMessage.AllotMessage("SyncPassionRechargeTagetGotSet", "同步激情活动每日购买神石返好礼已领取索引")
	#日志
	TraPassionRechargeTagetAward = AutoLog.AutoTransaction("TraPassionRechargeTagetAward", "激情活动每日购买神石返好礼")


def Start(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionRechargeTaget != circularType:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open CA_PassionRechargeTaget"
		return
		
	IsStart = True
	

def End(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionRechargeTaget != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end CA_PassionRechargeTaget while not start"
		return
		
	IsStart = False


def RequestGetTargetReward(role, msg):
	'''
	'''
	if not IsStart:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.PassionMinLevel:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionRechargeTarget, set())
	if index in gotSet:
		return
	
	config = PassionRechargeTargetConfig.PassionRechargeTargetCfgDict.get((roleLevel, index))
	if not config:
		print "GE_EXC, error while config = PassionRechargeTargetConfig.PassionRechargeTargetCfgDict.get((%s, %s))" % (roleLevel, index) 
		return
	
	if role.GetDayBuyUnbindRMB_Q() < config.needRecharge:
		return
	
	with TraPassionRechargeTagetAward:
		gotSet.add(index)
		for item in config.rewardItems:
			role.AddItem(*item)
	
	role.SendObj(SyncPassionRechargeTagetGotSet, gotSet)
	

def OnRoleDayClear(role, param):
	role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionRechargeTarget] = gotSet = set()
	role.SendObj(SyncPassionRechargeTagetGotSet, gotSet)
	

def OnSyncRoleOtherData(role, param):
	if not IsStart:
		return
	gotSet = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionRechargeTarget, set())
	role.SendObj(SyncPassionRechargeTagetGotSet, gotSet)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetTargetReward_PassionRechargeTaget", "客户端请求领取激情每日购买神石返好礼"), RequestGetTargetReward)
		
