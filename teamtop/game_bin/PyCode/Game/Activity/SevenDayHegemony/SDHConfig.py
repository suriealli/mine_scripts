#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenDayHegemony.SDHConfig")
#===============================================================================
# 七日争霸活动配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("SevenDayHegemony")
	
	#目标{(type, index) --> ...}
	SDHTargetConfigDict = {}
	#排名{(type, rank) --> ...}
	SDHRankConfigDict = {}
	
class SDHTargetConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SDHTarget.txt")
	def __init__(self):
		self.targetType = int
		self.targetIndex = int
		self.param = eval
		self.tarot = eval
		self.item = eval
		self.bindRMB = int
		self.unbindRMB_S = int

	
class SDHRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SDHRank.txt")
	def __init__(self):
		self.targetType = int
		self.rank = int
		self.money = int
		self.tarot = eval
		self.item = eval
		self.bindRMB = int
		self.money = int
		self.contribution = int
	
	
def LoadSDHTargetConfig():
	global SDHTargetConfigDict
	for config in SDHTargetConfig.ToClassType():
		if (config.targetType, config.targetIndex) in SDHTargetConfigDict:
			print 'GE_EXC, repeat targetType %s, targetIndex %s in SDHTargetConfigDict' % (config.targetType, config.targetIndex)
		SDHTargetConfigDict[(config.targetType, config.targetIndex)] = config
	
	
def LoadSDHRankConfig():
	global SDHRankConfigDict
	for config in SDHRankConfig.ToClassType():
		if (config.targetType, config.rank) in SDHRankConfigDict:
			print 'GE_EXC, repeat targetType %s, rank %s in SDHRankConfigDict' % (config.targetType, config.rank)
		SDHRankConfigDict[(config.targetType, config.rank)] = config
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSDHTargetConfig()
		LoadSDHRankConfig()

