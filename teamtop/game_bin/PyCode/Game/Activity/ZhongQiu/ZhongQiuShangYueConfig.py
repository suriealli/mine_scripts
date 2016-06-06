#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZhongQiu.ZhongQiuShangYueConfig")
#===============================================================================
# 中秋赏月 config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ZhongQiu")
	
	#中秋奖励套ID集合 set([rewardSuitId1,])
	ZhongQiuShangYue_RewardSuit_Set = set()
	
	#中秋赏月基本配置 {rewardId:cfg,}
	ZhongQiuShangYue_BaseConfig_Dict = {}
	
	#中秋赏月道具抽奖奖励池 {levelRangeId:randomObj,}
	ZhongQiuShangYue_ItemRewardPool_Dict = {}
	
	#中秋赏月神石抽奖奖励池 {levelRangeId:{rewardSuitId:randomObj,},}
	ZhongQiuShangYue_RMBRewardPool_Dict = {}
	
	#中秋赏月等级段配置 {levelRangeId:levelRange,}
	ZhongQiuShangYue_LevelRange_Dict = {}


class ZhongQiuLevelRange(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ZhongQiuLevelRange.txt")
	def __init__(self):
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		
	
def LoadZhongQiuLevelRange():
	global ZhongQiuShangYue_LevelRange_Dict	
	for cfg in ZhongQiuLevelRange.ToClassType():
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		if levelRangeId in ZhongQiuShangYue_LevelRange_Dict:
			print "GE_EXC, repeat levelRangeId(%d) in ZhongQiuShangYue_LevelRange_Dict" % levelRangeId
		ZhongQiuShangYue_LevelRange_Dict[levelRangeId] = levelRange
	
	
def GetLevelRangeIdByLevel(roleLevel):
	'''
	返回对应 roleLevel 的等级段ID
	'''
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in ZhongQiuShangYue_LevelRange_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	return tmpLevelRangeId


class ZhongQiuShangYueReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ZhongQiuShangYueReward.txt")
	def __init__(self):
		self.rewardId = int
		self.levelRangeId = int
		self.rewardSuitId = int
		self.rewardItem = self.GetEvalByString
		self.rateValue = int
		self.isPrecious = int
		self.isBroad = int
		

def LoadZhongQiuShangYueReward():
	global ZhongQiuShangYue_ItemRewardPool_Dict
	global ZhongQiuShangYue_RMBRewardPool_Dict
	global ZhongQiuShangYue_BaseConfig_Dict
	global ZhongQiuShangYue_RewardSuit_Set
	for cfg in ZhongQiuShangYueReward.ToClassType():
		rewardId = cfg.rewardId
		levelRangeId = cfg.levelRangeId
		rewardSuitId = cfg.rewardSuitId
		coding, cnt = cfg.rewardItem
		rateValue = cfg.rateValue
		isPrecious = cfg.isPrecious
		isBroad = cfg.isBroad
		rewardInfo = [rewardId, coding, cnt, isPrecious,isBroad]
		
		if rewardId in ZhongQiuShangYue_BaseConfig_Dict:
			print "GE_EXC, repeat rewardId(%s) in ZhongQiuShangYue_BaseConfig_Dict" % rewardId
		ZhongQiuShangYue_BaseConfig_Dict[rewardId] = cfg
		
		if rewardSuitId == 0:
			#道具抽奖奖励池
			ItemLevelRangeRandomObj = ZhongQiuShangYue_ItemRewardPool_Dict.setdefault(levelRangeId, Random.RandomRate())
			ItemLevelRangeRandomObj.AddRandomItem(rateValue, rewardInfo)
		else:
			#记录所有非零奖励套ID
			ZhongQiuShangYue_RewardSuit_Set.add(rewardSuitId)
			#神石抽奖奖励池
			RMBSuitRandomObjDict = ZhongQiuShangYue_RMBRewardPool_Dict.setdefault(levelRangeId, {})
			RMBSuitRandomObj = RMBSuitRandomObjDict.setdefault(rewardSuitId, Random.RandomRate())
			RMBSuitRandomObj.AddRandomItem(rateValue, rewardInfo)

def GetRewardRandomObj(lotteryType, roleLevel, rewardSuitId = 0):
	'''
	根据抽奖方式 返回角色此次抽奖的奖励随机器
	@param lotteryType:抽奖方式 0-道具抽奖 1-神石抽奖 
	'''
	if lotteryType == 1 and not rewardSuitId:
		print "GE_EXC, GetRewardRandomObj lotteryType == 1 and not rewardSuitId"
		return None
	
	randomObj = None
	tlevelRangeId = GetLevelRangeIdByLevel(roleLevel)
	if lotteryType == 0:
		randomObj = ZhongQiuShangYue_ItemRewardPool_Dict.get(tlevelRangeId, None)
	elif lotteryType == 1:
		tRMBSuitRandomObjDict = ZhongQiuShangYue_RMBRewardPool_Dict.get(tlevelRangeId, None)
		randomObj = tRMBSuitRandomObjDict.get(rewardSuitId, None)
	else:
		return None
	
	return randomObj
		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadZhongQiuLevelRange()
		LoadZhongQiuShangYueReward()