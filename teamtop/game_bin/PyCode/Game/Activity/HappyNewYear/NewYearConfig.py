#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HappyNewYear.NewYearConfig")
#===============================================================================
# 新年配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	NY_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	NY_FILE_FOLDER_PATH.AppendPath("HappyNewYear")
	
	NYAER_FREE_TIMES = {}	#奖励免费次数配置
	NYEAR_ONLIEN_REWARD = {}#开宝箱奖励配置
	NYEAR_ONLIEN_MINLEVEL_LIST = []
	
	NYDiscount_Dict = {}
	NYDiscountRandom_Dict = {}
	NewYearDiscountLv_List = []
	NYDiscountFresh_Dict = {}
	
	NewYearShop_Dict = {}
	
	NewYearScoreReward_Dict = {}
	
	NewYearLRank_Dict = {}
	NewYearLRank_List = []		#[(rank, needScore), ]
	
class NewYearLRankConfig(TabFile.TabLine):
	FilePath = NY_FILE_FOLDER_PATH.FilePath("NewYearHaoLRank.txt")
	def __init__(self):
		self.rank = int
		self.needScore = int
		self.rewardItems = eval
		self.money = int
		self.bindRMB = int
	
def LoadNewYearLRankConfig():
	global NewYearLRank_Dict
	
	for NYLRC in NewYearLRankConfig.ToClassType():
		if NYLRC.rank in NewYearLRank_Dict:
			print "GE_EXC, repeat rank : %s in NewYearLRank_Dict" % NYLRC.rank
			continue
		NewYearLRank_Dict[NYLRC.rank] = NYLRC
		NewYearLRank_List.append((NYLRC.rank, NYLRC.needScore))
	NewYearLRank_List.sort(reverse=True)
	
class NewYearHaoRewardConfig(TabFile.TabLine):
	FilePath = NY_FILE_FOLDER_PATH.FilePath("NewYearHaoReward.txt")
	def __init__(self):
		self.index = int
		self.rewardItems = eval
	
def LoadNewYearHaoRewardConfig():
	global NewYearScoreReward_Dict
	
	for NYHR in NewYearHaoRewardConfig.ToClassType():
		if NYHR.index in NewYearScoreReward_Dict:
			print 'GE_EXC, repeat index : %s in NewYearScoreReward_Dict' % NYHR.index
			continue
		NewYearScoreReward_Dict[NYHR.index] = NYHR
	
class NewYearShopConfig(TabFile.TabLine):
	FilePath = NY_FILE_FOLDER_PATH.FilePath("NewYearShop.txt")
	def __init__(self):
		self.coding = int							#物品coding
		self.needCoding = int						#需要物品coding
		self.needLevel = int						#兑换需要的角色等级
		self.needWorldLevel = int					#兑换需要的世界等级
		self.limitCnt = int							#限购个数(0-不限购)
		self.needItemCnt = int						#兑换需要的物品个数
	
def LoadNewYearShopConfig():
	global NewYearShop_Dict
	
	for NSC in NewYearShopConfig.ToClassType():
		if NSC.coding in NewYearShop_Dict:
			print "GE_EXC, repeat coding (%s) in NewYearShop_Dict" % NSC.coding
			continue
		NewYearShop_Dict[NSC.coding] = NSC
	
class NYDiscountFreshConfig(TabFile.TabLine):
	FilePath = NY_FILE_FOLDER_PATH.FilePath("NYearDiscountFresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.needScore = int
	
def LoadNYDiscountFreshConfig():
	global NYDiscountFresh_Dict
	
	for NYDF in NYDiscountFreshConfig.ToClassType():
		if NYDF.refreshCnt in NYDiscountFresh_Dict:
			print 'GE_EXC, repeat refreshCnt %s in NYDiscountFresh_Dict' % NYDF.refreshCnt
		NYDiscountFresh_Dict[NYDF.refreshCnt] = NYDF
	
class NewYearDiscountConfig(TabFile.TabLine):
	FilePath = NY_FILE_FOLDER_PATH.FilePath("NewYearDiscountConfig.txt")
	def __init__(self):
		self.goodId = int
		self.levelRange = eval
		self.item = eval
		self.itemCnt = int
		self.rateValue = int
		self.needUnbindRMB = int
		self.RMBType = int
		self.needScore = int
	
	def PreLevelRange(self):
		global NYDiscountRandom_Dict
		
		if self.levelRange not in NYDiscountRandom_Dict:
			NYDiscountRandom_Dict[self.levelRange] = Random.RandomRate()
			NYDiscountRandom_Dict[self.levelRange].AddRandomItem(self.rateValue, (self.goodId, self.itemCnt))
		else:
			NYDiscountRandom_Dict[self.levelRange].AddRandomItem(self.rateValue, (self.goodId, self.itemCnt))
		
def LoadNewYearDiscountConfig():
	global NYDiscountRandom_Dict, NYDiscount_Dict, NewYearDiscountLv_List
	
	for NYD in NewYearDiscountConfig.ToClassType():
		if NYD.goodId in NYDiscount_Dict:
			print 'GE_EXC, repeat goodId %s in NYDiscount_Dict' % NYD.goodId
		NYD.PreLevelRange()
		
		NYDiscount_Dict[NYD.goodId] = NYD
	
	NewYearDiscountLv_List = list(set(NYDiscountRandom_Dict.keys()))
	NewYearDiscountLv_List.sort()
	
class NYearOnlineFreeTimes(TabFile.TabLine):
	'''
	奖励免费次数配置
	'''
	FilePath = NY_FILE_FOLDER_PATH.FilePath("NYearOnlineFreeTimes.txt")
	def __init__(self):
		self.index = int
		self.onlineTime = int
		self.needFill = int
		self.freeTimes = int
		
class NYearOnlineReward(TabFile.TabLine):
	'''
	开宝箱奖励配置
	'''
	FilePath = NY_FILE_FOLDER_PATH.FilePath("NYearOnlineReward.txt")
	def __init__(self):
		self.MinLevel = int
		self.needUnbindRMB = int
		self.FreeReward = self.GetEvalByString
		self.RMBReward = self.GetEvalByString
		
	def PretreatRate(self):
		self.randomReward_free = Random.RandomRate()
		self.randomReward_RMB = Random.RandomRate()
		for (rate, itemCoding, itemCnt, codingType, isRumor) in self.FreeReward:
			self.randomReward_free.AddRandomItem(rate, (itemCoding, itemCnt, codingType, isRumor))
			
		for (rate, itemCoding, itemCnt, codingType, isRumor) in self.RMBReward:
			self.randomReward_RMB.AddRandomItem(rate, (itemCoding, itemCnt, codingType, isRumor))
			
def LoadNYearOnlineFreeTimes():
	global NYAER_FREE_TIMES
	
	for cfg in NYearOnlineFreeTimes.ToClassType():
		if cfg.index in NYAER_FREE_TIMES:
			print "GE_EXC,repeat index(%s) in NYearOnlineFreeTimes" % cfg.index
		NYAER_FREE_TIMES[cfg.index] = cfg
		
def LoadNYearOnlineReward():
	global NYEAR_ONLIEN_REWARD
	global NYEAR_ONLIEN_MINLEVEL_LIST
	for cfg in NYearOnlineReward.ToClassType():
		if cfg.MinLevel in NYEAR_ONLIEN_REWARD:
			print "GE_EXC, repeat MinLevel(%s) in NYEAR_ONLIEN_REWARD" % cfg.MinLevel
		cfg.PretreatRate()
		NYEAR_ONLIEN_REWARD[cfg.MinLevel] = cfg
		NYEAR_ONLIEN_MINLEVEL_LIST.append(cfg.MinLevel)
	NYEAR_ONLIEN_MINLEVEL_LIST = list(set(NYEAR_ONLIEN_MINLEVEL_LIST))
	NYEAR_ONLIEN_MINLEVEL_LIST.sort()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadNYearOnlineFreeTimes()
		LoadNYearOnlineReward()
		LoadNewYearDiscountConfig()
		LoadNYDiscountFreshConfig()
		LoadNewYearShopConfig()
		LoadNewYearHaoRewardConfig()
		LoadNewYearLRankConfig()
		
		