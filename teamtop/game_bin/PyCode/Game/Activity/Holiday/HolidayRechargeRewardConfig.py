#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Holiday.HolidayRechargeRewardConfig")
#===============================================================================
# 元旦充值奖励Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Holiday")
	
	Holiday_LotteryReward_Config_Dict = {}		#元旦充值抽奖奖励{rangeId:{rewardId:cfg,},}
	Holiday_LotteryReward_Range2ID_dict = {}	#元旦充值抽奖奖励等级区段对应等级区段ID关联{rangeId:levelRange,}
	Holiday_LotteryReward_RandomObj_Dict = {}	#元旦充值抽奖奖励抽奖随机器{rangeId:randomObj,} randomList->[(rate,(rewardId, coding, cnt, isPrecious))]
	
	Holiday_RechargeReward_Config_Dict = {}		#元旦重置兑换抽奖次数配置{rewardIndex:cfg,}

class HolidayLotteryReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HolidayLotteryReward.txt")
	def __init__(self):
		self.rewardId = int 
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.item = self.GetEvalByString
		self.rateValue = int
		self.isPrecious = int

class HolidayRechargeReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HolidayRechargeReward.txt")
	def __init__(self):
		self.rewardIndex = int 
		self.needRechargeRMB = int
		self.rewardLotteryTimes = int

def LoadHolidayLotteryReward():
	global Holiday_LotteryReward_Config_Dict
	global Holiday_LotteryReward_Range2ID_dict
	global Holiday_LotteryReward_RandomObj_Dict
	for cfg in HolidayLotteryReward.ToClassType():
		rewardId = cfg.rewardId
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		coding, cnt = cfg.item
		rateValue = cfg.rateValue
		isPrecious = cfg.isPrecious
		
		#区段ID关联
		Holiday_LotteryReward_Range2ID_dict[rangeId] = levelRange
		#配置base
		rewardDict = Holiday_LotteryReward_Config_Dict.setdefault(rangeId, {})
		if rewardId in rewardDict:
			print "GE_EXC,repeat rewardId(%s) in Holiday_LotteryReward_Config_Dict" % rewardId
		rewardDict[rewardId] = cfg
		#抽奖随机器
		if rangeId not in Holiday_LotteryReward_RandomObj_Dict:
			Holiday_LotteryReward_RandomObj_Dict[rangeId] = Random.RandomRate()
		randomObj = Holiday_LotteryReward_RandomObj_Dict[rangeId]
		randomObj.AddRandomItem(rateValue, (rewardId, coding, cnt, isPrecious))	

def LoadHolidayRechargeReward():
	global Holiday_RechargeReward_Config_Dict
	for cfg in HolidayRechargeReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in Holiday_RechargeReward_Config_Dict:
			print "GE_EXC, repeat rewardIndex(%s) in Holiday_RechargeReward_Config_Dict" % rewardIndex
		Holiday_RechargeReward_Config_Dict[rewardIndex] = cfg

def GetRandomObjByLevel(roleLevel):
	'''
	返回roleLevel对应等级的抽奖随机器
	'''
	tmpRangeId = 1	
	for rangeId, levelRange in Holiday_LotteryReward_Range2ID_dict.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown < roleLevel and roleLevel < levelUp:
			break 
	
	randomObj = Holiday_LotteryReward_RandomObj_Dict.get(tmpRangeId)
	if not randomObj:
		print "GE_EXC, can not get randomObj by roleLevel(%s) to rangeId(%s)" % (roleLevel, tmpRangeId)
		return None
	
	return randomObj

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadHolidayLotteryReward()
		LoadHolidayRechargeReward()