#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoddessCard.GoddessCardConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

GODDESS_CARD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
GODDESS_CARD_FILE_FOLDER_PATH.AppendPath("GoddessCard")

if "_HasLoad" not in dir():
	GODDESS_CARD_POSITION_ODDS = {}
	GODDESS_TREASURE_BASE = {}
	GODDESS_TREASURE_REWARD = {}
	GODDESS_CARD_REWARD = {}
	GODDESS_GROUP_LIMIT = {}
	GODDESS_GROUP_REWARD = {}
	
	HERO_CARD_TYPE = 1			#英雄卡牌类型
	GODDESS_CARD_TYPE = 2		#女神卡牌类型
	POSITION_CNT_MAX = 25		#最大位置数量
	GROUP_CARD_CNT_MAX = 3		#组合最大卡牌数量
	
	#翻牌卡牌类型随机对象
	GODDESS_CARD_TYPE_RANDOM_OBJ = Random.RandomRate()
	
	#女神卡牌宝箱随机对象
	GODDESS_TREASURE1_RANDOM_OBJ = Random.RandomRate()
	GODDESS_TREASURE2_RANDOM_OBJ = Random.RandomRate()
	GODDESS_TREASURE3_RANDOM_OBJ = Random.RandomRate()
	
	#女神卡牌随机对象
	HERO_CARD_RANDOM_OBJ = Random.RandomRate()
	GODDESS_CARD_RANDOM_OBJ = Random.RandomRate()
	
	#女神卡牌组合随机对象
	GODDESS_CARD_GROUP_RANDOM_OBJ = Random.RandomRate()
	
class GoddessCardPositionOdds(TabFile.TabLine):
	'''
	女神卡牌位置概率
	'''
	FilePath = GODDESS_CARD_FILE_FOLDER_PATH.FilePath("GoddessCardPositionOdds.txt")
	def __init__(self):
		self.posId = int
		self.turnOverOdds = int
		self.roundEightPoint = self.GetEvalByString
		
class GoddessTreasureBase(TabFile.TabLine):
	'''
	女神卡牌宝箱基础
	'''
	FilePath = GODDESS_CARD_FILE_FOLDER_PATH.FilePath("GoddessTreasureBase.txt")
	def __init__(self):
		self.treasureId = int
		self.treasureType = int
		self.activateCondition = self.GetEvalByString
		
class GoddessTreasureReward(TabFile.TabLine):
	'''
	女神卡牌宝箱奖励
	'''
	FilePath = GODDESS_CARD_FILE_FOLDER_PATH.FilePath("GoddessTreasureReward.txt")
	def __init__(self):
		self.rewardId = int
		self.treasureType = int
		self.rewardItem = self.GetEvalByString
		self.rewardOdds = int

class GoddessCardReward(TabFile.TabLine):
	'''
	女神卡牌奖励
	'''
	FilePath = GODDESS_CARD_FILE_FOLDER_PATH.FilePath("GoddessCardReward.txt")
	def __init__(self):
		self.rewardId = int
		self.cardType = int
		self.rewardItemData = self.GetEvalByString
		self.rewardOdds = int
		
	def Preprocess(self):
		self.rewardItemRandomObj = Random.RandomRate()
		for data in self.rewardItemData:
			itemCoding, itemCnt, odds = data
			self.rewardItemRandomObj.AddRandomItem(odds, (itemCoding, itemCnt))
		
class GoddessGroupReward(TabFile.TabLine):
	'''
	女神卡牌组合奖励
	'''
	FilePath = GODDESS_CARD_FILE_FOLDER_PATH.FilePath("GoddessGroupReward.txt")
	def __init__(self):
		self.groupId = int
		self.groupRewardType = int
		self.groupData = self.GetEvalByString
		self.groupOdds = int
		self.rewardItem = self.GetEvalByString
		
class GoddessCardType(TabFile.TabLine):
	'''
	女神卡牌类型
	'''
	FilePath = GODDESS_CARD_FILE_FOLDER_PATH.FilePath("GoddessCardType.txt")
	def __init__(self):
		self.cardType = int
		self.turnOverOdds = int
		
class GoddessGroupLimit(TabFile.TabLine):
	'''
	女神卡牌组合限制
	'''
	FilePath = GODDESS_CARD_FILE_FOLDER_PATH.FilePath("GoddessGroupLimit.txt")
	def __init__(self):
		self.cardIdx = int
		self.needTurnOverCardCnt = int
		
def LoadGoddessCardPositionOdds():
	global GODDESS_CARD_POSITION_ODDS
	for config in GoddessCardPositionOdds.ToClassType():
		GODDESS_CARD_POSITION_ODDS[config.posId] = config 
		
def LoadGoddessTreasureBase():
	global GODDESS_TREASURE_BASE
	for config in GoddessTreasureBase.ToClassType():
		GODDESS_TREASURE_BASE[config.treasureId] = config
		
def LoadGoddessTreasureReward():
	global GODDESS_TREASURE_REWARD
	global GODDESS_TREASURE1_RANDOM_OBJ
	global GODDESS_TREASURE2_RANDOM_OBJ
	global GODDESS_TREASURE3_RANDOM_OBJ
	
	for config in GoddessTreasureReward.ToClassType():
		GODDESS_TREASURE_REWARD[config.rewardId] = config
		if config.treasureType == 1:
			GODDESS_TREASURE1_RANDOM_OBJ.AddRandomItem(config.rewardOdds, config.rewardId)
		elif config.treasureType == 2:
			GODDESS_TREASURE2_RANDOM_OBJ.AddRandomItem(config.rewardOdds, config.rewardId)
		elif config.treasureType == 3:
			GODDESS_TREASURE3_RANDOM_OBJ.AddRandomItem(config.rewardOdds, config.rewardId)
			
def LoadGoddessCardReward():
	global GODDESS_CARD_REWARD
	global HERO_CARD_RANDOM_OBJ
	global GODDESS_CARD_RANDOM_OBJ
	
	for config in GoddessCardReward.ToClassType():
		config.Preprocess()
		GODDESS_CARD_REWARD[config.rewardId] = config
		if config.cardType == 1:
			HERO_CARD_RANDOM_OBJ.AddRandomItem(config.rewardOdds, config.rewardId)
		elif config.cardType == 2:
			GODDESS_CARD_RANDOM_OBJ.AddRandomItem(config.rewardOdds, config.rewardId)
			
def LoadGoddessGroupReward():
	global GODDESS_GROUP_REWARD
	global GODDESS_CARD_GROUP_RANDOM_OBJ
	
	for config in GoddessGroupReward.ToClassType():
		GODDESS_GROUP_REWARD[config.groupId] = config
		GODDESS_CARD_GROUP_RANDOM_OBJ.AddRandomItem(config.groupOdds, config.groupId)
		
def LoadGoddessCardType():
	global GODDESS_CARD_TYPE_RANDOM_OBJ
	for config in GoddessCardType.ToClassType():
		GODDESS_CARD_TYPE_RANDOM_OBJ.AddRandomItem(config.turnOverOdds, config.cardType)
		
def LoadGoddessGroupLimit():
	global GODDESS_GROUP_LIMIT
	for config in GoddessGroupLimit.ToClassType():
		GODDESS_GROUP_LIMIT[config.cardIdx] = config
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGoddessCardPositionOdds()
		LoadGoddessTreasureBase()
		LoadGoddessTreasureReward()
		LoadGoddessCardReward()
		LoadGoddessGroupReward()
		LoadGoddessCardType()
		LoadGoddessGroupLimit()
		
		