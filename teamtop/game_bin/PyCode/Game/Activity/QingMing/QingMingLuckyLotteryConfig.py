#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QingMingLuckyLotteryConfig")
#===============================================================================
# 清明幸运大轮盘 config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QingMing")
	
	QingMingLuckyLottery_LotteryReward_Dict = {}	#幸运大轮盘奖励池{rangeId:{rewardId:rewardCfg,},}
	QingMingLuckyLottery_Range2ID_Dict = {}			#幸运大轮盘等级区段关联区段ID{rangeId:levelRange,}
	QingMingLuckyLottery_RandomObj_Dict = {}		#幸运大轮盘抽奖随机器{rangeId:randomObj,} randomList->[rate,(rewardId, itemIndex, coding, cnt, isPrecious)]

class QingMingLuckyLotteryReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingLuckyLotteryReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.itemIndex = int
		self.item = self.GetEvalByString
		self.isPrecious = int
		self.rateValue = int
		
def LoadQingMingLuckyLotteryReward():
	global QingMingLuckyLottery_LotteryReward_Dict
	global QingMingLuckyLottery_Range2ID_Dict
	global QingMingLuckyLottery_RandomObj_Dict
	for cfg in QingMingLuckyLotteryReward.ToClassType():
		rewardId = cfg.rewardId
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		itemIndex = cfg.itemIndex
		coding, cnt = cfg.item
		isPrecious = cfg.isPrecious
		rateValue = cfg.rateValue
		#等级区段关联区段ID
		QingMingLuckyLottery_Range2ID_Dict[rangeId] = levelRange
		#奖励池
		rewardDict = QingMingLuckyLottery_LotteryReward_Dict.setdefault(rangeId, {})
		if rewardId in rewardDict:
			print "GE_EXC, repeat rewardId(%s) in QingMingLuckyLottery_LotteryReward_Dict" % rewardId
		rewardDict[rewardId] = cfg
		#抽奖随机器
		randomObj = QingMingLuckyLottery_RandomObj_Dict.setdefault(rangeId, Random.RandomRate())
		randomObj.AddRandomItem(rateValue, (rewardId, itemIndex, coding, cnt, isPrecious))

def GetRandomObjByLevel(roleLevel):
	'''
	返回roleLevel对应的抽奖随机器
	'''
	tmpRangeId = 1
	for rangeId, levelRange in QingMingLuckyLottery_Range2ID_Dict.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel and roleLevel <= levelUp:
			break
	
	randomObj = QingMingLuckyLottery_RandomObj_Dict.get(tmpRangeId)
	if not randomObj:
		return None
	else:
		return randomObj

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQingMingLuckyLotteryReward()
