#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.YeYouJieDiscount.YeYouJieDiscountConfig")
#===============================================================================
# 页游节折扣汇配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("YeYouJieDiscount")
	
	DiscountConfigDict = {}
	LevelRangeRandomDict = {}	#等级区间对应的随机物品库列表
	RefreshConfigDict = {}		#刷新次数对应扣除神石数的配置字典
	

class YeYouJieDiscountConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("YeYouJieDiscountConfig.txt")
	def __init__(self):
		self.goodId = int
		self.item = eval
		self.limitCnt = int
		self.needUnbindRMB = int
		self.RMBType = int
	

class YeYouJieDiscountFreshConfig(TabFile.TabLine):
	'''
	折扣汇刷新
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("YeYouJieDiscountRefresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.needUnbindRMB = int


class YeYouJieDiscountRateConfig(TabFile.TabLine):
	'''
	折扣汇商品概率配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("YeYouJieDiscountRate.txt")
	
	def __init__(self):
		self.levelRange = eval
		self.rate = eval


def LoadYeYouJieDiscountConfig():
	global DiscountConfigDict, LevelRangeConfigDict
	for config in YeYouJieDiscountConfig.ToClassType():
		if config.goodId in DiscountConfigDict:
			print 'GE_EXC, repeat goodId %s in DiscountConfigDict in YeYouJieDiscountConfig' % config.goodId
		DiscountConfigDict[config.goodId] = config
		

def LoadSpringFDiscountFresh():
	global RefreshConfigDict
	for config in YeYouJieDiscountFreshConfig.ToClassType():
		if config.refreshCnt in RefreshConfigDict:
			print "GE_EXC,repeat refreshCnt(%s) in RefreshConfigDict in YeYouJieDiscountConfig" % config.refreshCnt
		RefreshConfigDict[config.refreshCnt] = config.needUnbindRMB


def LoadYeYouJieDiscountRateConfig():
	global LevelRangeRandomDict
	for config in YeYouJieDiscountRateConfig.ToClassType():
		lowLevel, highlevel = config.levelRange
		for level in xrange(lowLevel, highlevel + 1):
			if level in LevelRangeRandomDict:
				print "GE_EXC,repeat level(%s) in LevelRangeRandomDict in YeYouJieDiscountConfig" % level
			LevelRangeRandomDict[level] = config.rate


if "_HasLoad" not in dir():	
	if Environment.HasLogic:
		LoadYeYouJieDiscountConfig()
		LoadSpringFDiscountFresh()
		LoadYeYouJieDiscountRateConfig()
