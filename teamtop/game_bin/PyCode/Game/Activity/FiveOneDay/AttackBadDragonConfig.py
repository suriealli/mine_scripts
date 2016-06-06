#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveOneDay.AttackBadDragonConfig")
#===============================================================================
# 注释
#===============================================================================

import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("FiveOneDay")
	
	#BAD_DRAGON_REWARD = {}			#勇斗恶龙随机奖品配置
	REWARD_RANDOM_DICT = {}			#勇斗恶龙随机奖品随机对象

class BadDragonRewardConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("BadDragonReward.txt")
	def __init__(self):
		self.level = self.GetEvalByString
		self.items = self.GetEvalByString
		
def LoadMoLingLuckyDraw():
	#global BAD_DRAGON_REWARD
	global REWARD_RANDOM_DICT
	for config in BadDragonRewardConfig.ToClassType():
		REWARD_RANDOM = Random.RandomRate()
		for coding, cnt, rate in config.items:
			REWARD_RANDOM.AddRandomItem(rate, (coding, cnt))
		for _level in xrange(config.level[0], config.level[1] + 1):
			REWARD_RANDOM_DICT[_level] = REWARD_RANDOM
		
			

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadMoLingLuckyDraw()