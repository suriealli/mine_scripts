#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RuneWheel.RuneWheelConfig")
#===============================================================================
# 符文宝轮配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	RuneWheel_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	RuneWheel_FILE_FOLDER_PATH.AppendPath("RuneWheel")
	RANDOM_ITEM = Random.RandomRate()
	RANDOM_ITEM_Ten = Random.RandomRate()
	
class RuneWheelConfig(TabFile.TabLine):
	'''
	 符文宝轮配置表
	'''
	FilePath = RuneWheel_FILE_FOLDER_PATH.FilePath("runewheellib.txt")
	def __init__(self):
		self.itemcode   = int
		self.rate   = int

class RuneWheelTenConfig(TabFile.TabLine):
	'''
	 符文宝轮次数为10的整数倍时的配置
	'''	
	FilePath = RuneWheel_FILE_FOLDER_PATH.FilePath("RuneTenTimes.txt")
	def __init__(self):
		self.itemlist = self.GetEvalByString
		self.rate = int

def LoadRuneWheelConfig():
	'''
	 读取符文宝轮配置表
	'''
	global RANDOM_ITEM
	for config in RuneWheelConfig.ToClassType():
		if (config.rate, config.itemcode) in RANDOM_ITEM.randomList:
			print "GE_EXC, repeat (config.rate, config.itemcode)(%s,%s) while LoadRuneWheelConfig" % (config.rate, config.itemcode)
		RANDOM_ITEM.AddRandomItem(config.rate, config.itemcode)

def LoadRuneWheelTenConfig():
	global RANDOM_ITEM_Ten
	for config in RuneWheelTenConfig.ToClassType():
		RANDOM_ITEM_Ten.AddRandomItem(config.rate, config.itemlist)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRuneWheelConfig()
		LoadRuneWheelTenConfig()
