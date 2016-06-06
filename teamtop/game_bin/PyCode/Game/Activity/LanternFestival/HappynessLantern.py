#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LanternFestival.HappynessLantern")
#===============================================================================
# 欢乐花灯
#===============================================================================
import random
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Role.Data import EnumInt32
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Game.Activity.LanternFestival import LanternFestivalConfig

if "_HasLoad" not in dir():
	IsStart = False
	#日志
	Tra_LanternHappinessUpper = AutoLog.AutoTransaction("Tra_LanternHappinessUpper", "元宵节欢乐花灯高级点灯")
	Tra_LanternHappinessLower = AutoLog.AutoTransaction("Tra_LanternHappinessLower", "元宵节欢乐花灯普通点灯")
	
	
def Start(param1, param2):
	if param2 != CircularDefine.CA_HappnessLantern:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC, HappnessLantern is already started"
		return
	
	IsStart = True
	

def End(param1, param2):
	if param2 != CircularDefine.CA_HappnessLantern:
		return
	global IsStart
	if not IsStart:
		print "GE_EXC, HappnessLantern is already ended"
		return
	IsStart = False


def RequestLightUpLantern(role, msg):
	'''
	客户端请求点亮花灯
	@param role
	@param msg 1普通  2高级
	'''
	levelSection = GetRoleLevelSection(role)
	lanternType = msg
	
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return

	config = LanternFestivalConfig.HappinessLanternDict.get(levelSection)
	if config is None:
		return
	
	if lanternType == 1:
		needMoney = config.needMoney
		needItem = config.lowerLantern
		incPoint = 0
		Tra = Tra_LanternHappinessLower
		itemCoding, itemCnt, isGlobalTell = config.RandomRateLower.RandomOne()
		
	elif lanternType == 2:
		needMoney = 0
		needItem = config.upperlantern
		incPoint = config.awardPoint
		Tra = Tra_LanternHappinessUpper
		itemCoding, itemCnt, isGlobalTell = config.RandomRateUpper.RandomOne()
	else:
		return
	
	if role.GetMoney() < needMoney:
		return
	
	if role.ItemCnt(needItem[0]) < needItem[1]:
		return
	
	
	tips = GlobalPrompt.Reward_Tips
	with Tra:
		if needMoney:
			role.DecMoney(needMoney)
		if role.DelItem(*needItem) < needItem[1]:
			return
		if incPoint:
			#这里需要添加每日积分的计算
			role.IncI32(EnumInt32.LanternFestivalPoint, incPoint)
			role.IncI32(EnumInt32.LanternFestivalPointDaily, incPoint)
			tips += GlobalPrompt.LanternPointTips % incPoint
			
		if itemCnt:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
	
	role.Msg(2, 0, tips)
	
	if isGlobalTell == 1:
		roleName = role.GetRoleName()
		cRoleMgr.Msg(11, 0, GlobalPrompt.LanternHappnessGlobalTell % (roleName, itemCoding, itemCnt))


def GetRoleLevelSection(role):
	'''
	获取角色的等级区间
	'''
	roleLevel = role.GetLevel()
	sectionList = list(LanternFestivalConfig.HappinessLanternSectionSet)
	if roleLevel not in sectionList:
		sectionList.append(roleLevel)
	sectionList.sort()
	section = sectionList.index(roleLevel) + 1
	return section


def HappynessLantern_ExtendReward(role, param):
	#活动是否开始
	global IsStart
	if IsStart is False:
		return None
	
	activityType, idx = param
	
	oddsConfig = LanternFestivalConfig.LanternExtendedConfigDict.get((activityType, idx))
	if not oddsConfig:
		return None
	
	rewardDict = {}
	if role.GetLevel() >= oddsConfig.needLevel:
		if random.randint(1, 10000) <= oddsConfig.dropOdds:
			rewardDict[oddsConfig.dropItemCoding] = 1
			
	return rewardDict


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLightUpLantern", "客户端请求欢乐花灯点花灯"), RequestLightUpLantern)
