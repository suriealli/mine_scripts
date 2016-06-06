#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DragonEgg.DragonEggConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

DRAGON_EGG_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
DRAGON_EGG_FILE_FOLDER_PATH.AppendPath("DragonEgg")

if "_HasLoad" not in dir():
	EGG_REWARD = {}
	GOLD_EGG_CONSUME = {}
	ACTIVITY_EGG = {}
	
class EggReward(TabFile.TabLine):
	'''
	龙蛋奖励配置
	'''
	FilePath = DRAGON_EGG_FILE_FOLDER_PATH.FilePath("EggReward.txt")
	def __init__(self):
		self.eggType = int
		self.minLevel = int
		self.maxLevel = int
		self.rewardItemList = self.GetEvalByString
		
class GoldEggConsume(TabFile.TabLine):
	'''
	砸金龙蛋消耗配置
	'''
	FilePath = DRAGON_EGG_FILE_FOLDER_PATH.FilePath("GoldEggConsume.txt")
	def __init__(self):
		self.cnt = int
		self.needRMB = int
		
class ActivityEgg(TabFile.TabLine):
	'''
	活动龙蛋掉落配置
	'''
	FilePath = DRAGON_EGG_FILE_FOLDER_PATH.FilePath("ActivityEgg.txt")
	def __init__(self):
		self.activityType = int
		self.fightIdx = int
		self.goldEggOdds = int
		self.goldEggCoding = int
		self.silverEggOdds = int
		self.silverEggCoding = int

def LoadEggBase():
	global EGG_REWARD
	for config in EggReward.ToClassType():
		randomObj = Random.RandomRate()#随机对象
		for coding, cnt, odds, isHearsay in config.rewardItemList:
			randomObj.AddRandomItem(odds, (coding, cnt, isHearsay))
		
		if config.eggType not in EGG_REWARD:
			EGG_REWARD[config.eggType] = {}
		d = EGG_REWARD[config.eggType]
		for level in xrange(config.minLevel, config.maxLevel + 1):
			d[level] = randomObj
			
def LoadGoldEggConsume():
	global GOLD_EGG_CONSUME
	for config in GoldEggConsume.ToClassType():
		GOLD_EGG_CONSUME[config.cnt] = config
		
def LoadActivityEgg():
	global ACTIVITY_EGG
	for config in ActivityEgg.ToClassType():
		ACTIVITY_EGG[(config.activityType, config.fightIdx)] = config
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadEggBase()
		LoadGoldEggConsume()
		LoadActivityEgg()
		