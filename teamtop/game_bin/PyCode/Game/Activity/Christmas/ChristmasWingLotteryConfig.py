#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasWingLotteryConfig")
#===============================================================================
# 圣诞羽翼转转乐Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Christmas")
	
	ChristmasWingLottery_LotteryReward_Dict = {}	#羽翼转转乐奖励池{rangeId:{rewardId:rewardCfg,},}
	ChristmasWingLottery_Range2ID_Dict = {}			#羽翼转转乐等级区段关联区段ID{rangeId:levelRange,}
	ChristmasWingLottery_RandomObj_Dict = {}		#羽翼转转乐抽奖随机器{rangeId:randomObj,} randomList->[rate,(rewardId, itemIndex, coding, cnt, isPrecious)]

class ChristmasWingLotteryReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ChristmasWingLotteryReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.itemIndex = int
		self.item = self.GetEvalByString
		self.isPrecious = int
		self.rateValue = int
		
def LoadChristmasWingLotteryReward():
	global ChristmasWingLottery_LotteryReward_Dict
	global ChristmasWingLottery_Range2ID_Dict
	global ChristmasWingLottery_RandomObj_Dict
	for cfg in ChristmasWingLotteryReward.ToClassType():
		rewardId = cfg.rewardId
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		itemIndex = cfg.itemIndex
		coding, cnt = cfg.item
		isPrecious = cfg.isPrecious
		rateValue = cfg.rateValue
		#等级区段关联区段ID
		ChristmasWingLottery_Range2ID_Dict[rangeId] = levelRange
		#奖励池
		rewardDict = ChristmasWingLottery_LotteryReward_Dict.setdefault(rangeId, {})
		if rewardId in rewardDict:
			print "GE_EXC, repeat rewardId(%s) in ChristmasWingLottery_LotteryReward_Dict" % rewardId
		rewardDict[rewardId] = cfg
		#抽奖随机器
		randomObj = ChristmasWingLottery_RandomObj_Dict.setdefault(rangeId, Random.RandomRate())
		randomObj.AddRandomItem(rateValue, (rewardId, itemIndex, coding, cnt, isPrecious))

def GetRandomObjByLevel(roleLevel):
	'''
	返回roleLevel对应的抽奖随机器
	'''
	tmpRangeId = 1
	for rangeId, levelRange in ChristmasWingLottery_Range2ID_Dict.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel and roleLevel <= levelUp:
			break
	
	randomObj = ChristmasWingLottery_RandomObj_Dict.get(tmpRangeId)
	if not randomObj:
		print "GE_EXC,ChristmasWingLottery::GetRandomObjByLevel:: can not get randomObj by roleLevel(%s) " % roleLevel
		return None
	
	return randomObj

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadChristmasWingLotteryReward()