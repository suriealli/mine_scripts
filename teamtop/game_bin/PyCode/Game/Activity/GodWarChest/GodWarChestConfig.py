#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GodWarChest.GodWarChestConfig")
#===============================================================================
# 战神宝箱配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	GODWARCHEST_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	GODWARCHEST_FILE_FOLDER_PATH.AppendPath("GodWarChest")
	
	GOLD_WAR_CHEST_DICT = {}	#宝箱配置
	CHEST_REWARD_DICT = {}		#每个宝箱拥有的奖励
	CHEST_REWARD_DICT = {}		#宝箱奖励配置
	CHEST_MIN_LEVEL_LIST = []	#最小等级列表
	
class GoldWarChestConfig(TabFile.TabLine):
	'''
	宝箱配置
	'''
	FilePath = GODWARCHEST_FILE_FOLDER_PATH.FilePath("GoldWarChestConfig.txt")
	def __init__(self):
		self.index = int
		self.needRMB = int
		self.needFillRMB = int
		self.extendreward = int
		
		self.needDay1 = int
		self.dayreward1 = int
		
		self.needDay2 = int
		self.dayreward2 = int
		
		self.needDay3 = int
		self.dayreward3 = int
		
		self.needDay4 = int
		self.dayreward4 = int
		
		self.needDay5 = int
		self.dayreward5 = int
		
		self.needDay6 = int
		self.dayreward6 = int
				
		self.needDay7 = int
		self.dayreward7 = int
		
		self.needDay8 = int
		self.dayreward8 = int
		
		self.needDay9 = int
		self.dayreward9 = int
		
		self.needDay10 = int
		self.dayreward10 = int
		
class ChestReward(TabFile.TabLine):
	'''
	奖励配置
	'''
	FilePath = GODWARCHEST_FILE_FOLDER_PATH.FilePath("ChestReward.txt")
	def __init__(self):
		self.rewardId = int
		self.MinLevel = int
		self.Itemrewards = self.GetEvalByString
		self.bindRMB = int
		
def LoadGoldWarChestConfig():
	global GOLD_WAR_CHEST_DICT
	
	for cfg in GoldWarChestConfig.ToClassType():
		if cfg.index in GOLD_WAR_CHEST_DICT:
			print "GE_EXC,repeat index(%s) in LoadGoldWarChestConfig" % cfg.index
		GOLD_WAR_CHEST_DICT[cfg.index] = cfg
			
def LoadChestReward():
	global CHEST_REWARD_DICT
	global CHEST_MIN_LEVEL_LIST
	for cfg in ChestReward.ToClassType():
		key = (cfg.rewardId, cfg.MinLevel)
		if key in CHEST_REWARD_DICT:
			print "GE_EXC, repeat rewardId(%s) and minLevel(%s) in LoadChestReward" % (cfg.rewardId, cfg.MinLevel)
		CHEST_REWARD_DICT[key] = cfg
		CHEST_MIN_LEVEL_LIST.append(cfg.MinLevel)
	CHEST_MIN_LEVEL_LIST = list(set(CHEST_MIN_LEVEL_LIST))
	CHEST_MIN_LEVEL_LIST.sort()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGoldWarChestConfig()
		LoadChestReward()
		