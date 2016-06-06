#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GuBaoTanMi.GuBaoTanMiConfig")
#===============================================================================
# 古堡探秘 Config
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("GuBaoTanMi")
	
	#古堡探秘 等级段配置 {levelRangeId:LevelRange,}
	GuBaoTanMi_LevelRangeConfig_Dict = {}
	#古堡探秘 抽奖随机器 {levelRangeId:randomObj,}
	GuBaoTanMi_RandomObj_Dict = {}
	#古堡探秘 特殊宝箱配置 {levelRangeId:{rewardIndex:cfg,},}
	GuBaoTanMi_SpeciousReward_Dict = {}
	#古堡探秘 累计探秘解锁奖励配置 {rewardIndex:cfg,}
	GuBaoTanMi_UnlockReward_Dict = {}
	

class GuBaoTanMiLevelRange(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("GuBaoTanMiLevelRange.txt")
	def __init__(self):
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
	

def LoadGuBaoTanMiLevelRange():
	global GuBaoTanMi_LevelRangeConfig_Dict
	for cfg in GuBaoTanMiLevelRange.ToClassType():
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		if levelRangeId in GuBaoTanMi_LevelRangeConfig_Dict:
			print "GE_EXC,repeat levelRangeId(%s) in GuBaoTanMi_LevelRangeConfig_Dict" % levelRangeId
		
		GuBaoTanMi_LevelRangeConfig_Dict[levelRangeId] = levelRange

def GetLevelRangeIdByLevel(roleLevel):
	'''
	返回对应 roleLevel 的等级段ID
	'''
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in GuBaoTanMi_LevelRangeConfig_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	return tmpLevelRangeId
		

class GuBaoTanMiRewardPool(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("GuBaoTanMiRewardPool.txt")
	def __init__(self):
		self.rewardId = int
		self.levelRangeId = int
		self.rewardItem = self.GetEvalByString
		self.rateValue = int
		self.isPrecious = int
		

def LoadGuBaoTanMiRewardPool():
	global GuBaoTanMi_RandomObj_Dict
	for cfg in GuBaoTanMiRewardPool.ToClassType():
		rewardId = cfg.rewardId
		levelRangeId = cfg.levelRangeId
		coding, cnt = cfg.rewardItem
		rateValue = cfg.rateValue
		isPrecious = cfg.isPrecious
		
		randomObj = GuBaoTanMi_RandomObj_Dict.setdefault(levelRangeId, Random.RandomRate())
		randomObj.AddRandomItem(rateValue, [rewardId, coding, cnt, isPrecious])

def GetRandomObjByLevel(roleLevel):
	'''
	返回对应 roleLevel 的抽奖随机器
	'''
	levelRangeId = GetLevelRangeIdByLevel(roleLevel)
	if levelRangeId in GuBaoTanMi_RandomObj_Dict:
		return GuBaoTanMi_RandomObj_Dict[levelRangeId]
	else:
		return None
	
	
class GuBaoTanMiSpecialReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("GuBaoTanMiSpecialReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.levelRangeId = int
		self.needItem = self.GetEvalByString
		self.rewardItem = self.GetEvalByString
		self.needItemName = str


def LoadGuBaoTanMiSpecialReward():
	global GuBaoTanMi_SpeciousReward_Dict
	for cfg in GuBaoTanMiSpecialReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		levelRangeId = cfg.levelRangeId
		levelRangeIdDict = GuBaoTanMi_SpeciousReward_Dict.setdefault(levelRangeId, {})
		if rewardIndex in levelRangeIdDict:
			print "GE_EXC, repeat rewardIndex(%s) in GuBaoTanMi_SpeciousReward_Dict with levelRangeId(%s)" % (rewardIndex, levelRangeId)
		levelRangeIdDict[rewardIndex] = cfg

def GetSRCfgByLevelAndIndex(roleLevel, rewardIndex):
	'''
	返回对应 roleLevel下 奖励索引为  rewardIndex 的配置
	'''
	levelRangeId = GetLevelRangeIdByLevel(roleLevel)
	levelRangeIdDict = GuBaoTanMi_SpeciousReward_Dict.get(levelRangeId, {})
	if rewardIndex in levelRangeIdDict:
		return levelRangeIdDict[rewardIndex]
	else:
		return None


class GuBaoTanMiUnlockReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("GuBaoTanMiUnlockReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needTanMiCnt = int
		self.rewardItems = self.GetEvalByString
		

def LoadGuBaoTanMiUnlockReward():
	global GuBaoTanMi_UnlockReward_Dict
	for cfg in GuBaoTanMiUnlockReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in GuBaoTanMi_UnlockReward_Dict:
			print "GE_EXc, repeat rewardIndex(%s) in GuBaoTanMi_UnlockReward_Dict" % rewardIndex
		GuBaoTanMi_UnlockReward_Dict[rewardIndex] = cfg

def GetUnlockRewardByIndex(rewardIndex):
	'''
	返回对应奖励索引为 rewardIndex 的配置
	'''	
	if rewardIndex in GuBaoTanMi_UnlockReward_Dict:
		return GuBaoTanMi_UnlockReward_Dict[rewardIndex]
	else:
		return None

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadGuBaoTanMiLevelRange()
		LoadGuBaoTanMiRewardPool()
		LoadGuBaoTanMiSpecialReward()
		LoadGuBaoTanMiUnlockReward()
		

