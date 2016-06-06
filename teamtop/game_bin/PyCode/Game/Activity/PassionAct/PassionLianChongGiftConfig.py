#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionLianChongGiftConfig")
#===============================================================================
# 激情活动连冲豪礼配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	PassionLianChongGiftConfigDict = {}


class PassionLianChongGiftConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionLianChongGift.txt")
	def __init__(self):
		self.days = int
		self.rewardItems = eval
		self.levelRange = eval


def LoadPassionLianChongGiftConfig():
	global PassionLianChongGiftConfigDict
	for config in PassionLianChongGiftConfig.ToClassType():
		startLevel, endlevel = config.levelRange
		days = config.days
		for level in xrange(startLevel, endlevel + 1):
			if (level, days) in PassionLianChongGiftConfigDict:
				print "GE_EXC,repeat (level, days)(%s,%s) in PassionLianChongGiftConfigDict" % (level, days)
			PassionLianChongGiftConfigDict[(level, days)] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassionLianChongGiftConfig()
