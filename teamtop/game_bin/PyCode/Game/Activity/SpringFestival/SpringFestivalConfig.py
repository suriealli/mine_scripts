#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SpringFestival.SpringFestivalConfig")
#===============================================================================
# 春节活动配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	SFESTIVAL_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SFESTIVAL_FILE_FOLDER_PATH.AppendPath("SpringFestival")
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("CircularActive")
	
	RED_ENVELOPE_DICT = {}	#红包配置
	RED_ENVELOPE_TIME = None	#红包开启时间
	RED_ENVELOPE_REWARD_DICT = {}	#购买红包给的奖励
	GOD_WEALTH_DICT = {}	#天降财神
	NIAN_COMING_TIMES_DICT = {}	#年兽来了次数配置
	NIAN_COMING_REWARD_DICT = {}#年兽来了奖励配置
	NIAN_MINLEVEL_LIST = []	#缓存年兽来了最小级
	NIAN_COMING_EXCHANGE_DICT = {}#年兽兑换
	SPRING_SISCOUNT_DICT = {}	#折扣汇配置
	SPRING_SISCOUNTLV_LIST = []
	SPRING_DISCOUNT_RANDOM_DICT = {}#折扣汇随机配置
	SPRING_DISCOUNT_FRESH_DICT = {}	#折扣刷新
	SPRING_SERVER_TYPE_DICT = {}	#最靓丽分区配置
	SPRING_LOCAL_RANK_DICT = {}		#最靓丽本地排行
	SPRING_REWARD_DICT = {}			#最靓丽积分奖励
	SPRING_SHOP_DICT = {}			#靓丽时装修商店
	
class RedEnvelope(TabFile.TabLine):
	'''
	红包配置
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("RedEnvelope.txt")
	def __init__(self):
		self.index = int
		self.needUnbindRMB_Q = int
		self.needDay1 = int
		self.day1 = int
		self.needDay2 = int
		self.day2 = int
		self.needDay3 = int
		self.day3 = int
		self.needDay4 = int
		self.day4 = int
		self.needDay5 = int
		self.day5 = int
		self.needDay6 = int
		self.day6 = int
		self.needDay7 = int
		self.day7 = int
		
def LoadRedEnvelope():
	global RED_ENVELOPE_DICT
	
	for cfg in RedEnvelope.ToClassType():
		if cfg.index in RED_ENVELOPE_DICT:
			print "GE_EXC,repeat index(%s) in LoadRedEnvelope" % cfg.index
		RED_ENVELOPE_DICT[cfg.index] = cfg
	
class RedEnvelopeActive(TabFile.TabLine):
	'''
	新年红包活动时间配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("RedEnvelopeActive.txt")
	def __init__(self):
		self.StartTime = self.GetDatetimeByString
		self.EndTime = self.GetDatetimeByString
		
def LoadLoadRedEnvelopeTime():
	global RED_ENVELOPE_TIME
	for cfg in RedEnvelopeActive.ToClassType():
		RED_ENVELOPE_TIME = cfg
		
class RedEnvelopeReward(TabFile.TabLine):
	'''
	购买红包后给的奖励
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("RedEnvelopeReward.txt")
	def __init__(self):
		self.level = int
		self.reward1 = self.GetEvalByString
		self.reward2 = self.GetEvalByString
		self.reward3 = self.GetEvalByString
		
def LoadRedEnvelopeReward():
	global RED_ENVELOPE_REWARD_DICT
	
	for cfg in RedEnvelopeReward.ToClassType():
		if cfg.level in RED_ENVELOPE_REWARD_DICT:
			print "GE_EXC,repeat level(%s) in LoadRedEnvelopeReward" % cfg.level
		RED_ENVELOPE_REWARD_DICT[cfg.level] = cfg
	
class GodWealth(TabFile.TabLine):
	'''
	天降财神
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("GodWealth.txt")
	def __init__(self):
		self.index = int
		self.needCostRMB = int
		self.rewardRMB_S = int
		
def LoadGodWealth():
	global GOD_WEALTH_DICT
	
	for cfg in GodWealth.ToClassType():
		if cfg.index in GOD_WEALTH_DICT:
			print "GE_EXC,repeat index(%s) in LoadGodWealth" % cfg.index
		GOD_WEALTH_DICT[cfg.index] = cfg
		
class NianComingTimes(TabFile.TabLine):
	'''
	年兽来了奖励次数配置
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("NianComingTimes.txt")
	def __init__(self):
		self.index = int
		self.needUnRMB_Q = int
		self.rewardTimes = int
		
def LoadNianComingTimes():
	global NIAN_COMING_TIMES_DICT
	
	for cfg in NianComingTimes.ToClassType():
		if cfg.index in NIAN_COMING_TIMES_DICT:
			print "GE_EXC,repeat index(%s) in NianComingTimes" % cfg.index
		NIAN_COMING_TIMES_DICT[cfg.index] = cfg
	
class NianComingReward(TabFile.TabLine):
	'''
	年兽奖励配置
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("NianComingReward.txt")
	def __init__(self):
		self.MinLevel = int
		self.RMBReward = self.GetEvalByString
		self.NianReward = self.GetEvalByString
	
	def PretreatRate(self):
		self.RMBReward_Random = Random.RandomRate()
		self.NianReward_Random = Random.RandomRate()
		for (rate, itemCoding, itemCnt, codingType, isRumor) in self.RMBReward:
			self.RMBReward_Random.AddRandomItem(rate, (itemCoding, itemCnt, codingType, isRumor))
			
		for (rate, itemCoding, itemCnt) in self.NianReward:
			self.NianReward_Random.AddRandomItem(rate, (itemCoding, itemCnt))
			
def LoadNianComingReward():
	global NIAN_COMING_REWARD_DICT, NIAN_MINLEVEL_LIST
	
	for cfg in NianComingReward.ToClassType():
		if cfg.MinLevel in NIAN_COMING_REWARD_DICT:
			print "GE_EXC,repeat MinLevel(%s) in NianComingReward" % cfg.MinLevel
		NIAN_COMING_REWARD_DICT[cfg.MinLevel] = cfg
		cfg.PretreatRate()
		NIAN_MINLEVEL_LIST.append(cfg.MinLevel)
	NIAN_MINLEVEL_LIST = list(set(NIAN_MINLEVEL_LIST))
	NIAN_MINLEVEL_LIST.sort()
	
class NianComingExchange(TabFile.TabLine):
	'''
	兑换年兽
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("NianComingExchange.txt")
	def __init__(self):
		self.coding = int
		self.needCoding = int
		self.needCnt = int
		
def LoadNianComingExchange():
	global NIAN_COMING_EXCHANGE_DICT
	
	for cfg in NianComingExchange.ToClassType():
		if cfg.coding in NIAN_COMING_EXCHANGE_DICT:
			print "GE_EXC,repeat coding(%s) in NianComingExchange" % cfg.coding
		NIAN_COMING_EXCHANGE_DICT[cfg.coding] = cfg
		
class SpringFDiscountConfig(TabFile.TabLine):
	'''
	折扣汇
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("SpringFDiscountConfig.txt")
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
		global SPRING_DISCOUNT_RANDOM_DICT
		
		if self.levelRange not in SPRING_DISCOUNT_RANDOM_DICT:
			SPRING_DISCOUNT_RANDOM_DICT[self.levelRange] = Random.RandomRate()
			SPRING_DISCOUNT_RANDOM_DICT[self.levelRange].AddRandomItem(self.rateValue, (self.goodId, self.itemCnt))
		else:
			SPRING_DISCOUNT_RANDOM_DICT[self.levelRange].AddRandomItem(self.rateValue, (self.goodId, self.itemCnt))
	
def LoadNewYearDiscountConfig():
	global SPRING_DISCOUNT_RANDOM_DICT, SPRING_SISCOUNT_DICT, SPRING_SISCOUNTLV_LIST
	
	
	for NYD in SpringFDiscountConfig.ToClassType():
		if NYD.goodId in SPRING_SISCOUNT_DICT:
			print 'GE_EXC, repeat goodId %s in SPRING_SISCOUNT_DICT' % NYD.goodId
		NYD.PreLevelRange()
		
		SPRING_SISCOUNT_DICT[NYD.goodId] = NYD
	
	SPRING_SISCOUNTLV_LIST = list(set(SPRING_DISCOUNT_RANDOM_DICT.keys()))
	SPRING_SISCOUNTLV_LIST.sort()
	
class SpringFDiscountFresh(TabFile.TabLine):
	'''
	折扣汇刷新
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("SpringFDiscountFresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.needScore = int
		
def LoadSpringFDiscountFresh():
	global SPRING_DISCOUNT_FRESH_DICT
	
	for cfg in SpringFDiscountFresh.ToClassType():
		if cfg.refreshCnt in SPRING_DISCOUNT_FRESH_DICT:
			print "GE_EXC,repeat refreshCnt(%s) in LoadSpringFDiscountFresh" % cfg.refreshCnt
		SPRING_DISCOUNT_FRESH_DICT[cfg.refreshCnt] = cfg

class SpringBServerType(TabFile.TabLine):
	'''
	春节最靓丽服务器分区
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("SpringBServerType.txt")
	def __init__(self):
		self.serverType = int
		self.kaifuDay = self.GetEvalByString
		
def LoadSpringBServerType():
	global SPRING_SERVER_TYPE_DICT
	
	for cfg in SpringBServerType.ToClassType():
		if cfg.serverType in SPRING_SERVER_TYPE_DICT:
			print "GE_EXC,repeeat serverType(%s) in LoadSpringBServerType" % cfg.serverType
		SPRING_SERVER_TYPE_DICT[cfg.serverType] = cfg
		
class SpringBLRank(TabFile.TabLine):
	'''
	春节最靓丽本地排行
	'''
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("SpringBLRank.txt")
	def __init__(self):
		self.serverType = int
		self.rank = int
		self.needScore = int
		self.rewardItems = self.GetEvalByString
		self.money = int
		self.bindRMB = int
		
def LoadSpringBLRank():
	global SPRING_LOCAL_RANK_DICT
	
	for cfg in SpringBLRank.ToClassType():
		key = (cfg.serverType, cfg.rank)
		if key in SPRING_LOCAL_RANK_DICT:
			print "GE_EXC,repeat rank(%s) and serverType(%s) in LoadSpringBLRank" % (cfg.rank, cfg.serverType)
		SPRING_LOCAL_RANK_DICT[key] = cfg
		
class SpringBReward(TabFile.TabLine):
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("SpringBReward.txt")
	def __init__(self):
		self.index = int
		self.rewardItems = self.GetEvalByString
	
def LoadSpringBReward():
	global SPRING_REWARD_DICT
	
	for cfg in SpringBReward.ToClassType():
		if cfg.index in SPRING_REWARD_DICT:
			print "GE_EXC,repeat index(%s) in LoadSpringBReward" % cfg.index
		SPRING_REWARD_DICT[cfg.index] = cfg
		
class SpringShop(TabFile.TabLine):
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("SpringShop.txt")
	def __init__(self):
		self.coding = int
		self.needCoding = int
		self.needItemCnt = int
		self.needLevel = int
		self.needWorldLevel = int
		self.limitCnt = int
		self.isSend = int
		
def LoadSpringShop():
	global SPRING_SHOP_DICT
	
	for cfg in SpringShop.ToClassType():
		if cfg.coding in SPRING_SHOP_DICT:
			print "GE_EXC,repeat coding(%s) in SpringShop" % cfg.coding
		SPRING_SHOP_DICT[cfg.coding] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRedEnvelope()
		LoadLoadRedEnvelopeTime()
		LoadRedEnvelopeReward()
		LoadGodWealth()
		LoadNianComingTimes()
		LoadNianComingReward()
		LoadNianComingExchange()
		LoadNewYearDiscountConfig()
		LoadSpringFDiscountFresh()
		LoadSpringBServerType()
		LoadSpringBLRank()
		LoadSpringBReward()
		LoadSpringShop()
		