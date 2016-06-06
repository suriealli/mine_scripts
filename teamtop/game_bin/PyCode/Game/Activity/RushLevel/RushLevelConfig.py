#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RushLevel.RushLevelConfig")
#===============================================================================
# 冲级排名配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

RUSH_LEVEL_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
RUSH_LEVEL_FILE_FOLDER_PATH.AppendPath("RushLevel")

if "_HasLoad" not in dir():
	RUSH_LEVEL_REWARD = {}
	
class RushLevelReward(TabFile.TabLine):
	'''
	冲级奖励
	'''
	FilePath = RUSH_LEVEL_FILE_FOLDER_PATH.FilePath("RushLevelReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rewardHeroNumber = int
		self.rewardItemList = self.GetEvalByString

def LoadRushLevelReward():
	global RUSH_LEVEL_REWARD
	for config in RushLevelReward.ToClassType():
		RUSH_LEVEL_REWARD[config.rewardId] = config 

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRushLevelReward()
		