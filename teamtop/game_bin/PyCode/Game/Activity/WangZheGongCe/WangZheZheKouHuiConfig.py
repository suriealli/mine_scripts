#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheZheKouHuiConfig")
#===============================================================================
# 公测折扣汇 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("WangZheGongCe")
	
	DiscountConfigDict = {}
	LevelRangeRandomDict = {}	#等级区间对应的随机物品库列表
	RefreshConfigDict = {}		#刷新次数对应扣除神石数的配置字典
	MAXREFRESHCNT = 0			#刷新代价封顶次数
	

class WangZheZheKouHuiConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheZheKouHuiConfig.txt")
	def __init__(self):
		self.goodId = int
		self.item = eval
		self.limitCnt = int
		self.needUnbindRMB = int
		self.needConsumeRMB = int
		self.RMBType = int
	

class WangZheZheKouHuiRefreshConfig(TabFile.TabLine):
	'''
	折扣汇刷新
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheZheKouHuiRefresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.needUnbindRMB = int


class WangZheZheKouHuiRateConfig(TabFile.TabLine):
	'''
	折扣汇商品概率配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheZheKouHuiRate.txt")
	
	def __init__(self):
		self.levelRange = eval
		self.rate = eval


def LoadWangZheZheKouHuiConfig():
	global DiscountConfigDict, LevelRangeConfigDict
	for config in WangZheZheKouHuiConfig.ToClassType():
		if config.goodId in DiscountConfigDict:
			print 'GE_EXC, repeat goodId %s in DiscountConfigDict in WangZheZheKouHuiConfig' % config.goodId
		DiscountConfigDict[config.goodId] = config
		

def LoadWangZheZheKouHuiRefreshConfig():
	global MAXREFRESHCNT
	global RefreshConfigDict
	for config in WangZheZheKouHuiRefreshConfig.ToClassType():
		if config.refreshCnt in RefreshConfigDict:
			print "GE_EXC,repeat refreshCnt(%s) in RefreshConfigDict in WangZheZheKouHuiRefreshConfig" % config.refreshCnt
		RefreshConfigDict[config.refreshCnt] = config.needUnbindRMB
		
		if config.refreshCnt > MAXREFRESHCNT:
			MAXREFRESHCNT = config.refreshCnt

def LoadWangZheZheKouHuiRateConfig():
	global LevelRangeRandomDict
	for config in WangZheZheKouHuiRateConfig.ToClassType():
		lowLevel, highlevel = config.levelRange
		for level in xrange(lowLevel, highlevel + 1):
			if level in LevelRangeRandomDict:
				print "GE_EXC,repeat level(%s) in LevelRangeRandomDict in WangZheZheKouHuiConfig" % level
			LevelRangeRandomDict[level] = config.rate


if "_HasLoad" not in dir():	
	if Environment.HasLogic and not Environment.IsCross:
		LoadWangZheZheKouHuiConfig()
		LoadWangZheZheKouHuiRefreshConfig()
		LoadWangZheZheKouHuiRateConfig()
