#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionMarketConfig")
#===============================================================================
# 激情卖场 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	DiscountConfigDict = {}
	LevelRangeRandomDict = {}	#等级区间对应的随机物品库列表
	RefreshConfigDict = {}		#刷新次数对应扣除神石数的配置字典
	MAXREFRESHCNT = 0			#刷新代价封顶次数
	

class PassionMarketConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionMarketConfig.txt")
	def __init__(self):
		self.goodId = int
		self.item = eval
		self.limitCnt = int
		self.needUnbindRMB = int
		self.RMBType = int
	

class PassionMarketRefreshConfig(TabFile.TabLine):
	'''
	激情卖场刷新
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("PassionMarketRefresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.needUnbindRMB = int


class PassionMarketRateConfig(TabFile.TabLine):
	'''
	激情卖场商品概率配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("PassionMarketRate.txt")
	
	def __init__(self):
		self.levelRange = eval
		self.rate = eval


def LoadPassionMarketConfig():
	global DiscountConfigDict, LevelRangeConfigDict
	for config in PassionMarketConfig.ToClassType():
		if config.goodId in DiscountConfigDict:
			print 'GE_EXC, repeat goodId %s in DiscountConfigDict in PassionMarketConfig' % config.goodId
		DiscountConfigDict[config.goodId] = config
		

def LoadPassionMarketRefreshConfig():
	global MAXREFRESHCNT
	global RefreshConfigDict
	for config in PassionMarketRefreshConfig.ToClassType():
		if config.refreshCnt in RefreshConfigDict:
			print "GE_EXC,repeat refreshCnt(%s) in RefreshConfigDict in PassionMarketRefreshConfig" % config.refreshCnt
		RefreshConfigDict[config.refreshCnt] = config.needUnbindRMB
		
		if config.refreshCnt > MAXREFRESHCNT:
			MAXREFRESHCNT = config.refreshCnt

def LoadPassionMarketRateConfig():
	global LevelRangeRandomDict
	for config in PassionMarketRateConfig.ToClassType():
		lowLevel, highlevel = config.levelRange
		for level in xrange(lowLevel, highlevel + 1):
			if level in LevelRangeRandomDict:
				print "GE_EXC,repeat level(%s) in LevelRangeRandomDict in PassionMarketConfig" % level
			LevelRangeRandomDict[level] = config.rate


if "_HasLoad" not in dir():	
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionMarketConfig()
		LoadPassionMarketRefreshConfig()
		LoadPassionMarketRateConfig()