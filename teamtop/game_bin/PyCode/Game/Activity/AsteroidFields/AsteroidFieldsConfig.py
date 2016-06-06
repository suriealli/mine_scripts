#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.AsteroidFields.AsteroidFieldsConfig")
#===============================================================================
# 魔域星宫配置表
#===============================================================================

import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random
from Common.Other.GlobalPrompt import YYAntiNoReward


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("AsteroidFields")
	
	AsteroidFieldsConfig_Dict = {}
	AsteroidFieldsGuanka_Dict = {}
	
class AsteroidFieldsConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("AsteroidFields.txt")
	def __init__(self):
		self.AFIndex = int
		self.FightType = int
		self.MonsterId = int
		self.MoneyToReward = int
		self.ItemsToReward = self.GetEvalByString
		self.RandomReward = self.GetEvalByString
		self.RandomRewardRate = self.GetEvalByString
		self.MoneyToReward_fcm = int                  #关卡必奖金币
		self.ItemsToReward_fcm = self.GetEvalByString #关卡必奖物品
		
	def Precoding(self):
		self.RandomRate = Random.RandomRate()
		for item in self.RandomRewardRate:
			self.RandomRate.AddRandomItem(*item)
	
	
	def GetRewardList(self, flag):
		#YY防沉迷对奖励特殊处理
		if flag:
			tmpreward = self.ItemsToReward_fcm
		else:
			tmpreward = self.ItemsToReward
			
		randomCnt = self.RandomRate.RandomOne()
		if randomCnt:
			return tmpreward + [(self.RandomReward, randomCnt)]
		else:
			return tmpreward 


class AsteroidFieldsGuanka(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("AsteroidFieldsGuanka.txt")
	def __init__(self):
		self.AFId = int
		self.FirstIndex = int
		self.LastIndex = int
		self.LevelNeeded = int

def LoadAsteroidFieldsConfig():
	global AsteroidFieldsConfig_Dict
	for config in AsteroidFieldsConfig.ToClassType():
		if config.AFIndex in AsteroidFieldsConfig_Dict:
			print "GE_EXC, repeat AFIndex(%s) in AsteroidFieldsConfig_Dict" % config.AFIndex
		AsteroidFieldsConfig_Dict[config.AFIndex] = config
		config.Precoding()



def LoadAsteroidFieldsGuanka():
	global AsteroidFieldsGuanka_Dict
	for config in AsteroidFieldsGuanka.ToClassType():
		if config.AFId in AsteroidFieldsGuanka_Dict:
			print "GE_EXC, repeat AFId(%s) in AsteroidFieldsGuanka_Dict" % config.AFId
		AsteroidFieldsGuanka_Dict[config.AFId] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadAsteroidFieldsConfig()
		LoadAsteroidFieldsGuanka()
		
		
