#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.DoubleTwelveConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

DOUBLE_TWELVE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
DOUBLE_TWELVE_FILE_FOLDER_PATH.AppendPath("DoubleTwelve")

if "_HasLoad" not in dir():
	REBATE = {}
	RICH_RANK_REWARD = {}
	
class Rebate(TabFile.TabLine):
	'''
	返利领不停配置对象
	'''
	FilePath = DOUBLE_TWELVE_FILE_FOLDER_PATH.FilePath("Rebate.txt")
	def __init__(self):
		self.rewardId = int
		self.targetRMB = int
		self.rewardMoney = int
		self.rewardRMB = int
		self.rewardItem = self.GetEvalByString
		
class RichRankReward(TabFile.TabLine):
	'''
	富豪榜奖励配置对象
	'''
	FilePath = DOUBLE_TWELVE_FILE_FOLDER_PATH.FilePath("RichRankReward.txt")
	def __init__(self):
		self.rank = int
		self.rewardMoney = int
		self.rewardRMB = int
		self.rewardItem = self.GetEvalByString
		self.rewardTitleId = int

def LoadRebate():
	global REBATE
	for config in Rebate.ToClassType():
		REBATE[config.rewardId] = config 
		
def LoadRichRankReward():
	global RICH_RANK_REWARD
	for config in RichRankReward.ToClassType():
		RICH_RANK_REWARD[config.rank] = config 

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRebate()
		LoadRichRankReward()
		
		