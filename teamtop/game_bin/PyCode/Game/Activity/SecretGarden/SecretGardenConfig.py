#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SecretGarden.SecretGardenConfig")
#===============================================================================
# 秘密花园 Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("SecretGarden")
	
	
	#抽奖奖励池 {rewardId:cfg,}
	SecretGarden_RewardPool_Dict = {}
	
	#抽奖控制随机器 {levelRangeId:cfg,}
	SecretGarden_Lottery_Dict = {}
	
	#幸运果实配置 {rewardIndex:cfg,}
	SecretGarden_LuckyReward_Dict = {}
	#幸运果实随机器
	SecretGarden_LuckyReward_RandomObj = Random.RandomRate()
	
	#累计奖励配置 {rewardId:cfg,}
	SecretGarden_UnlockReward_Dict = {}

class SecretGardenRewardPool(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("SecretGardenRewardPool.txt")
	def __init__(self):
		self.rewardId = int
		self.item = self.GetEvalByString
		self.isPrecious = int
		self.rateValue = int
	

def LoadSecretGardenRewardPool():
	global SecretGarden_RewardPool_Dict
	for cfg in SecretGardenRewardPool.ToClassType():
		rewardId = cfg.rewardId
		if rewardId in SecretGarden_RewardPool_Dict:
			print "GE_EXC,LoadSecretGardenRewardPool:repeat rewardId(%s) in SecretGarden_RewardPool_Dict" % rewardId
		SecretGarden_RewardPool_Dict[rewardId] = cfg


class SecretGardenLottery(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("SecretGardenLottery.txt")
	def __init__(self):
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		self.rewardPool = self.GetEvalByString
	
	
	def process(self):
		self.randObj = Random.RandomRate()
		RPG = SecretGarden_RewardPool_Dict.get
		for rewardId in self.rewardPool:
			rewardCfg = RPG(rewardId)
			if not rewardCfg:
				print "GE_EXC, SecretGardenLottery::process:rewardId(%s) not in SecretGarden_RewardPool_Dict" % rewardId
			self.randObj.AddRandomItem(rewardCfg.rateValue, [rewardCfg.rewardId, rewardCfg.item[0], rewardCfg.item[1], rewardCfg.isPrecious])


def LoadSecretGardenLottery():
	global SecretGarden_Lottery_Dict
	for cfg in SecretGardenLottery.ToClassType():
		levelRangeId = cfg.levelRangeId
		if levelRangeId in SecretGarden_Lottery_Dict:
			print "GE_EXC,LoadSecretGardenLottery:repeat levelRangeId(%s) in SecretGarden_Lottery_Dict" % levelRangeId
		cfg.process()
		SecretGarden_Lottery_Dict[levelRangeId] = cfg


def GetLotteryRandomByLevel(roleLevel):
	'''
	返回 对应 玩家等级 roleLevel 的抽奖随机对象
	'''		
	for lotteryCfg in SecretGarden_Lottery_Dict.itervalues():
		levelRange = lotteryCfg.levelRange
		if levelRange[0] <= roleLevel <= levelRange[1]:
			return lotteryCfg.randObj
	return None
	

class SecretGardenLuckyReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("SecretGardenLuckyReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.rewardItem = self.GetEvalByString
		self.rateValue = int
		self.isPrecious = int
		self.grownCnt = int
	

def LoadSecretGardenLuckyReward():
	global SecretGarden_LuckyReward_Dict
	for cfg in SecretGardenLuckyReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in SecretGarden_LuckyReward_Dict:
			print "GE_EXC,LoadSecretGardenLuckyReward: repeat rewardIndex(%s) in SecretGarden_LuckyReward_Dict" % rewardIndex
		SecretGarden_LuckyReward_Dict[rewardIndex] = cfg
		
	global SecretGarden_LuckyReward_RandomObj
	for rewardIndex, rewardCfg in SecretGarden_LuckyReward_Dict.iteritems():
		SecretGarden_LuckyReward_RandomObj.AddRandomItem(rewardCfg.rateValue, rewardIndex)



class SecretGardenUnlockReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("SecretGardenUnlockReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rewardItem = self.GetEvalByString
		self.needServerCnt = int
		self.needRoleCnt = int


def LoadSecretGardenUnlockReward():
	global SecretGarden_UnlockReward_Dict
	for cfg in SecretGardenUnlockReward.ToClassType():
		rewardId = cfg.rewardId
		if rewardId in SecretGarden_UnlockReward_Dict:
			print "GE_EXC,LoadSecretGardenUnlockReward:repeat rewardId(%s) in SecretGarden_UnlockReward_Dict" % rewardId
		SecretGarden_UnlockReward_Dict[rewardId] = cfg


def LoadConfig():
	'''
	有序的加载配置
	'''
	#先加载奖励池
	LoadSecretGardenRewardPool()
	#再加载抽奖控制
	LoadSecretGardenLottery()
	
	#加载果实配置
	LoadSecretGardenLuckyReward()
	
	#加载累计奖励
	LoadSecretGardenUnlockReward()


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadConfig()
