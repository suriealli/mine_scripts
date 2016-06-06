#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TheMammon.TheMammonConfig")
#===============================================================================
# 天降财神配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("TheMammon")
	
	TheMammonConfigDict = {}
	

class TheMammonConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("TheMammon.txt")
	def __init__(self):
		self.Index = int
		self.chargeValue = eval
		self.rebate = eval


def LoadTheMammonConfig():
	global TheMammonConfigDict
	for config in TheMammonConfig.ToClassType():
		if config.Index in TheMammonConfigDict:
			print "GE_EXC,repeat Index(%s) in TheMammonConfigDict" % config.Index
		TheMammonConfigDict[config.Index] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTheMammonConfig()
