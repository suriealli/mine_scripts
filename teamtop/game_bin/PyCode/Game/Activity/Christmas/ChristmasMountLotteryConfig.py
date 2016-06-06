#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasMountLotteryConfig")
#===============================================================================
# 圣诞坐骑转转乐Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Christmas")
	
	ChristmasMountLottery_LotteryReward_Dict = {}	#圣诞坐骑转转乐奖励池{rangeId:{rewardId:rewardCfg,},}
	ChristmasMountLottery_Range2ID_Dict = {}		#圣诞坐骑转转乐等级区段关联区段ID{rangeId:levelRange,}
	ChristmasMountLottery_RandomObj_Dict = {}		#圣诞坐骑转转乐抽奖随机器{rangeId:randomObj,} randomList->[rate,(rewardId, itemIndex, coding, cnt, isPrecious)]

class ChristmasMountLotteryReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ChristmasMountLotteryReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.itemIndex = int
		self.item = self.GetEvalByString
		self.isPrecious = int
		self.rateValue = int
		
def LoadChristmasMountLotteryReward():
	global ChristmasMountLottery_LotteryReward_Dict
	global ChristmasMountLottery_Range2ID_Dict
	global ChristmasMountLottery_RandomObj_Dict
	for cfg in ChristmasMountLotteryReward.ToClassType():
		rewardId = cfg.rewardId
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		itemIndex = cfg.itemIndex
		coding, cnt = cfg.item
		isPrecious = cfg.isPrecious
		rateValue = cfg.rateValue
		#等级区段关联区段ID
		ChristmasMountLottery_Range2ID_Dict[rangeId] = levelRange
		#奖励池
		rewardDict = ChristmasMountLottery_LotteryReward_Dict.setdefault(rangeId, {})
		if rewardId in rewardDict:
			print "GE_EXC, repeat rewardId(%s) in ChristmasMountLottery_LotteryReward_Dict" % rewardId
		rewardDict[rewardId] = cfg
		#抽奖随机器
		randomObj = ChristmasMountLottery_RandomObj_Dict.setdefault(rangeId, Random.RandomRate())
		randomObj.AddRandomItem(rateValue, (rewardId, itemIndex, coding, cnt, isPrecious))

def GetRandomObjByLevel(roleLevel):
	'''
	返回roleLevel对应的抽奖随机器
	'''
	tmpRangeId = 1
	for rangeId, levelRange in ChristmasMountLottery_Range2ID_Dict.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel and roleLevel <= levelUp:
			break
	
	randomObj = ChristmasMountLottery_RandomObj_Dict.get(tmpRangeId)
	if not randomObj:
		print "GE_EXC,ChristmasMountLottery::GetRandomObjByLevel:: can not get randomObj by roleLevel(%s) " % roleLevel
		return None
	
	return randomObj

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadChristmasMountLotteryReward()