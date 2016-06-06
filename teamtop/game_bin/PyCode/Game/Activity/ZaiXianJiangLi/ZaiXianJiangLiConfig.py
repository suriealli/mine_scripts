#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZaiXianJiangLi.ZaiXianJiangLiConfig")
#===============================================================================
# 新在线奖励 config
#===============================================================================
from Util.File import TabFile
import DynamicPath
from Util import Random
import Environment

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ZaiXianJiangLi")
	
	ZXJL_RewardRandomObj_Dict = {}		#新在线奖励_抽奖奖励池   {levelRangeId:randomObj,}
	ZXJL_Range2ID_Dict = {}				#新在线奖励_等级段ID & 等级关联  {levelRangeId:levelRange,}

class ZaiXianJiangLiReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ZaiXianJiangLiReward.txt")
	def __init__(self):
		self.rewardId = int
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		self.rewardIndex = int
		self.rewardItem = self.GetEvalByString
		self.rateValue = int
		self.isPrecious = int

def GetRandomObjByLevel(roleLevel):
	'''
	返回对应roleLevel 的抽奖随机器
	'''
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in ZXJL_Range2ID_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	if tmpLevelRangeId in ZXJL_RewardRandomObj_Dict:
		return ZXJL_RewardRandomObj_Dict[tmpLevelRangeId]
	else:
		return None

def LoadZaiXianJiangLiReward():
	global ZXJL_Range2ID_Dict
	global ZXJL_RewardRandomObj_Dict
	for cfg in ZaiXianJiangLiReward.ToClassType():
		rewardId = cfg.rewardId
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		rewardIndex = cfg.rewardIndex
		coding, cnt = cfg.rewardItem
		rateValue = cfg.rateValue
		isPrecious = cfg.isPrecious
		
		#关联
		ZXJL_Range2ID_Dict[levelRangeId] = levelRange
		
		#抽奖随机器
		randomObj = ZXJL_RewardRandomObj_Dict.setdefault(levelRangeId, Random.RandomRate())
		randomObj.AddRandomItem(rateValue, (rewardId, rewardIndex, coding, cnt, isPrecious))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadZaiXianJiangLiReward()
