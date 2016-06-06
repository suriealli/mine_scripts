#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHZReward.QQHZConfig")
#===============================================================================
#QQ黄钻配置 腾讯 繁体
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if '_HasLoad' not in dir():
	QQHZ_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	QQHZ_FILE_FOLDER_PATH.AppendPath("QQHZ")
	QQHZ_DAILY_REWARD  = {}
	QQHZ_NOVICE_REWARD = {}
	QQHZ_LEVEL_REWARD  = {}
	DAY_3366_REWARD = {}
	QQHZ_DAILY_REWARD_DICT = {}
	
class QQHZDaily(TabFile.TabLine):
	'''
	黄钻每日奖励配置
	'''
	FilePath = QQHZ_FILE_FOLDER_PATH.FilePath("QQHZdaily.txt")
	def __init__(self):
		self.Level		= int
		self.LevelEvl1	= self.GetEvalByString
		self.rewardId1	= int
		self.LevelEvl2	= self.GetEvalByString
		self.rewardId2	= int
		self.LevelEvl3	= self.GetEvalByString
		self.rewardId3	= int
		self.LevelEvl4	= self.GetEvalByString
		self.rewardId4	= int
		self.LevelEvl5	= self.GetEvalByString
		self.rewardId5	= int
		self.LevelEvl6	= self.GetEvalByString
		self.rewardId6	= int
		self.LevelEvl7	= self.GetEvalByString
		self.rewardId7	= int
		self.LevelEvl8	= self.GetEvalByString
		self.rewardId8	= int
		
class DailyReward(TabFile.TabLine):
	'''
	每日礼包奖励配置
	'''
	FilePath = QQHZ_FILE_FOLDER_PATH.FilePath("DailyReward.txt")
	def __init__(self):
		self.rewardId 			= int
		self.bindRMB 			= int
		self.money 				= int
		self.HZrewards			= self.GetEvalByString
		self.HZYearsRMB			 = int
		self.HZYearsRewards		= self.GetEvalByString
		self.LZrewards			= self.GetEvalByString
		self.LZYearsRewards		= self.GetEvalByString
		self.LZHHReward			= self.GetEvalByString
		
class QQHZNovice(TabFile.TabLine):
	'''
	黄钻新手奖励配置表
	'''	
	FilePath = QQHZ_FILE_FOLDER_PATH.FilePath("QQHZnovice.txt")
	def __init__(self):
		self.Level = int
		self.HZrewards	= self.GetEvalByString
		self.LZrewards	= self.GetEvalByString
		self.bindRMB	= int
		self.money		= int
		
class QQHZLevel(TabFile.TabLine):
	'''
	黄钻等级礼包
	'''
	FilePath = QQHZ_FILE_FOLDER_PATH.FilePath("QQHZlevel.txt")
	def __init__(self):
		self.nowPackIndex	= int
		self.nextPackIndex	= int
		self.level			= int
		self.HZitems		= self.GetEvalByString
		self.LZitems		= self.GetEvalByString
		self.addTarot		= int

class Day3366Reward(TabFile.TabLine):
	'''
	3366每日礼包
	'''
	FilePath = QQHZ_FILE_FOLDER_PATH.FilePath("Day3366Reward.txt")
	def __init__(self):
		self.rewardId	= int
		self.MinLevel	= int
		self.MaxLevel	= int
		self.items		= self.GetEvalByString
		self.money		= int
		self.bindRMB	= int

def LoadQQHZDaily():
	global QQHZ_DAILY_REWARD
	for config in QQHZDaily.ToClassType():
		if config.Level in QQHZ_DAILY_REWARD:
			print "GE_EXC, repeat level in LoadQQHZDaily (%s)" % config.Level
		DAILY_REWARD = QQHZ_DAILY_REWARD[config.Level] = {}
		if config.rewardId1 not in DAILY_REWARD:
			DAILY_REWARD[config.rewardId1] = config.LevelEvl1
		if config.rewardId2 not in DAILY_REWARD:
			DAILY_REWARD[config.rewardId2] = config.LevelEvl2
		if config.rewardId3 not in DAILY_REWARD:
			DAILY_REWARD[config.rewardId3] = config.LevelEvl3
		if config.rewardId4 not in DAILY_REWARD:
			DAILY_REWARD[config.rewardId4] = config.LevelEvl4
		if config.rewardId5 not in DAILY_REWARD:
			DAILY_REWARD[config.rewardId5] = config.LevelEvl5
		if config.rewardId6 not in DAILY_REWARD:
			DAILY_REWARD[config.rewardId6] = config.LevelEvl6
		if config.rewardId7 not in DAILY_REWARD:
			DAILY_REWARD[config.rewardId7] = config.LevelEvl7
		if config.rewardId8 not in DAILY_REWARD:
			DAILY_REWARD[config.rewardId8] = config.LevelEvl8
			
def LoadQQNovice():
	global QQHZ_NOVICE_REWARD
	for config in QQHZNovice.ToClassType():
		if config.Level in QQHZ_NOVICE_REWARD:
			print "GE_EXC, repeat level in LoadQQHZnovice (%s)" % config.Level
		QQHZ_NOVICE_REWARD[config.Level] = config

def LoadQQLevel():
	global QQHZ_LEVEL_REWARD
	for config in QQHZLevel.ToClassType():
		if config.nowPackIndex in QQHZ_LEVEL_REWARD:
			print "GE_EXC, repeat nowPackIndex in QQHZLevel(%s)" % config.nowPackIndex
		QQHZ_LEVEL_REWARD[config.nowPackIndex] = config

def LoadDay3366Reward():
	global DAY_3366_REWARD
	for config in Day3366Reward.ToClassType():
		if config.rewardId in DAY_3366_REWARD:
			print "GE_EXC, repeat rewardId in Day3366Reward(%s)" % config.rewardId
		DAY_3366_REWARD[config.rewardId] = config

def LoadDayReward():
	global QQHZ_DAILY_REWARD_DICT
	for config in DailyReward.ToClassType():
		if config.rewardId in QQHZ_DAILY_REWARD_DICT:
			print "GE_EXC, repeat rewardId in DailyReward(%s)" % config.rewardId
		QQHZ_DAILY_REWARD_DICT[config.rewardId] = config
	
if '_HasLoad' not in dir():
	if Environment.HasLogic:
		LoadQQHZDaily()
		LoadQQNovice()
		LoadQQLevel()
		LoadDay3366Reward()
		LoadDayReward()