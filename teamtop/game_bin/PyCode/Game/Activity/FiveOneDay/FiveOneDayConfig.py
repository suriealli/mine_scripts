#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveOneDay.FiveOneDayConfig")
#===============================================================================
# 五一活动配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FIVEONE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FIVEONE_FILE_FOLDER_PATH.AppendPath("FiveOneDay")
	
	FIVEONE_LOGIN_REWARD = None	#登录配置
	FIVEONE_COST_REWARD = {}	#消费配置
	
class FiveOneLoginReward(TabFile.TabLine):
	'''
	五一登录奖励
	'''
	FilePath = FIVEONE_FILE_FOLDER_PATH.FilePath("FiveOneLoginReward.txt")
	def __init__(self):
		self.itemRewards = self.GetEvalByString
		
class FiveOneCostReward(TabFile.TabLine):
	'''
	五一消费奖励
	'''
	FilePath = FIVEONE_FILE_FOLDER_PATH.FilePath("FiveOneCostReward.txt")
	def __init__(self):
		self.index = int
		self.costRMB = int
		self.itemReward = self.GetEvalByString
		
def LoadFiveOneLoginReward():
	global FIVEONE_LOGIN_REWARD
	
	for cfg in FiveOneLoginReward.ToClassType():
		FIVEONE_LOGIN_REWARD = cfg
		
def LoadFiveOneCostReward():
	global FIVEONE_COST_REWARD
	
	for cfg in FiveOneCostReward.ToClassType():
		if cfg.index in FIVEONE_COST_REWARD:
			print "GE_EXC, repeat index(%s) in LoadFiveOneCostReward" % cfg.index
		FIVEONE_COST_REWARD[cfg.index] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadFiveOneLoginReward()
		LoadFiveOneCostReward()