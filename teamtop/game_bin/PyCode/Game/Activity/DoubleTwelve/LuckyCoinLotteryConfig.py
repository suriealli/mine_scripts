#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.LuckyCoinLotteryConfig")
#===============================================================================
# 好运币专场配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DoubleTwelve")
	
	LuckyCoinLottery_MaxLotteryCost = 0
	LuckyCoinLottery_LotteryCostConfig_Dict = {}		#抽奖消耗好运币配置{lotteryTime:needLuckyCoin,}
	
	LuckyCoinLottery_LotteryRewardConfig_Dict = {}		#奖励池配置{rangeId:{rewardId:cfg,},}
	LuckyCoinLottery_LotteryRewardRange2Id_Dict = {}	#等级区段ID对应等级区段关联 {rangeId:LevelRange,}
	
	LuckyCoinLottery_MaxResetCost = 0
	LuckyCoinLottery_ResetTimesCost_Dict = {}			#重置转盘神石消耗配置	{resetTime:needUnbindRMB,}

class LCLotteryCost(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LCLotteryCost.txt")
	def __init__(self):
		self.lotteryTime = int 
		self.needLuckyCoin = int
		
class LCLotteryReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LCLotteryReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.rewardIndex = int
		self.rewardItem = self.GetEvalByString
		self.isPrecious = int
		self.rateValue = int

class LCResetTimesCost(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LCResetTimesCost.txt")
	def __init__(self):
		self.resetNum = int
		self.needUnbindRMB = int

def LoadLCLotteryCost():
	global LuckyCoinLottery_MaxLotteryCost
	global LuckyCoinLottery_LotteryCostConfig_Dict
	for cfg in LCLotteryCost.ToClassType():
		if cfg.lotteryTime in LuckyCoinLottery_LotteryCostConfig_Dict:
			print "GE_EXC, repeat lotteryTime(%s) in LCLotteryCost" % cfg.lotteryTime
		LuckyCoinLottery_LotteryCostConfig_Dict[cfg.lotteryTime] = cfg.needLuckyCoin
		if cfg.needLuckyCoin > LuckyCoinLottery_MaxLotteryCost:
			LuckyCoinLottery_MaxLotteryCost = cfg.needLuckyCoin

def LoadLCLotteryReward():
	global LuckyCoinLottery_LotteryRewardConfig_Dict
	global LuckyCoinLottery_LotteryRewardRange2Id_Dict
	global LuckyCoinLottery_LotteryRewardRandomObj_Dict
	for cfg in LCLotteryReward.ToClassType():
		rewardId = cfg.rewardId
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		#等级区段ID和等级区段关联
		LuckyCoinLottery_LotteryRewardRange2Id_Dict[rangeId] = levelRange
		
		rangeIdCfgDict = LuckyCoinLottery_LotteryRewardConfig_Dict.setdefault(rangeId, {})
		if rewardId in rangeIdCfgDict:
			print "GE_EXC, repeat rewardIndex(%s) in LCLotteryReward of rangeId(%s) " % (rewardId, rangeId)
		rangeIdCfgDict[rewardId] = cfg
		
def LoadLCResetTimesCost():
	global LuckyCoinLottery_MaxResetCost
	global LuckyCoinLottery_ResetTimesCost_Dict
	for cfg in LCResetTimesCost.ToClassType():
		if cfg.resetNum in LuckyCoinLottery_ResetTimesCost_Dict:
			print "GE_EXC,repeat resetTime(%s) in LCResetTimesCost" % cfg.resetNum
		LuckyCoinLottery_ResetTimesCost_Dict[cfg.resetNum] = cfg.needUnbindRMB
		if LuckyCoinLottery_MaxResetCost < cfg.needUnbindRMB:
			LuckyCoinLottery_MaxResetCost = cfg.needUnbindRMB

def GetRangeIdByLevel(roleLevel):
	'''
	根据玩家等级获取对应等级区段ID
	'''
	tmpRangeId = 1
	for rangeId, levelRange in LuckyCoinLottery_LotteryRewardRange2Id_Dict.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown < roleLevel and roleLevel < levelUp:
			break
		
	return tmpRangeId

def GetCostByLotteryTimes(lotteryTimes):
	'''
	根据抽奖次数获取需要好运币数量
	若次数对应不存在 返回配置最大需要
	'''
	needLuckyCoin = LuckyCoinLottery_LotteryCostConfig_Dict.get(lotteryTimes)
	if not needLuckyCoin:
		needLuckyCoin = LuckyCoinLottery_MaxLotteryCost
	
	return needLuckyCoin
		
def GetResetCostByResetTimes(resetTimes):
	'''
	获取对应重置次数的神石消耗
	若次数对应配置不存在 返回配置最大消耗
	'''
	needUnbindRMB = LuckyCoinLottery_ResetTimesCost_Dict.get(resetTimes)
	if not needUnbindRMB:
		needUnbindRMB = LuckyCoinLottery_MaxResetCost
	
	return needUnbindRMB

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadLCLotteryCost()
		LoadLCLotteryReward()
		LoadLCResetTimesCost()