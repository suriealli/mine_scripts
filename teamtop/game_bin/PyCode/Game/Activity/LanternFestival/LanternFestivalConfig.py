#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LanternFestival.LanternFestivalConfig")
#===============================================================================
# 元宵节活动配置表
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("LanternFestival")
	
	RiddleList = []
	RiddleConfigDict = {}
	
	LanternServerTypeDict = {}
	
	HappinessLanternDict = {}
	HappinessLanternSectionSet = set()
	LanternExtendedConfigDict = {}
	
	LanternRebateDict = {}
	LanternRebateActiveDict = {}
	
	LanternRankConfigDict = {}
	LanternFestivalTargetDict = {}
	
	LanternStoreConfigDict = {}
	
	BuyRiddleTimesConfigDict = {}


#===============================================================================
# 欢乐花灯
#===============================================================================
class HappinessLanternConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LanternHappnessFestival.txt")
	def __init__(self):
		self.levelSection = int
		self.minlevel = int
		self.upperlantern = eval
		self.lowerLantern = eval
		self.needMoney = int
		self.awardPoint = int
		self.upperAwardItems = eval
		self.lowerAwardItems = eval
		
	
	def PreCoding(self):
		self.RandomRateUpper = randomRateUpper = Random.RandomRate()
		self.RandomRateLower = randomRateLower = Random.RandomRate()
		for item, rate in self.upperAwardItems:
			randomRateUpper.AddRandomItem(rate, item)
		for item, rate in self.lowerAwardItems:
			randomRateLower.AddRandomItem(rate, item)


def LoadHappinessLanternConfig():
	global HappinessLanternDict
	for config in HappinessLanternConfig.ToClassType():
		if config.levelSection in HappinessLanternDict:
			print "GE_EXC,repeat levelSection(%s) in HappinessLanternDict" % config.levelSection
		config.PreCoding()
		HappinessLanternDict[config.levelSection] = config
		HappinessLanternSectionSet.add(config.minlevel)


class LanternExtended(TabFile.TabLine):
	'''
	探宝器掉落配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("LanternExtended.txt")
	def __init__(self):
		self.activityType = int
		self.fightIdx = int
		self.dropOdds = int
		self.dropItemCoding = int
		self.needLevel = int

def LoadLanternExtended():
	global LanternExtendedConfigDict
	for config in LanternExtended.ToClassType():
		LanternExtendedConfigDict[(config.activityType, config.fightIdx)] = config

#===============================================================================
# 花灯返利
#===============================================================================
class LanternRebateConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LanternRebate.txt")
	def __init__(self):
		self.Index = int
		self.rebateLevel = int
		self.NeedVIPLevel = int
		self.Items = eval


def LoadLanternRebateConfig():
	global LanternRebateDict
	for config in LanternRebateConfig.ToClassType():
		if (config.Index, config.rebateLevel) in LanternRebateDict:
			print "GE_EXC,repeat (Index,rebateLevel)(%s,%s) in LanternRebateDict" % (config.Index, config.rebateLevel)
		LanternRebateDict[(config.Index, config.rebateLevel)] = config


class LanternRebateActiveConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LanternRebateActive.txt")
	def __init__(self):
		self.Index = int
		self.NeedPoint = int

def LoadLanternRebateActive():
	global LanternRebateActiveDict
	for config in LanternRebateActiveConfig.ToClassType():
		if config.Index in LanternRebateActiveDict:
			print "GE_EXC,repeat Index(%s) in LanternRebateActiveDict" % config.Index
		LanternRebateActiveDict[config.Index] = config.NeedPoint

#===============================================================================
# 点灯高手
#===============================================================================
class LanternRankConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LanternLocalRank.txt")
	def __init__(self):
		self.rank = int							#排名
		self.serverType = int					#服务器类型
		self.needScore = int
		self.rewardItems = eval
		self.money = int
		self.bindRMB = int


def LoadLanternRankConfig():
	global LanternRankConfigDict
	for config in LanternRankConfig.ToClassType():
		if (config.rank, config.serverType) in LanternRankConfigDict:
			print "GE_EXC, repeat (rank,serverType)(%s,%s) in LanternRankConfigDict" % (config.rank, config.serverType)
		LanternRankConfigDict[(config.rank, config.serverType)] = config


class LanternServerTypeConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LanternServerType.txt")
	def __init__(self):
		self.serverType = int						#服务器类型
		self.kaifuDay = eval		

def LoadLanternServerTypeConfig():
	global LanternServerTypeDict
	
	for config in LanternServerTypeConfig.ToClassType():
		if config.serverType in LanternServerTypeDict:
			print "GE_EXC, repeat serverType (%s) in LanternServerTypeDict" % config.serverType
			continue
		LanternServerTypeDict[config.serverType] = config


class LanternTargetConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LanternTarget.txt")
	def __init__(self):
		self.Index = int
		self.NeedPoint = int
		self.Items = eval


def LoadLanternTargetConfig():
	global LanternFestivalTargetDict
	for config in LanternTargetConfig.ToClassType():
		if config.Index in LanternFestivalTargetDict:
			print "GE_EXC,repeat Index(%s) in LanternFestivalTargetDict"
		LanternFestivalTargetDict[config.Index] = config


#===============================================================================
# 元宵商店
#===============================================================================
class LanternStoreConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LanternStore.txt")
	def __init__(self):
		self.coding = int							#物品coding
		self.needCoding = int						#需要物品coding
		self.needLevel = int						#兑换需要的角色等级
		self.needWorldLevel = int					#兑换需要的世界等级
		self.limitCnt = int							#限购个数(0-不限购)
		self.needItemCnt = int						#兑换需要的物品个数


def LoadLanternStoreConfig():
	global LanternStoreConfigDict
	for config in LanternStoreConfig.ToClassType():
		if config.coding in LanternStoreConfigDict:
			print "GE_EXC, repeat coding (%s) in LanternStoreConfigDict" % config.coding
		LanternStoreConfigDict[config.coding] = config

#===============================================================================
# 购买猜灯谜次数配置
#===============================================================================
class BuyRiddleTimesConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("RiddleBuyPrice.txt")
	def __init__(self):
		self.Cnt = int
		self.Price = int


def LoadBuyRiddleTimesConfig():
	global BuyRiddleTimesConfigDict
	for config in BuyRiddleTimesConfig.ToClassType():
		if config.Cnt in BuyRiddleTimesConfigDict:
			print "GE_EXC,repeat Cnt(%s) in BuyRiddleTimesConfigDict" % config.Cnt
		BuyRiddleTimesConfigDict[config.Cnt] = config.Price
	
#===============================================================================
# 灯谜题库
#===============================================================================
class RiddleLibConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("RiddlesLib.txt")
	def __init__(self):
		self.index = int
		self.right = int


def LoadRiddleConfig():
	global RiddleConfigDict
	for config in RiddleLibConfig.ToClassType():
		if config.index in RiddleConfigDict:
			print "GE_EXC,repeat index(%s) in RiddleConfigDict" % config.index 
		RiddleConfigDict[config.index] = config.right
	global RiddleList
	RiddleList = RiddleConfigDict.keys()
	#题目数必须大于20，不然的话肯定是配置表有问题
	assert len(RiddleList) >= 20


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadHappinessLanternConfig()
		LoadLanternExtended()
		LoadLanternRebateConfig()
		LoadLanternRebateActive()
		LoadLanternRankConfig()
		LoadLanternStoreConfig()
		LoadBuyRiddleTimesConfig()
		LoadRiddleConfig()
		LoadLanternServerTypeConfig()
		LoadLanternTargetConfig()
