#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionXiaoFeiMaiDanConfig")
#===============================================================================
# 你消费我买单配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	DayIndexConfigDict = {}
	XiaoFeiMaiDanConfigDict = {}
	

class XiaoFeiMaiDanConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionXiaoFeiMaiDan.txt")
	def __init__(self):
		self.dayIndex = int
		self.theDate = eval
		self.startBackDayIndex = int
		self.endBackDayIndex = int
		self.percent = int
		self.maxBack = int
		self.needRecordConsume = int


def LoadXiaoFeiMaiDanConfig():
	global DayIndexConfigDict
	global XiaoFeiMaiDanConfigDict
	for config in XiaoFeiMaiDanConfig.ToClassType():
		if config.dayIndex in XiaoFeiMaiDanConfigDict:
			print "GE_EXC,repeat dayIndex(%s) in XiaoFeiMaiDanConfigDict in PassionXiaoFeiMaiDanConfig" % config.dayIndex
		XiaoFeiMaiDanConfigDict[config.dayIndex] = config
		
		if config.theDate in DayIndexConfigDict:
			print "GE_EXC,repeat theDate(%s) in DayIndexConfigDict in PassionXiaoFeiMaiDanConfig" % config.theDate
		DayIndexConfigDict[config.theDate] = config.dayIndex


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadXiaoFeiMaiDanConfig()
