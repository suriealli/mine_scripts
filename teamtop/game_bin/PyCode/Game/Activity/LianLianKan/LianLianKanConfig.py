#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LianLianKan.LianLianKanConfig")
#===============================================================================
# 连连看配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("LianLianKan")
	
	LianLianKan_Reward = {}
	LevelRange_Dict = {}
	LianLianKan_BuyDict = {}
	
class LianLianKanReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LianLianKanReward.txt")
	def __init__(self):
		self.rewardId = int
		self.levelRange = self.GetEvalByString
		self.rewardItems = self.GetEvalByString
		self.pro = int
		self.IsMsg = int
		
class LianLianKanBuy(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LianLianKanBuy.txt")
	def __init__(self):
		self.buyTimes = int
		self.cost = int
		
def LoadLianLianKanReward():
	global LianLianKan_Reward
	global LevelRange_Dict
	
	levelRange_List = {}
	for cfg in LianLianKanReward.ToClassType():
		if cfg.rewardId in LianLianKan_Reward:
			print "GE_EXC,repeat rewardId(%s) in LoadLianLianKanReward" % cfg.rewardId
		LianLianKan_Reward[cfg.rewardId] = cfg
		if cfg.levelRange not in levelRange_List:
			levelRange_List[cfg.levelRange] = set()
		levelRange_List[cfg.levelRange].add((cfg.rewardId, cfg.pro))
	for levelRange, rewardList in levelRange_List.iteritems():
		RandomRange = Random.RandomRate()
		for rewardId, pro in rewardList:
			RandomRange.AddRandomItem(pro, rewardId)
		LevelRange_Dict[levelRange] = RandomRange
		
def GetRewardIdsByLevel(level):
	global LevelRange_Dict
	for (minLevel,maxLevel),RandomRange in LevelRange_Dict.iteritems():
		if minLevel <= level <= maxLevel:
			return RandomRange.RandomMany(3)
	return None

def LoadLianLianKanBuy():
	global LianLianKan_BuyDict
	for cfg in LianLianKanBuy.ToClassType():
		if cfg.buyTimes in LianLianKan_BuyDict:
			print "GE_EXC,repeat buyTimes(%s) in LoadLianLianKanBuy"
		LianLianKan_BuyDict[cfg.buyTimes] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLianLianKanReward()
		LoadLianLianKanBuy()