#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionConsumeTargetConfig")
#===============================================================================
# 每日消费充值神石返好礼配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	PassionConsumeTargetCfgDict = {}


class PassionConsumeTargetConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionConsumeTarget.txt")
	def __init__(self):
		self.index = int
		self.rewardItems = eval
		self.levelRange = eval
		self.needConsume = int


def LoadPassionConsumeTargetConfig():
	global PassionConsumeTargetCfgDict
	for config in PassionConsumeTargetConfig.ToClassType():
		startLevel, endlevel = config.levelRange
		index = config.index
		for level in xrange(startLevel, endlevel + 1):
			if (level, index) in PassionConsumeTargetCfgDict:
				print "GE_EXC,repeat (level, index)(%s,%s) in PassionConsumeTargetCfgDict" % (level, index)
			PassionConsumeTargetCfgDict[(level, index)] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassionConsumeTargetConfig()
