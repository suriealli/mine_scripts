#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PetLuckyFarm.PetLuckyFarmConfig")
#===============================================================================
# 宠物福田配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PetLuckyFarm")
	
	PetLuckyFarmConfigDict = {}
	PetLuckyFarmRewardConfigDict = {}
	HoeGetDict = {}
	
class PetLuckyFarmConfig(TabFile.TabLine):
	'''
	宠物福田配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("petluckyfarm.txt")
	def __init__(self):
		self.world_level = int
		self.gold_rate = self.GetEvalByString
		self.silver_rate = self.GetEvalByString
	
	def PreCoding(self):
		RDM_gold = Random.RandomRate()
		RDA_gold = RDM_gold.AddRandomItem 
		for idx, rate in self.gold_rate:
			RDA_gold(rate, idx)
		self.GoldRandomRate = RDM_gold
		
		RDM_silver = Random.RandomRate()
		RDA_silver = RDM_silver.AddRandomItem 
		for idx, rate in self.silver_rate:
			RDA_silver(rate, idx)
		self.SilverRandomRate = RDM_silver
		

class PetLuckyFarmRewardConfig(TabFile.TabLine):
	'''
	宠物福田奖励配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("rewardconfig.txt")
	def __init__(self):
		self.index = int
		self.thing = self.GetEvalByString
		self.type = int
		self.isBroadcast = int
		
class HoeGetConfig(TabFile.TabLine):
	'''
	宠物福田锄头奖励投放
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("hoeget.txt")
	def __init__(self):
		self.activityType = int
		self.fightIdx = int
		self.goldHoeOdds = int
		self.goldHoeCoding = int
		self.silverHoeOdds = int
		self.silverHoeCoding = int	
	
	
def LoadPetLuckyFarmConfig():
	global PetLuckyFarmConfigDict
	for config in PetLuckyFarmConfig.ToClassType():
		if config.world_level in PetLuckyFarmConfigDict:
			print "GE_EXC, repeat config.world_level(%s)in PetLuckyFarmConfigDict" % config.world_level
		config.PreCoding()
		PetLuckyFarmConfigDict[config.world_level] = config

def LoadPetLuckyFarmRewardConfig():
	global PetLuckyFarmRewardConfigDict
	for config in PetLuckyFarmRewardConfig.ToClassType():
		if config.index in PetLuckyFarmRewardConfigDict:
			print "GE_EXC, repeat config.index(%s)in PetLuckyFarmRewardConfigDict" % config.index
		PetLuckyFarmRewardConfigDict[config.index] = config

def LoadHoeGetConfig():
	global HoeGetDict
	for config in HoeGetConfig.ToClassType():
		if (config.activityType, config.fightIdx) in HoeGetDict:
			print "GE_EXC, repeat (config.activityType, config.fightIdx)(%s,%s) in HoeGetDict" % (config.activityType, config.fightIdx)
		HoeGetDict[(config.activityType, config.fightIdx)] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPetLuckyFarmConfig()
		LoadPetLuckyFarmRewardConfig()
		LoadHoeGetConfig()
