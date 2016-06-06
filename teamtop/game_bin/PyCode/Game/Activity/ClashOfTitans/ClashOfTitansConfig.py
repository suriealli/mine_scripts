#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ClashOfTitans.ClashOfTitansConfig")
#===============================================================================
# 诸神之战配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ClashOfTitans")

	LevelRangeDict = {}				#level-->levelRange
	PersonRankConfigDict = {}	 	#(rank,levelRange)-->config
	
	PersonScoreConfigDict = {}		#(score,levelRange) --> config
	PersonScoreRangeDict = {}		#levelRange--> [每个积分段的最小积分]
	
	UnionScoreConfigDict = {}		#(score,levelRange) --> config
	UnionScoreRangeDict = {}		#levelRange--> [每个积分段的最小积分]
	
	TitanConfigDict = {}			#levelrange --> config
	TitanUnionConfigDict = {}		#evelrange --> config


class LevelRangeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LevelRange.txt")
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
				print "GE_EXC,repeat level(%s) in LevelRangeDict in ClashOfTitans" % level
			LevelRangeDict[level] = config.levelRange


class PersonRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ClashOfTitansPersonRank.txt")
	def __init__(self):
		self.rank = int
		self.levelRange = int
		self.rewardItems = eval
		self.rewardMoney = int


def LoadPersonRankConfig():
	global PersonRankConfigDict
	for config in PersonRankConfig.ToClassType():
		if (config.rank, config.levelRange) in PersonRankConfigDict:
			print 'GE_EXC, repeat rank %s levelRange %s in PersonRankConfigDict in ClashOfTitans' % (config.rank, config.levelRange)
		PersonRankConfigDict[(config.rank, config.levelRange)] = config



class PersonScoreConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ClashOfTitansPersonScore.txt")
	def __init__(self):
		self.score = int
		self.levelRange = int
		self.rewardItems = eval
		self.rewardMoney = int

def LoadPersonScoreConfig():
	global PersonScoreConfigDict, PersonScoreRangeDict
	for config in PersonScoreConfig.ToClassType():
		if (config.score, config.levelRange) in PersonScoreConfigDict:
			print "GE_EXC,repeat (score, levelRange)(%s,%s) in PersonScoreConfigDict in ClashOfTitans" % (config.score, config.levelRange)
		PersonScoreConfigDict[(config.score, config.levelRange)] = config
		PersonScoreRangeDict.setdefault(config.levelRange, set()).add(config.score)


class UnionScoreConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ClashOfTitansUnionScore.txt")
	def __init__(self):
		self.rewardId = int
		self.score = int
		self.levelRange = int
		self.rewardItems = eval
		self.experience = int


def LoadUnionScoreConfig():
	global UnionScoreConfigDict, UnionScoreRangeDict
	for config in UnionScoreConfig.ToClassType():
		if (config.score, config.levelRange) in UnionScoreConfigDict:
			print "GE_EXC,repeat (score, levelRange) (%s,%s) in UnionScoreConfigDict in ClashOfTitans" % (config.score, config.levelRange)
		UnionScoreConfigDict[(config.score, config.levelRange)] = config
		UnionScoreRangeDict.setdefault(config.levelRange, set()).add(config.score)


class TitanConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ClashOfTitansTitanAward.txt")
	def __init__(self):
		self.levelRange = int
		self.rewardItems = eval
		self.rewardMoney = int


def LoadTitanConfig():
	global TitanConfigDict
	for config in TitanConfig.ToClassType():
		if config.levelRange in TitanConfigDict:
			print "GE_EXC,repeat levelRange(%s) in TitanConfigDict in ClashOfTitans" % config.levelRange
		TitanConfigDict[config.levelRange] = config


class TitanUnionConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ClashOfTitansTitanUnion.txt")
	def __init__(self):
		self.levelRange = int
		self.rewardItems = eval
		self.rewardMoney = int


def LoadTitanUnionConfig():
	global TitanUnionConfigDict
	for config in TitanUnionConfig.ToClassType():
		if config.levelRange in TitanUnionConfigDict:
			print "GE_EXC,repeat levelRange(%s) in TitanUnionConfigDict in ClashOfTitans" % config.levelRange
		TitanUnionConfigDict[config.levelRange] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLevelRangeConfig()
		LoadPersonRankConfig()
		LoadPersonScoreConfig()
		LoadUnionScoreConfig()
		LoadTitanConfig()
		LoadTitanUnionConfig()
