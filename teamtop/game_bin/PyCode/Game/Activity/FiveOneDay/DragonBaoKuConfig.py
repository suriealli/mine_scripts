#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveOneDay.DragonBaoKuConfig")
#===============================================================================
# 神龙宝库活动配置
#===============================================================================

import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("FiveOneDay")
	
	REWARD_ITEM_DICT = {}

class RewardConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DragonBaoKu.txt")
	def __init__(self):
		self.itemCoding = int
		self.dragonBall = int
		self.maxNum = int
		self.needItemCoding = int
		self.needLevel = int
	
def LoadRewardConfig():
	global RewardConfigDict
	for config in RewardConfig.ToClassType():
		REWARD_ITEM_DICT[config.itemCoding] = config
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRewardConfig()