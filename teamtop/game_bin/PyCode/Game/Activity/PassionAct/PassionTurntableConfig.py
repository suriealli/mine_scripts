#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTurntableConfig")
#===============================================================================
# 激情活动幸运转盘配置(七夕活动新增)
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	TurntableLevelConfigDict = {}
	TurntableSchemeConfigDict = {}
	TurntablePriceConfigDict = {}
	

class TurntableLevelConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTutableLevel.txt")
	def __init__(self):
		self.roleLevel	 = int
		self.schemeList = eval


class TurntableSchemeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTutableAwardScheme.txt")
	def __init__(self):
		self.Index	 = int
		self.RateList = eval
		self.goodItems = eval

class TurntablePriceConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTutablePrice.txt")
	def __init__(self):
		self.times = int
		self.needCoding	 = int
		self.needCnt	 = int
		self.needName = str


def LoadTurntableLevelConfig():
	global TurntableLevelConfigDict
	for config in TurntableLevelConfig.ToClassType():
		if config.roleLevel in TurntableLevelConfigDict:
			print "GE_EXC,repeat roleLevel(%s) in TurntableLevelConfigDict in PassionTurntableConfig" % config.roleLevel
		TurntableLevelConfigDict[config.roleLevel] = config


def LoadTurntableSchemeConfig():
	global TurntableSchemeConfigDict
	for config in TurntableSchemeConfig.ToClassType():
		if config.Index in TurntableSchemeConfigDict:
			print "GE_EXC,repeat Index(%s) in TurntableSchemeConfigDict in PassionTurntableConfig" % config.Index
		TurntableSchemeConfigDict[config.Index] = config


def LoadTurntablePriceConfig():
	global TurntablePriceConfigDict
	for config in TurntablePriceConfig.ToClassType():
		if config.times in TurntablePriceConfigDict:
			print "GE_EXC,repeat times(%s) in TurntablePriceConfigDict in PassionTurntableConfig" % config.times
		TurntablePriceConfigDict[config.times] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTurntableLevelConfig()
		LoadTurntableSchemeConfig()
		LoadTurntablePriceConfig()
