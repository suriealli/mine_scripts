#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.GroupBuyPartyConfig")
#===============================================================================
# 团购派对配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DoubleTwelve")
	#活动时间配置  为解决模块间循环引用问题 放到circularActive中处理 同一份配置
	FILE_FLODER_PATH_EX = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH_EX.AppendPath("CircularActive")
	
	GBP_BASECONFIG = None		#团购派对活动配置
	GBP_GOOD_CONFIG_DICT = {}	#团购派对商品配置{dayIndex:{rangeId:{itemIndex:cfg},},}
	GBP_REWARD_CONFIG_DICT = {}	#团购派对及奖励配置{dayIndex:{itemIndex:cfg,},}
	GBP_RANGE2ID_CONFIG_DICT = {}	#团购商品等级区段对应区段ID关联 {rangId:levelRange,}

class GroupBuyPartyBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH_EX.FilePath("GroupBuyPartyBase.txt")
	def __init__(self):
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.totalDay = int
	
class GroupBuyPartyGood(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("GroupBuyPartyGood.txt")
	def __init__(self):
		self.dayIndex = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.itemIndex = int
		self.item = self.GetEvalByString
		self.needRMB = int

class GroupBuyPartyReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("GroupBuyPartyReward.txt")
	def __init__(self):
		self.dayIndex = int
		self.itemIndex = int
		self.rewards = self.GetEvalByString

def LoadGroupBuyPartyBase():
	global GBP_BASECONFIG
	for cfg in GroupBuyPartyBase.ToClassType():
		GBP_BASECONFIG = cfg
	
def LoadGroupBuyPartyGood():
	global GBP_GOOD_CONFIG_DICT
	global GBP_RANGE2ID_CONFIG_DICT
	for cfg in GroupBuyPartyGood.ToClassType():
		dayIndex = cfg.dayIndex
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		itemIndex = cfg.itemIndex
		dayGoodDict = GBP_GOOD_CONFIG_DICT.setdefault(dayIndex,{})
		dayRangeIdGoodDict = dayGoodDict.setdefault(rangeId,{})
		if itemIndex in dayRangeIdGoodDict:
			print "GE_EXC,repeat itemIndex(%s) in dayIndex(%s),rangeId(%s)" % (itemIndex, rangeId, dayIndex)
		dayRangeIdGoodDict[itemIndex] = cfg
		GBP_RANGE2ID_CONFIG_DICT[rangeId] = levelRange
		

def LoadGroupBuyPartyReward():
	global GBP_REWARD_CONFIG_DICT
	for cfg in GroupBuyPartyReward.ToClassType():
		dayIndex = cfg.dayIndex
		itemIndex = cfg.itemIndex
		dayRewardDict = GBP_REWARD_CONFIG_DICT.setdefault(dayIndex,{})
		if itemIndex in dayRewardDict:
			print "GE_EXC,repeat itemIndex(%s) in dayIndex(%s)" % (itemIndex, dayIndex)
		dayRewardDict[itemIndex] = cfg

def GetRewardCfgByDayAndIndex(dayIndex, itemIndex):
	'''
	获取对应天数和物品奖励配置
	'''
	dayRewardCfgDict = GBP_REWARD_CONFIG_DICT.get(dayIndex)
	if not dayRewardCfgDict:
		print "GE_EXC, can not get dayRewardCfgDict by dayIndex(%s)" % dayIndex
		return None
	
	rewardCfg = dayRewardCfgDict.get(itemIndex)
	if not rewardCfg:
		print "GE_EXC, can not get rewardCfg by itemIndex(%s)" % itemIndex
		return None
	
	return rewardCfg

def GetGoodCfgByIndexAndLevel(dayIndex, itemIndex, roleLevel):
	'''
	获取对应商品索引和等级对应商品配置
	'''
	dayGoodDict = GBP_GOOD_CONFIG_DICT.get(dayIndex)
	if not dayGoodDict:
		print "GE_EXC, GetGoodCfgByIndexAndLevel::can not get dayGoodDict by dayIndex(%s)" % dayIndex
		return None
	
	tmpRangeId = 1
	for rangeId, levelRange in GBP_RANGE2ID_CONFIG_DICT.iteritems():
		levelDown, levelUp = levelRange
		tmpRangeId = rangeId
		if levelDown <= roleLevel and roleLevel <= levelUp:
			break
	
	dayRangeIdGoodDict = dayGoodDict.get(tmpRangeId)
	if not dayRangeIdGoodDict:
		print "GE_EXC,GetGoodCfgByIndexAndLevel::can not get dayRangeIdGoodDict by tmpRangeId(%s)" % tmpRangeId
		return None
	
	goodCfg = dayRangeIdGoodDict.get(itemIndex)
	if not goodCfg:
		print "GE_EXC, GetGoodCfgByIndexAndLevel::can not get goodCfg by itemIndex(%s)" % itemIndex
		return None
	
	return goodCfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadGroupBuyPartyBase()
		LoadGroupBuyPartyGood()
		LoadGroupBuyPartyReward()