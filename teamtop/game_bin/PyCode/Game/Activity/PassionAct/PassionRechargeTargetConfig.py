#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionRechargeTargetConfig")
#===============================================================================
# 每日购买神石返好礼配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	PassionRechargeTargetCfgDict = {}


class PassionRechargeTargetConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionRechargeTarget.txt")
	def __init__(self):
		self.index = int
		self.rewardItems = eval
		self.levelRange = eval
		self.needRecharge = int


def LoadPassionRechargeTargetConfig():
	global PassionRechargeTargetCfgDict
	for config in PassionRechargeTargetConfig.ToClassType():
		startLevel, endlevel = config.levelRange
		index = config.index
		for level in xrange(startLevel, endlevel + 1):
			if (level, index) in PassionRechargeTargetCfgDict:
				print "GE_EXC,repeat (level, index)(%s,%s) in PassionRechargeTargetCfgDict" % (level, index)
			PassionRechargeTargetCfgDict[(level, index)] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassionRechargeTargetConfig()
		
