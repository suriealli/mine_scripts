#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ShenWangBaoKu.ShenWangBaoKuConfig")
#===============================================================================
# 神王宝库配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ShenWangBaoKu")
	
	RewardConfigDict = {}
	RewardItemConfigDict = {}
	PointStoreConfigDict = {}


class RewardConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("reward.txt")
	def __init__(self):
		self.level = int
		self.rewards1 = eval
		self.rewards2 = eval
		
	def PreCoding(self):
		randomRate1 = self.randomRate1 = Random.RandomRate()
		randomRate2 = self.randomRate2 = Random.RandomRate()
		for index, rate in self.rewards1:
			randomRate1.AddRandomItem(rate, index)
			
		for index, rate in self.rewards2:
			randomRate2.AddRandomItem(rate, index)
		


class RewardItemConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("rewardconfig.txt")
	def __init__(self):
		self.index = int
		self.thing = eval
		self.type = int
		self.isBroadcast = int
	

class PointStoreConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("pointStore.txt")
	def __init__(self):
		self.itemCoding = int
		self.needPoint = int
		self.limitCnt = int
		self.needLevel = int
		self.needWorldLevel = int


def LoadRewardConfig():
	global RewardConfigDict
	for config in RewardConfig.ToClassType():
		if config.level in RewardConfigDict:
			print "GE_EXC, repeat config.level(%s) in RewardConfigDictShenWangBaoKu " % config.level
			
		config.PreCoding()
		RewardConfigDict[config.level] = config


def LoadRewardItemConfig():
	global RewardItemConfigDict
	for config in RewardItemConfig.ToClassType():
		if config.index in RewardItemConfigDict:
			print "GE_EXC, repeat config.index(%s) in RewardItemConfigDictShenWangBaoKu " % config.index
		RewardItemConfigDict[config.index] = config


def LoadPointStoreConfig():
	global PointStoreConfigDict
	for config in PointStoreConfig.ToClassType():
		if config.itemCoding in PointStoreConfigDict:
			print "GE_EXC, repeat config.itemCoding(%s) in PointStoreConfigDictShenWangBaoKu " % config.itemCoding
		PointStoreConfigDict[config.itemCoding] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRewardConfig()
		LoadRewardItemConfig()
		LoadPointStoreConfig()
		
