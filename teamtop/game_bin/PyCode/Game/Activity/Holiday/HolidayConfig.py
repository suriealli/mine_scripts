#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Holiday.HolidayConfig")
#===============================================================================
# 元旦配置表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	HC_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	HC_FILE_FOLDER_PATH.AppendPath("Holiday")
	
	ShoppingFestival_Dict = {}
	ShoppingFestivalLv_List = []
	
	ShoppingScore_Dict = {}
	ShoppingScore_List = []
	
	MoneyWish_Dict = {}
	MoneyWishLv_List = []
	
class ShoppingFestivalConfig(TabFile.TabLine):
	FilePath = HC_FILE_FOLDER_PATH.FilePath("HolidayShoppingFestival.txt")
	def __init__(self):
		self.goodNumber = int
		self.minLevel = int
		
		self.goodCoding1 = int
		self.needUnindRMB1 = int
		self.needUnbindRMB_Q1 = int
		
		self.goodCoding2 = int
		self.needUnindRMB2 = int
		self.needUnbindRMB_Q2 = int
		
		self.limitCnt = int
	
	def PretreatGood(self):
		#预处理商品波数对应的商品
		self.waveGoodDict = {}
		
		self.waveGoodDict[1] = (self.goodCoding1, self.needUnindRMB1, self.needUnbindRMB_Q1)
		self.waveGoodDict[2] = (self.goodCoding2, self.needUnindRMB2, self.needUnbindRMB_Q2)
		
class ShoppingScoreConfig(TabFile.TabLine):
	FilePath = HC_FILE_FOLDER_PATH.FilePath("HolidayShoppingScore.txt")
	def __init__(self):
		self.scoreIndex = int
		self.minScore = int
		self.rewardCoding = int
	
class MoneyWishConfig(TabFile.TabLine):
	FilePath = HC_FILE_FOLDER_PATH.FilePath("HolidayMoneyWish.txt")
	def __init__(self):
		self.minLevel = int
		self.needMoney = int
		self.reward = eval
	
	def PretreatRate(self):
		self.randomReward = Random.RandomRate()
		
		for (rate, itemCoding, itemCnt, isRumor) in self.reward:
			self.randomReward.AddRandomItem(rate, (itemCoding, itemCnt, isRumor))
	
def LoadMoneyWishConfig():
	global MoneyWish_Dict, MoneyWishLv_List
	
	for MW in MoneyWishConfig.ToClassType():
		if MW.minLevel in MoneyWish_Dict:
			print 'GE_EXC, repeat minLevel %s in MoneyWish_Dict' % MW.minLevel
		MW.PretreatRate()
		MoneyWish_Dict[MW.minLevel] = MW
		MoneyWishLv_List.append(MW.minLevel)
	MoneyWishLv_List = list(set(MoneyWishLv_List))
	MoneyWishLv_List.sort()
	
def LoadShoppingScoreConfig():
	global ShoppingScore_Dict, ShoppingScore_List
	
	for SS in ShoppingScoreConfig.ToClassType():
		if SS.scoreIndex in ShoppingScore_Dict:
			print 'GE_EXC, repeat scoreIndex %s in ShoppingScore_Dict' % SS.scoreIndex
		ShoppingScore_Dict[SS.scoreIndex] = SS
		ShoppingScore_List.append(SS.minScore)
	ShoppingScore_List = list(set(ShoppingScore_List))
	ShoppingScore_List.sort()
	
def LoadShoppingFestivalConfig():
	global ShoppingFestival_Dict, ShoppingFestivalLv_List
	
	for SF in ShoppingFestivalConfig.ToClassType():
		if (SF.goodNumber, SF.minLevel) in ShoppingFestival_Dict:
			print 'GE_EXC, repeat goodNumber %s, minLevel %s in ShoppingFestival_Dict' % (SF.goodNumber, SF.minLevel)
		SF.PretreatGood()
		ShoppingFestival_Dict[(SF.goodNumber, SF.minLevel)] = SF
		ShoppingFestivalLv_List.append(SF.minLevel)
	ShoppingFestivalLv_List = list(set(ShoppingFestivalLv_List))
	ShoppingFestivalLv_List.sort()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadMoneyWishConfig()
		LoadShoppingScoreConfig()
		LoadShoppingFestivalConfig()
	