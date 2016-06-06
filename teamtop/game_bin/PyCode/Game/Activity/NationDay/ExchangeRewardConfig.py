#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationDay.ExchangeRewardConfig")
#===============================================================================
# 国庆奖励兑换配置
#===============================================================================

import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("NationDay")
	
	ND_EXCHANGE_REWARD_DICT = {}	#国庆奖励兑换配置字典{exchangeType：cfg}
	
class ExchangeReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ExchangeReward.txt")
	def __init__(self):
		self.exchangeType = int		#兑换类型 
		self.costItem = eval		#消耗物品
		self.gainItem = eval		#获得物品
		self.broadcast = int 		#是否公告

def LoadExchangeConfig():
	global ND_EXCHANGE_REWARD_DICT
	for cfg in ExchangeReward.ToClassType():
		if cfg.exchangeType in ND_EXCHANGE_REWARD_DICT:
			print "GE_EXC,repeat exchangeType(%s) in ND_EXCHANGE_REWARD_DICT" % cfg.exchangeType
		ND_EXCHANGE_REWARD_DICT[cfg.exchangeType] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadExchangeConfig()	