#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.RosePresentConfig")
#===============================================================================
# 送人玫瑰Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ValentineDay")
	
	RosePresent_BaseConfig_Dict = {}		#送人玫瑰基本配置 {roseType:cfg,}
	RosePresent_LotteryRange2ID_Dict = {}	#返利抽奖等级段-等级段ID关联 {rangeId:levelRange,}
	RosePresent_LotteryRandomObj_Dict = {}	#送人玫瑰抽奖随机器配置{roseType:{rangeId:randomObj},} randomeList->[ratevalue,(rewardId, rewardType, coding, cnt, isPrecious)]
	RosePresent_RoseDropConfig_Dict = {}	#副本 & 英灵神殿 掉落龙币配置

class RosePresentBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("RosePresentBase.txt")
	def __init__(self):
		self.roseType = int				
		self.needCoding = int
		self.needMoney = int
		self.rewardLotteryTime = int
		self.lotteryTimeType = int
		self.rewardSendGlamour = int
		self.rewardReceiverGlamour = int

class RosePresentLottery(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("RosePresentLottery.txt")
	def __init__(self):
		self.rewardId = int
		self.rewardType = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.rewardItem = self.GetEvalByString
		self.isPrecious = int
		self.rateValue = int

def GetRandomObjByTypeAndLevel(rewardType, roleLevel):
	'''
	根据 类型 和角色等级 获取对应奖励随机器
	'''
	tmpRangeId = 1
	for rangeId, levelRange in RosePresent_LotteryRange2ID_Dict.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel <= levelUp:
			break
		
	randomObjDict = RosePresent_LotteryRandomObj_Dict.get(rewardType)
	if not randomObjDict:
		return None
	
	randomObj = randomObjDict.get(tmpRangeId, None)
	if not randomObj:
		return None
	
	return randomObj

class RoseDrop(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("RoseDrop.txt")
	def __init__(self):
		self.activityType = int 
		self.fightIdx = int 
		self.dropRate = int 
		self.proCoding = int

def LoadRosePresentBase():
	global RosePresent_BaseConfig_Dict
	for cfg in RosePresentBase.ToClassType():
		roseType = cfg.roseType
		if roseType in RosePresent_BaseConfig_Dict:
			print "GE_EXC,repeat roesType(%s) in RosePresent_BaseConfig_Dict" % roseType
		RosePresent_BaseConfig_Dict[roseType] = cfg
	
def LoadRosePresentLottery():
	global RosePresent_LotteryRange2ID_Dict
	global RosePresent_LotteryRandomObj_Dict
	for cfg in RosePresentLottery.ToClassType():
		rewardId = cfg.rewardId
		rewardType = cfg.rewardType
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		coding, cnt = cfg.rewardItem
		isPrecious = cfg.isPrecious
		rateValue = cfg. rateValue
		
		if rangeId not in RosePresent_LotteryRange2ID_Dict:
			RosePresent_LotteryRange2ID_Dict[rangeId] =  levelRange
		
		randomObjDict = RosePresent_LotteryRandomObj_Dict.setdefault(rewardType, {})

		randomObj = randomObjDict.setdefault(rangeId, Random.RandomRate())
		randomObj.AddRandomItem(rateValue,(rewardId, rewardType, coding, cnt, isPrecious))
	
def LoadRoseDrop():
	global RosePresent_RoseDropConfig_Dict
	for cfg in RoseDrop.ToClassType():
		RosePresent_RoseDropConfig_Dict[(cfg.activityType, cfg.fightIdx)] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadRosePresentBase()
		LoadRosePresentLottery()
		LoadRoseDrop()