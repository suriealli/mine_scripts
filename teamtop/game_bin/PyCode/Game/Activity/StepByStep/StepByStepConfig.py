#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.StepByStep.StepByStepConfig")
#===============================================================================
# 步步高升配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("StepByStep")
	
	StepByStepConfigDict = {}
	
class StepByStepConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("stepbystep.txt")
	def __init__(self):
		self.index = int
		self.price = int
		self.name = str
		self.items = self.GetEvalByString
		self.unbindRMB = int
		self.bindRMB = int
		self.money = int
		self.isBroadcast = int

def LoadStepByStepConfig():
	global StepByStepConfigDict
	for config in StepByStepConfig.ToClassType():
		if config.index in StepByStepConfigDict:
			print "GE_EXC,repeat config.index(%s) in StepByStepConfigDict" % config.index
		StepByStepConfigDict[config.index] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadStepByStepConfig()
