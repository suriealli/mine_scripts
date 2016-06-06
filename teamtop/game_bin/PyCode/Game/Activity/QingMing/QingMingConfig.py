#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QingMingConfig")
#===============================================================================
# 注释
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QingMing")
	
	SenvenDayConsumeConfigDict = {}
	SenvenDayConsumeLevelRangeDict = {}
	
	SenvenDayRechargeConfigDict = {}
	SenvenDayRechargeLevelRangeDict = {}
	
	QingMingExchangeConfigDict = {}

class SenvenDayConsumeConfig(TabFile.TabLine):
	'''
	七日消费活动配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingSevenDayConsume.txt")
	def __init__(self):
		self.key = eval
		self.levelRangeID = int
		self.levelRange = eval
		self.needConsumeUnbindRMB = int
		self.items = eval


class SenvenDayRechargeConfig(TabFile.TabLine):
	'''
	七日充值活动配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingSevenDayRecharge.txt")
	def __init__(self):
		self.key = eval
		self.levelRangeID = int
		self.levelRange = eval
		self.needDayBuyUnbindRMB_Q = int
		self.items = eval


class QingMingExchangeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingExchange.txt")
	def __init__(self):
		self.coding = int
		self.needCoding = int
		self.needItemCnt = int
		self.limitCnt = int
		self.needLevel = int
		self.needWorldLevel = int


def LoadSenvenDayConsumeConfig():
	global SenvenDayConsumeConfigDict, SenvenDayConsumeLevelRangeDict
	for config in SenvenDayConsumeConfig.ToClassType():
		if config.key in SenvenDayConsumeConfigDict:
			print "GE_EXC,repeat key(%s,%s) in SenvenDayConsumeConfigDict" % (config.key, config.levelRangeID)
		SenvenDayConsumeConfigDict[(config.key, config.levelRangeID)] = config
		
		for i in xrange(config.levelRange[0], config.levelRange[1] + 1):
			if i in SenvenDayRechargeLevelRangeDict:
				if config.levelRangeID != SenvenDayRechargeLevelRangeDict[i]:
					print "GE_EXC,error while set levelRangeID in SenvenDayConsumeConfigDict for level(%s)" % i
			SenvenDayConsumeLevelRangeDict[i] = config.levelRangeID
	

def LoadSenvenDayRechargeConfig():
	global SenvenDayRechargeConfigDict, SenvenDayRechargeLevelRangeDict
	
	for config in SenvenDayRechargeConfig.ToClassType():
		if config.key in SenvenDayRechargeConfigDict:
			print "GE_EXC,repeat key(%s,%s) in SenvenDayRechargeConfigDict" % (config.key, config.levelRangeID)
		SenvenDayRechargeConfigDict[(config.key, config.levelRangeID)] = config
		
		for i in xrange(config.levelRange[0], config.levelRange[1] + 1):
			if i in SenvenDayRechargeLevelRangeDict:
				if config.levelRangeID != SenvenDayRechargeLevelRangeDict[i]:
					print "GE_EXC,error while set levelRangeID in SenvenDayRechargeLevelRangeDict for level(%s)" % i
			SenvenDayRechargeLevelRangeDict[i] = config.levelRangeID


def LoadQingMingExchangeConfig():
	global QingMingExchangeConfigDict
	for config in QingMingExchangeConfig.ToClassType():
		if config.coding in QingMingExchangeConfigDict:
			print "GE_EXC, repeat config.coding(%s) in QingMingExchangeConfigDict " % config.coding
		QingMingExchangeConfigDict[config.coding] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSenvenDayConsumeConfig()
		LoadSenvenDayRechargeConfig()
		LoadQingMingExchangeConfig()
