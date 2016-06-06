#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GodsTreasure.GodsTreasureConfig")
#===============================================================================
# 众神秘宝配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

GODS_TREASURE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
GODS_TREASURE_FILE_FOLDER_PATH.AppendPath("GodsTreasure")

if "_HasLoad" not in dir():
	GODS_TREASURE_BASE = {}
	GODS_TREASURE_REWARD = {}
	TREASURE_DETECTOR = {}
	
class GodsTreasureBase(TabFile.TabLine):
	'''
	众神秘宝基础配置表对象
	'''
	FilePath = GODS_TREASURE_FILE_FOLDER_PATH.FilePath("GodsTreasureBase.txt")
	def __init__(self):
		self.searchType = int
		self.needMoney = int
		self.needItemCoding = int
		self.rewardData = self.GetEvalByString
		
	def init_random(self):
		self.randomObj = Random.RandomRate()
		for rewardId, odds in self.rewardData:
			self.randomObj.AddRandomItem(odds, rewardId)

class GodsTreasureReward(TabFile.TabLine):
	'''
	众神秘宝奖励配置表对象
	'''
	FilePath = GODS_TREASURE_FILE_FOLDER_PATH.FilePath("GodsTreasureReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rewardItemCoding = int
		self.rewardItemCnt = int
		self.isHearsay = int
		
class TreasureDetector(TabFile.TabLine):
	'''
	探宝器掉落配置
	'''
	FilePath = GODS_TREASURE_FILE_FOLDER_PATH.FilePath("TreasureDetector.txt")
	def __init__(self):
		self.activityType = int
		self.fightIdx = int
		self.dropOdds = int
		self.dropItemCoding = int
		self.needLevel = int

def LoadGodsTreasureBase():
	global GODS_TREASURE_BASE
	for config in GodsTreasureBase.ToClassType():
		config.init_random()
		GODS_TREASURE_BASE[config.searchType] = config 
		
def LoadGodsTreasureReward():
	global GODS_TREASURE_REWARD
	for config in GodsTreasureReward.ToClassType():
		GODS_TREASURE_REWARD[config.rewardId] = config 
		
def LoadTreasureDetector():
	global TREASURE_DETECTOR
	for config in TreasureDetector.ToClassType():
		TREASURE_DETECTOR[(config.activityType, config.fightIdx)] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGodsTreasureBase()
		LoadGodsTreasureReward()
		LoadTreasureDetector()
	
