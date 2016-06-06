#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LimitChest.LimitChestConfig")
#===============================================================================
# 限次宝箱配置表
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util.Random import RandomRate

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("LimitChest")
	
	LimitChestConfigDict = {}
	
class LimitChestConfig(TabFile.TabLine):
	'''
	限次宝箱配置表
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("LimitChest.txt")
	def __init__(self):
		self.ChestCode = int
		self.Reward = self.GetEvalByString
		self.FreeCnt = int
		self.Cost = int
		self.RedHand = self.GetEvalByString
	def PreCoding(self):
		RDM = RandomRate()
		for thingtype , thing, rate in self.Reward:
			RDM.AddRandomItem(rate, (thingtype, thing))
		self.RandomRate = RDM

def LoadLimitChestConfig():
	global LimitChestConfigDict
	for config in LimitChestConfig.ToClassType():
		if config.ChestCode in LimitChestConfigDict:
			print "GE_EXC, repeat ChestCode(%s) in LimitChestConfig" % config.ChestCode
		config.PreCoding()
		LimitChestConfigDict[config.ChestCode] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLimitChestConfig()
