#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionLoginGift")
#===============================================================================
# 激情活动登陆有礼
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Game.Role import Event
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumInt32
from Game.Activity.PassionAct import PassionDefine, PassionActVersionMgr, \
	PassionLoginGiftConfig


if "_HasLoad" not in dir():
	IsStart = False
	#消息
	SyncPassionGiftLoginRec = AutoMessage.AllotMessage("SyncPassionLoginGiftLoginRec", "同步激情活动登陆有礼登录领奖记录")
	SyncPassionGiftLoginRechargeRec = AutoMessage.AllotMessage("SyncPassionGiftLoginRechargeRec", "同步激情活动登陆有礼登充值记录")
	SyncPassionGiftLoginRechargeWardRec = AutoMessage.AllotMessage("SyncPassionGiftLoginRechargeWardRec", "同步激情活动登陆有礼充值领奖记录")
	#日志
	TraPassionLoginGiftLoginAward = AutoLog.AutoTransaction("TraPassionLoginGiftLoginAward", "激情活动登陆有礼登录奖励")
	TraPassionLoginGiftRechargeAward = AutoLog.AutoTransaction("TraPassionLoginGiftRechargeAward", "激情活动登陆有礼充值奖励")
	

def Start(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionLoginGift != circularType:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open CA_PassionLoginGift"
		return
		
	IsStart = True
	

def End(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionLoginGift != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end CA_PassionLoginGift while not start"
		return
		
	IsStart = False


def GetDayIndex():
	dateTuple = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day())
	return PassionLoginGiftConfig.DayIndexConfigDict.get(dateTuple)


def AfterChangeUnbindRMB_Q(role, param):
	if not IsStart:
		return
	
	oldValue, nowValue = param
	if nowValue <= oldValue:
		return
	
	rechargeValue = nowValue - oldValue
	
	dayIndex = GetDayIndex()
	if not dayIndex:
		return
	
	rechargeRecDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionLoginGiftRechargeRec, {})
	rechargeRecDict[dayIndex] = rechargeRecDict.get(dayIndex, 0) + rechargeValue
	
	#同步客户端
	role.SendObj(SyncPassionGiftLoginRechargeRec, rechargeRecDict)


def RequestGetLoginAward(role, msg):
	'''
	客户端请求获取登录有礼奖励
	'''
	if not IsStart:
		return

	if role.GetLevel() < EnumGameConfig.PassionLoginGiftNeedLevel:
		return
	
	if not PassionActVersionMgr.CheckRoleVersion(role):
		print "GE_EXC,role(%s) PassionAct version(%s) not equal to NowVersion(%s)" % (role.GetRoleID(), role.GetI32(EnumInt32.PassionActVersion, PassionActVersionMgr.PassionVersion))
		return
	
	dayIndex = msg
	loginRecDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionLoginGiftLoginRec, {})
	
	if dayIndex not in loginRecDict:
		return
	if loginRecDict[dayIndex]:
		return
	
	config = PassionLoginGiftConfig.LoginGiftConfigDict.get(dayIndex)
	if config is None:
		print "GE_EXC,error while config = PassionLoginGiftConfig.LoginGiftConfigDict.get(dayIndex)%s for role(%s)" % (dayIndex, role.GetRoleID())
		return
	
	tips = GlobalPrompt.Reward_Tips
	with TraPassionLoginGiftLoginAward:
		loginRecDict[dayIndex] = True
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePassionLoginGiftLoginAward, dayIndex)
		if config.loginMoney:
			role.IncMoney(config.loginMoney)
			tips += GlobalPrompt.Money_Tips % config.loginMoney
		for item in config.loginItems:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	#同步客户端
	role.SendObj(SyncPassionGiftLoginRec, loginRecDict)
	role.Msg(2, 0, tips)


def RequestGetRechargeAward(role, msg):
	'''
	客户端请求获取登录有礼奖励
	'''
	if not IsStart:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionLoginGiftNeedLevel:
		return
	
	#版本号不一致
	if not PassionActVersionMgr.CheckRoleVersion(role):
		print "GE_EXC,role(%s) PassionAct version(%s) not equal to NowVersion(%s)" % (role.GetRoleID(), role.GetI32(EnumInt32.PassionActVersion, PassionActVersionMgr.PassionVersion))
		return
	
	dayIndex = msg
	
	rechargeAwradRecSet = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionLoginGiftRechargeAwradRec, set([]))
	
	if dayIndex in rechargeAwradRecSet:
		return
	
	rechargeRecDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionLoginGiftRechargeRec, {})
	
	rechargeValue = rechargeRecDict.get(dayIndex, 0)
	
	config = PassionLoginGiftConfig.LoginGiftConfigDict.get(dayIndex)
	if config is None:
		print "GE_EXC,error while config = PassionLoginGiftConfig.LoginGiftConfigDict.get(dayIndex)%s for role(%s)" % (dayIndex, role.GetRoleID())
		return
	
	if rechargeValue < config.needRechargeRMB:
		return
	
	
	tips = GlobalPrompt.Reward_Tips
	with TraPassionLoginGiftRechargeAward:
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePassionLoginGiftRechargeAward, dayIndex)
		rechargeAwradRecSet.add(dayIndex)
		for item in config.rechargeItems:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	role.SendObj(SyncPassionGiftLoginRechargeWardRec, rechargeAwradRecSet)
	role.Msg(2, 0, tips)


def OnRoleDayClear(role, param):
	if not IsStart:
		return
	dayIndex = GetDayIndex()
	if dayIndex:
		loginRecDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionLoginGiftLoginRec, {})
		loginRecDict.setdefault(dayIndex, False)
		
	loginRecDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionLoginGiftLoginRec, {})
	role.SendObj(SyncPassionGiftLoginRec, loginRecDict)


def OnSyncRoleOtherData(role, param):
	if not IsStart:
		return
	
	dayIndex = GetDayIndex()
	if dayIndex:
		loginRecDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionLoginGiftLoginRec, {})
		loginRecDict.setdefault(dayIndex, False)
	
	rechargeAwradRecSet = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionLoginGiftRechargeAwradRec, set([]))
	rechargeRecDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionLoginGiftRechargeRec, {})
	loginRecDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionLoginGiftLoginRec, {})
	
	role.SendObj(SyncPassionGiftLoginRec, loginRecDict)
	role.SendObj(SyncPassionGiftLoginRechargeRec, rechargeRecDict)
	role.SendObj(SyncPassionGiftLoginRechargeWardRec, rechargeAwradRecSet)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetLoginAward_PassionLoginGift", "客户端请求获取激情活动登录有礼 登录奖励"), RequestGetLoginAward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetConsumeAward_PassionLoginGift", "客户端请求获取激情活动登录有礼消费奖励"), RequestGetRechargeAward)
