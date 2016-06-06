#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTurntable")
#===============================================================================
# 激情活动幸运转盘(七夕活动新增)
#===============================================================================
import random
import cRoleMgr
import Environment
from Util import Random
from Game.Role import Event
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumInt8, EnumInt32
from Game.Activity.PassionAct import PassionTurntableConfig, PassionDefine, PassionActVersionMgr


if "_HasLoad" not in dir():
	IsStart = False
	
	#消息
	SyncPassionTurntableResultCallBack = AutoMessage.AllotMessage("SyncPassionTurntableResultCallBack", "同步客户端激情活动幸运转盘抽奖结果(回调)")
	SyncPassionTurntableCurrentScheme = AutoMessage.AllotMessage("SyncPassionTurntableCurrentScheme", "同步客户端激情活动幸运转盘抽当前方案")
	SyncPassionTurntableHasGotIdx = AutoMessage.AllotMessage("SyncPassionTurntableHasGotIdx", "同步客户端激情活动幸运转盘已经抽取过的位置")
	
	#日志
	TraPassionTurntableCost = AutoLog.AutoTransaction("TraPassionTurntableCost", "激情活动转盘抽奖消耗")
	TraPassionTurntableReward = AutoLog.AutoTransaction("TraPassionTurntableReward", "激情活动转盘发奖")
	TraPassionTurntableChangeScheme = AutoLog.AutoTransaction("TraPassionTurntableChangeScheme", "激情活动转盘更换奖励方案")
	
	
def Start(*param):
	_, activetype = param
	if activetype != CircularDefine.CA_PassionTurntable:
		return
	global IsStart
	if IsStart:
		print "GE_EXC, PassionTurntable is already started "
		return
	IsStart = True


def End(*param):
	_, activetype = param
	if activetype != CircularDefine.CA_PassionTurntable:
		return
	global IsStart
	if not IsStart:
		print "GE_EXC, PassionTurntable is already ended "
		return
	IsStart = False


def RequestGetAward(role, msg):
	'''
	客户端请求抽奖
	'''
	if IsStart is False:
		return
	#角色身上版本号与当前版本号不一致
	if role.GetI32(EnumInt32.PassionActVersion) != PassionActVersionMgr.PassionVersion:
		print "GE_EXC,role(%s) PassionAct version(%s) not equal to NowVersion(%s)" % (role.GetRoleID(), role.GetI32(EnumInt32.PassionActVersion, PassionActVersionMgr.PassionVersion))
		return
	
	roleLevel = role.GetLevel()
	if role.GetLevel() < EnumGameConfig.PassionTurntableNeedLevel:
		return
	
	levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)
	if not levelConfig:
		print "GE_EXC, error while levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)(%s)" % roleLevel 
		return
	
	nowTimes = role.GetI8(EnumInt8.PassionTurntableTimes) + 1
	priceConfig = PassionTurntableConfig.TurntablePriceConfigDict.get(nowTimes)
	if not priceConfig:
		print "GE_EXC,error while priceConfig = PassionTurntableConfig.TurntablePriceConfigDict.get(nowTimes)(%s)" % nowTimes
		return
	
	needCoding = priceConfig.needCoding
	needCnt = priceConfig.needCnt
	
	if role.ItemCnt(needCoding) < needCnt:
		return
	
	passionTurntableDataDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionTurntable, {})
	#获取当前方案的下标，如果没有当前方案，则设为当前等级的第一个
	schemeID = passionTurntableDataDict.setdefault("currentSchemeIdx", levelConfig.schemeList[0])
	#获取当前已经领过奖励的下标集合，如果还没有领取过，则为空集合
	currentGotIdxSet = passionTurntableDataDict.setdefault("currentHasGotSet", set())
	#根据当前方案的下标获取方案的id
	
	schemeConfig = PassionTurntableConfig.TurntableSchemeConfigDict.get(schemeID)
	if not schemeConfig:
		print "GE_EXC,error while schemeConfig = PassionTurntableConfig.TurntableSchemeConfigDict.get(schemeID)(%s)" % schemeID
		return
	
	randomRate = Random.RandomRate()
	for idx, (itemCoding, itemCnt, rate) in enumerate(schemeConfig.RateList):
		if idx in currentGotIdxSet:
			continue
		randomRate.AddRandomItem(rate, (idx, itemCoding, itemCnt))
	
	theIdx, itemCoding, itemCnt = randomRate.RandomOne()
	
	#此处扣费
	with TraPassionTurntableCost:
		if role.DelItem(needCoding, needCnt) < needCnt:
			return
		role.IncI8(EnumInt8.PassionTurntableTimes, 1)
	
	role.SendObjAndBack(SyncPassionTurntableResultCallBack, theIdx, 20, BackFun, (theIdx, itemCoding, itemCnt, schemeConfig))


def BackFun(role, callargv, params):
	#抽奖回调
	passionTurntableDataDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionTurntable, {})
	#获取当前方案的下标，如果没有当前方案，则下标为0
	currentSchemeIdx = passionTurntableDataDict["currentSchemeIdx"]
	#获取当前已经领过奖励的下标集合，如果还没有领取过，则为空集合
	currentGotIdxSet = passionTurntableDataDict["currentHasGotSet"]
	
	theIdx, itemCoding, itemCnt, schemeConfig = params
	
	roleLevel = role.GetLevel()
	levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)
	if not levelConfig:
		print "GE_EXC, error while levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)(%s)" % roleLevel 
		return
	
	#此处发奖
	with TraPassionTurntableReward:
		currentGotIdxSet.add(theIdx)
		role.AddItem(itemCoding, itemCnt)
		#如果一轮已经抽完了的话，要重置
		if len(currentGotIdxSet) >= len(schemeConfig.RateList):
			#这里用一次浅复制
			randomList = list(levelConfig.schemeList)
			if currentSchemeIdx in randomList:
				randomList.remove(currentSchemeIdx)
			currentSchemeIdx = passionTurntableDataDict["currentSchemeIdx"] = random.choice(randomList)
			currentGotIdxSet = passionTurntableDataDict["currentHasGotSet"] = set()
			role.SetI8(EnumInt8.PassionTurntableTimes, 0)

	role.SendObj(SyncPassionTurntableHasGotIdx, currentGotIdxSet)
	role.SendObj(SyncPassionTurntableCurrentScheme, currentSchemeIdx)
	
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (itemCoding, itemCnt))
	if (itemCoding, itemCnt) in schemeConfig.goodItems:
		cRoleMgr.Msg(1, 0, GlobalPrompt.PassionTurntableGlobalTell % (role.GetRoleName(), itemCoding, itemCnt))
	

def RequestChangeScheme(role, msg):
	'''
	客户端请求更换奖励方案(刷新)
	'''
	if IsStart is False:
		return
	
	#角色身上版本号与当前版本号不一致
	if role.GetI32(EnumInt32.PassionActVersion) != PassionActVersionMgr.PassionVersion:
		print "GE_EXC,role(%s) PassionAct version(%s) not equal to NowVersion(%s)" % (role.GetRoleID(), role.GetI32(EnumInt32.PassionActVersion, PassionActVersionMgr.PassionVersion))
		return
	
	roleLevel = role.GetLevel()
	if role.GetLevel() < EnumGameConfig.PassionTurntableNeedLevel:
		return
	
	if role.GetUnbindRMB() < EnumGameConfig.PassionTurntableRefreshPrice:
		return
	
	levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)
	if not levelConfig:
		print "GE_EXC, error while levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)(%s)" % roleLevel 
		return
	
	passionTurntableDataDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionTurntable, {})
	currentSchemeIdx = passionTurntableDataDict.setdefault("currentSchemeIdx", levelConfig.schemeList[0])
	
	#这里加日志，先扣钱
	with TraPassionTurntableChangeScheme:
		role.DecUnbindRMB(EnumGameConfig.PassionTurntableRefreshPrice)
		role.SetI8(EnumInt8.PassionTurntableTimes, 0)
		randomList = list(levelConfig.schemeList)
		if currentSchemeIdx in randomList:
			randomList.remove(currentSchemeIdx)
		currentSchemeIdx = passionTurntableDataDict["currentSchemeIdx"] = random.choice(randomList)
		currentGotIdxSet = passionTurntableDataDict["currentHasGotSet"] = set()
		
	role.SendObj(SyncPassionTurntableHasGotIdx, currentGotIdxSet)
	role.SendObj(SyncPassionTurntableCurrentScheme, currentSchemeIdx)
	role.Msg(2, 0, GlobalPrompt.PassionTurntableChangeTips)
	

def RequestOpenPanel(role, msg):
	'''
	客户端请求打开面板
	'''
	if IsStart is False:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.PassionTurntableNeedLevel:
		return
	
	levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)
	if not levelConfig:
		print "GE_EXC, error while levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)(%s)" % roleLevel 
		return
	
	passionTurntableDataDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionTurntable, {})
	#获取当前方案的下标，如果没有当前方案，则设为当前方案的第一个
	currentSchemeIdx = passionTurntableDataDict.get("currentSchemeIdx", levelConfig.schemeList[0])
	#获取当前已经领过奖励的下标集合，如果还没有领取过，则为空集合
	hasGotSet = passionTurntableDataDict.get("currentHasGotSet", set())
	
	#将方案id和已经领奖过的下标集合同步给客户端
	role.SendObj(SyncPassionTurntableHasGotIdx, hasGotSet)
	role.SendObj(SyncPassionTurntableCurrentScheme, currentSchemeIdx)


def AfterLevelUp(role, param):
	'''
	角色升级后处理
	'''
	if IsStart is False:
		return
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.PassionTurntableNeedLevel:
		return
	levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)
	if not levelConfig:
		print "GE_EXC, error while levelConfig = PassionTurntableConfig.TurntableLevelConfigDict.get(roleLevel)(%s)" % roleLevel 
		return
	
	passionTurntableDataDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionTurntable, {})
	#获取当前方案的下标，如果没有当前方案，则设为当前方案的第一个
	currentSchemeIdx = passionTurntableDataDict.get("currentSchemeIdx", levelConfig.schemeList[0])
	#获取当前已经领过奖励的下标集合，如果还没有领取过，则为空集合
	hasGotSet = passionTurntableDataDict.get("currentHasGotSet", set())
	
	#将方案id和已经领奖过的下标集合同步给客户端
	role.SendObj(SyncPassionTurntableHasGotIdx, hasGotSet)
	role.SendObj(SyncPassionTurntableCurrentScheme, currentSchemeIdx)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsNA() or Environment.EnvIsTK() or Environment.EnvIsPL()):
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionTurntableOpenPanel", "客户端请求打开激情活动转盘面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionTurntableChangeTurntable", "客户端请求激情活动转盘更改方案"), RequestChangeScheme)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionTurntableGetAward", "客户端请求激情活动转盘抽奖"), RequestGetAward)

