#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RechargeEveryday.RechargeEverydayConfig")
#===============================================================================
# 今日首充配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("RechargeEveryDay")
	
	RechargeEverydayConfigDict = {}


class RechargeEverydayConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("RechargeEveryDay.txt")
	def __init__(self):
		self.level = int
		self.items = eval


def LoadRechargeEverydayConfig():
	global RechargeEverydayConfigDict
	for config in RechargeEverydayConfig.ToClassType():
		if config.level in RechargeEverydayConfigDict:
			print "GE_EXC, repeat level(%s) in RechargeEverydayConfigDict" % config.level
		RechargeEverydayConfigDict[config.level] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRechargeEverydayConfig()
