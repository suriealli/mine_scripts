#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DuanWuJie.DuanWuJieConfig")
#===============================================================================
# 欢庆端午节配置
#===============================================================================

import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DuanWuJie")
	
	RewardConfigDict = {}
	GoldZongziConfigDict = {}
	NormalZongziConfigDict = {}
	ZongziDropConfigDict = {}
	LevelRangeDict = {}


class RewardConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("reward.txt")
	def __init__(self):
		self.rewardID = int
		self.ItemCode = int
		self.Cnt = int
		self.Type = int
		self.IsBroadcast = int


class GoldZongziConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("goldZongzi.txt")
	def __init__(self):
		self.index = int
		self.levelRange = int
		self.rate = eval
		self.precious = int
		
	def PreCoding(self):
		randomRate = self.randomRate = Random.RandomRate()
		for rewardIndex, rate in self.rate:
			randomRate.AddRandomItem(rate, rewardIndex)
	
	
class NormalZongzi(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("normalZongzi.txt")
	def __init__(self):
		self.levelRange = int
		self.rate = eval
	
	def PreCoding(self):
		randomRate = self.randomRate = Random.RandomRate()
		for rewardIndex, rate in self.rate:
			randomRate.AddRandomItem(rate, rewardIndex)


class ZongziDrop(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("zongziDrop.txt")
	def __init__(self):
		self.activityType = int 
		self.fightIdx = int 
		self.normalRate = int 
		self.normalCoding = int
		self.goldRate = int 
		self.goldCoding = int


class LevelRangeConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LevelRange.txt")
	def __init__(self):
		self.levelRange = int
		self.minLevel = int
		self.maxLevel = int


def LoadLevelRangeConfig():
	global LevelRangeDict
	for config in LevelRangeConfig.ToClassType():
		minLevel = config.minLevel
		maxLevel = config.maxLevel
		for level in xrange(minLevel, maxLevel + 1):
			if level in LevelRangeDict:
				print "GE_EXC,repeat level(%s) in LevelRangeDict in DuanWuJieConfig" % level
			LevelRangeDict[level] = config.levelRange


def LoadRewardConfig():
	global RewardConfigDict
	for config in RewardConfig.ToClassType():
		if config.rewardID in RewardConfigDict:
			print "GE_EXC,repeat rewardID(%s) in RewardConfigDict in DuanWuJieConfig" % config.rewardID
		RewardConfigDict[config.rewardID] = config


def LoadGoldZongziConfig():
	global GoldZongziConfigDict
	for config in GoldZongziConfig.ToClassType():
		if (config.index, config.levelRange) in GoldZongziConfigDict:
			print "GE_EXC,repeat (index(%s),levelRange(%s)) in GoldZongziConfigDict in DuanWuJieConfig" % (config.index, config.levelRange)
		config.PreCoding()
		GoldZongziConfigDict[(config.index, config.levelRange)] = config


def LoadNormalZongziConfig():
	global NormalZongziConfigDict
	for config in NormalZongzi.ToClassType():
		if config.levelRange in NormalZongziConfigDict:
			print "GE_EXC,repeat levelRange(%s) in NormalZongziConfigDict in DuanWuJieConfig" % config.levelRange
		config.PreCoding()
		NormalZongziConfigDict[config.levelRange] = config


def LoadZongziDrop():
	global ZongziDropConfigDict
	for config in ZongziDrop.ToClassType():
		ZongziDropConfigDict[(config.activityType, config.fightIdx)] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRewardConfig()
		LoadGoldZongziConfig()
		LoadNormalZongziConfig()
		LoadZongziDrop()
		LoadLevelRangeConfig()
		
