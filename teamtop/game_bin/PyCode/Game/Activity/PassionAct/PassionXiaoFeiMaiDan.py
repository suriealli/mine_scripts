#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionXiaoFeiMaiDan")
#===============================================================================
# 激情活动你消费我买单
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
	PassionXiaoFeiMaiDanConfig

if "_HasLoad" not in dir():
	IsStart = False
	#消息
	SyncPassionXiaoFeiMaiDanConsumeRec = AutoMessage.AllotMessage("SyncPassionXiaoFeiMaiDanConsumeRec", "同步激情活动你消费我买单消费记录")
	SyncPassionXiaoFeiMaiDanConsumeAwardRec = AutoMessage.AllotMessage("SyncPassionXiaoFeiMaiDanConsumeAwardRec", "同步激情活动你消费我买单领奖记录")
	
	#日志
	TraPassionXiaoFeiMaiDanAward = AutoLog.AutoTransaction("TraPassionXiaoFeiMaiDanAward", "激情活动你消费我买单活动返利")

def Start(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionXiaoFeiMaiDan != circularType:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open CA_PassionXiaoFeiMaiDan"
		return
		
	IsStart = True
	

def End(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionXiaoFeiMaiDan != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end CA_PassionXiaoFeiMaiDan while not start"
		return
		
	IsStart = False


def GetDayIndex():
	dateTuple = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day())
	return PassionXiaoFeiMaiDanConfig.DayIndexConfigDict.get(dateTuple)


def AfterChangeUnbindRMB_Q(role, param):
	if not IsStart:
		return
	
	dayIndex = GetDayIndex()
	if not dayIndex:
		return
	config = PassionXiaoFeiMaiDanConfig.XiaoFeiMaiDanConfigDict.get(dayIndex)
	if config is None:
		print "GE_EXC,error while config = PassionXiaoFeiMaiDanConfig.XiaoFeiMaiDanConfigDict.get(dayIndex) %s for role(%s)" % (dayIndex, role.GetRoleID())
		return
	if not config.needRecordConsume:
		return
	
	oldValue, nowValue = param
	if nowValue >= oldValue:
		return
	
	consumeValue = oldValue - nowValue 
	
	consumeRecDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionMaiDanConsumeRec, {})
	consumeRecDict[dayIndex] = consumeRecDict.get(dayIndex, 0) + consumeValue
	
	role.SendObj(SyncPassionXiaoFeiMaiDanConsumeRec, consumeRecDict)


def RequestGetAward(role, msg):
	'''
	客户端请求获取登录有礼奖励
	'''
	if not IsStart:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionXiaoFeiMaiDanNeedLevel:
		return
	
	if not PassionActVersionMgr.CheckRoleVersion(role):
		print "GE_EXC,role(%s) PassionAct version(%s) not equal to NowVersion(%s)" % (role.GetRoleID(), role.GetI32(EnumInt32.PassionActVersion, PassionActVersionMgr.PassionVersion))
		return
	
	dayIndex = msg
	awardRecSet = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionMaiDanConsumeAwradRec, set([]))
	if dayIndex in awardRecSet:
		return
	
	config = PassionXiaoFeiMaiDanConfig.XiaoFeiMaiDanConfigDict.get(dayIndex)
	if config is None:
		print "GE_EXC,error while config = PassionXiaoFeiMaiDanConfig.XiaoFeiMaiDanConfigDict.get(dayIndex) %s for role(%s)" % (dayIndex, role.GetRoleID())
		return
	
	todayIndex = GetDayIndex()
	if not todayIndex:
		return
	if todayIndex > config.endBackDayIndex:
		return
	if todayIndex < config.startBackDayIndex:
		return
	
	consumeRecDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMaiDanConsumeRec, {})
	if dayIndex not in consumeRecDict:
		return
	
	consumeValue = consumeRecDict[dayIndex]
	
	backValue = consumeValue * config.percent / 100
	backValue = min(config.maxBack, backValue)
	
	
	tips = GlobalPrompt.Reward_Tips
	with TraPassionXiaoFeiMaiDanAward:
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePassionXiaoFeiMaiDanAward, (dayIndex, consumeValue))
		awardRecSet.add(dayIndex)
		role.IncUnbindRMB_S(backValue)
		tips += GlobalPrompt.UnBindRMB_Tips % backValue
	
	role.SendObj(SyncPassionXiaoFeiMaiDanConsumeAwardRec, awardRecSet)
	role.Msg(2, 0, tips)


def OnSyncRoleOtherData(role, param):
	if not IsStart:
		return
	consumeRecDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMaiDanConsumeRec, {})
	awardRecSet = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMaiDanConsumeAwradRec, set([]))
	role.SendObj(SyncPassionXiaoFeiMaiDanConsumeAwardRec, awardRecSet)
	role.SendObj(SyncPassionXiaoFeiMaiDanConsumeRec, consumeRecDict)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetAward_PassionXiaoFeiMaiDan", "客户端请求获取激情活动你消费我买单奖励"), RequestGetAward)
