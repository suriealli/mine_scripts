#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.ZaiXianLuxuryRewardConfig")
#===============================================================================
# 在线有豪礼 Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("WangZheGongCe")
	
	ZXLR_RewardRandomObj_Dict = {}		#在线有豪礼_抽奖奖励池   {levelRangeId:{rewardIndex:randomObj,},}
	ZXLR_Range2ID_Dict = {}				#在线有豪礼_等级段ID & 等级关联  {levelRangeId:levelRange,}
	ZXLR_Unlock_Dict = {}				#在线有豪礼_奖励解锁配置{rewardIndex:needZaiXianMins,}
	ZXLR_MAX_REWARDINDEX = 0			#在线有豪礼_最大奖励索引

class ZaiXianLuxuryReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ZaiXianLuxuryReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needZaiXianMins = int
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		self.rewardItems = self.GetEvalByString

def GetRandomObjByLevelAndIndex(roleLevel, rewardIndex):
	'''
	返回对应roleLevel 和 rewardIndex 的抽奖随机器
	'''
	tmpLevelRangeId = GetLevelRangeIdByLevel(roleLevel)
	levelRangeIdDict = ZXLR_RewardRandomObj_Dict.get(tmpLevelRangeId)
	if not levelRangeIdDict:
		return None
	
	return levelRangeIdDict.get(rewardIndex, None)
	
def GetNeedOnLineMinsByIndex(rewardIndex):
	'''
	返回ewardIndex下一轮抽奖需要在线时长
	'''
	return ZXLR_Unlock_Dict.get(rewardIndex, None)

def GetLevelRangeIdByLevel(roleLevel):
	'''
	返回 对应 roleLevel 的等级段ID
	'''
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in ZXLR_Range2ID_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	return tmpLevelRangeId

def LoadZaiXianLuxuryReward():
	global ZXLR_MAX_REWARDINDEX
	global ZXLR_Unlock_Dict
	global ZXLR_Range2ID_Dict
	global ZXLR_RewardRandomObj_Dict
	for cfg in ZaiXianLuxuryReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		needZaiXianMins = cfg.needZaiXianMins
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		
		#最大奖励索引
		if rewardIndex > ZXLR_MAX_REWARDINDEX:
			ZXLR_MAX_REWARDINDEX = rewardIndex
		
		#解锁关联
		ZXLR_Unlock_Dict[rewardIndex] = needZaiXianMins
		
		#等级关联
		ZXLR_Range2ID_Dict[levelRangeId] = levelRange
		
		#抽奖随机器
		levelRangeIdDict = ZXLR_RewardRandomObj_Dict.setdefault(levelRangeId, {})
		randomObj = levelRangeIdDict.setdefault(rewardIndex, Random.RandomRate())
		for itemIndex, coding, cnt, rateValue in cfg.rewardItems:
			randomObj.AddRandomItem(rateValue, (itemIndex, coding, cnt))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadZaiXianLuxuryReward()