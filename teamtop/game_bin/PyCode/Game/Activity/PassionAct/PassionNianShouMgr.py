#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionNianShouMgr")
#===============================================================================
# 春节打年兽
#===============================================================================
import random
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Activity.PassionAct import PassionNianShouConfig
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role import Event
from Common.Message import AutoMessage

FirItemCoding = 29376
CostMoney = 80000
CostRmb = 88
if "_HasLoad" not in dir() :
	IsStart = False
	#记录日志
	Tra_NianShou_Nomal = AutoLog.AutoTransaction("Tra_NianShou_Nomal", "打年兽普通攻击")
	Tra_NianShou_Special = AutoLog.AutoTransaction("Tra_NianShou_Special", "打年兽高级攻击")
	
	
def OpenActive(*param):
	_, circularType = param
	if CircularDefine.CA_PassionNianShou != circularType:
		return
	global IsStart
	if IsStart  :
		print "GE_EXC, repeat PassionNianShou has started"
	IsStart = True

def CloseActive(*param):
	_, circularType = param
	if CircularDefine.CA_PassionChunJieActive != circularType:
		return
	global IsStart
	if not IsStart :
		print "GE_EXC, repeat PassionNianShou has closed"
	IsStart =False
	

def NormalFightNianShou(role, counts):
	global IsStart
	if not IsStart :
		return
	if counts not in (1, 10) :
		return
	#等级不足 
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	#金钱或道具不足
	if role.GetMoney() < CostMoney*counts or  role.ItemCnt(FirItemCoding) < counts:
		return
	RoleLevel = role.GetLevel()
	RangeId = 0
	for cf in PassionNianShouConfig.NianShouReward.itervalues() :
		if cf.levelRange[0] <= RoleLevel <= cf.levelRange[1] and cf.rewardType == 1:
			RangeId = cf.rangeId
			break
	if not RangeId :
		print "GE_EXC, repeat no Level %s in NormalFightNianShou" % RoleLevel
		return
	
	NianShouRange = PassionNianShouConfig.NianShou_Reward_Random.get(RangeId)
	if not NianShouRange :
		print "GE_EXC, repeat no RangeId %s in NormalFightNianShou" % RangeId
		return
	ItemDict = {}
	#发奖励
	with Tra_NianShou_Nomal :
		role.DecMoney(CostMoney*counts)
		role.DelItem(FirItemCoding, counts)
		for _ in range(counts) :
			isBroadcastTips = ""
			RewardId = NianShouRange.RandomOne()
			itemsMgr = PassionNianShouConfig.NianShouReward.get(RewardId)
			if itemsMgr.isBroadcast :
				itemCoding, cnt = itemsMgr.item
				isBroadcastTips += GlobalPrompt.PassionDaNianShouTip % (role.GetRoleName(),itemCoding, cnt)
				role.Msg(11, 0, isBroadcastTips)
			itemCoding, cnt = itemsMgr.item
			if itemCoding in ItemDict :
				cnt += ItemDict[itemCoding]
			ItemDict[itemCoding] = cnt
		tips = GlobalPrompt.Reward_Tips
		for item, cnt in ItemDict.iteritems():
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
		role.Msg(2, 0, tips)

#高级攻击
def SpecialFightNianShou(role, counts):
	global IsStart
	if not IsStart :
		return
	if counts not in (1, 10) :
		return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	#神石不足
	if role.GetUnbindRMB() < CostRmb*counts :
		return
	RoleLevel = role.GetLevel()
	RangeId = 0
	for cf in PassionNianShouConfig.NianShouReward.itervalues() :
		if cf.levelRange[0] <= RoleLevel <= cf.levelRange[1] and cf.rewardType == 2:
			RangeId = cf.rangeId
			break
	if not RangeId :
		print "GE_EXC, repeat no Level %s in NormalFightNianShou" % RoleLevel
		return
	NianShouRange = PassionNianShouConfig.NianShou_Reward_Random.get(RangeId)
	if not NianShouRange :
		print "GE_EXC, repeat no RangeId %s in NormalFightNianShou" % RangeId
		return
	ItemDict = {}
	#发奖励
	with Tra_NianShou_Special :
		role.DecUnbindRMB(CostRmb*counts)
		for _ in range(counts) :
			isBroadcastTips = ""
			RewardId = NianShouRange.RandomOne()
			itemsMgr = PassionNianShouConfig.NianShouReward.get(RewardId)
			itemCoding, cnt = itemsMgr.item
			if itemsMgr.isBroadcast :
				isBroadcastTips += GlobalPrompt.PassionDaNianShouTip % (role.GetRoleName(),itemCoding, cnt)
				role.Msg(11, 0, isBroadcastTips)
			if itemCoding in ItemDict :
				cnt += ItemDict[itemCoding]
			ItemDict[itemCoding] = cnt
		tips = GlobalPrompt.Reward_Tips
		for item, cnt in ItemDict.iteritems():
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
		role.Msg(2, 0, tips)


def PassionNianShou_ExtendReward(role, param):
	'''
	副本和英灵神殿 通关活动期间概率获得烈焰火把
	'''
	global IsStart
	if not IsStart:
		return None
	
	activityType, idx = param	
	cfg = PassionNianShouConfig.NianShou_Item_Drop.get((activityType, idx))
	if not cfg:
		return None
	
	rewardDict = {}
	#烈焰火把掉落
	if random.randint(1, 10000) <= cfg.dropRate:
		rewardDict[cfg.proCoding] = 1
	
	return rewardDict

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenActive)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseActive)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionNianShouNormalFight", "春节打神兽普通攻击"), NormalFightNianShou)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionNianShouSpecialFight", "春节打神兽高级攻击"), SpecialFightNianShou)
