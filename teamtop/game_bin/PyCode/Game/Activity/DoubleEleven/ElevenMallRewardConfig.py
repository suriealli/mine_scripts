#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.ElevenMallRewardConfig")
#===============================================================================
# 注释 @author Gaoshuai 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DoubleEleven")
	
	ElevenMallRewardDict = {}
	ElevenMallRewardList = []

class ElevenMallRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ElevenMallReward.txt")
	def __init__(self):
		self.index = int
		self.money = int
		self.percent = int
		
def LoadElevenMallRewardConfig():
	global ElevenMallRewardDict
	
	for cfg in ElevenMallRewardConfig.ToClassType():
		if cfg.index in ElevenMallRewardDict:
			print "GE_EXC, repeat index(%s) in ElevenMallRewardDict" % cfg.index
		ElevenMallRewardDict[cfg.money] = cfg.percent
		ElevenMallRewardList.append(cfg.money)
	ElevenMallRewardList.sort()
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadElevenMallRewardConfig()
