#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LuckyBag.LuckyBagConfig")
#===============================================================================
# 福袋配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random
from Game.Item.ItemUse import ItemUserClass

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("LuckyBag")
	

	LuckyBag_Config_Dict = {}		#福袋配置字典{coding:config}
	LuckyBag_AwardIndex_Dict = {}		#福袋奖励的配置{index:奖励config}

class LuckyBagConfig(TabFile.TabLine):
	
	FilePath = FILE_FOLDER_PATH.FilePath('LuckBag.txt')
	def __init__(self):
		self.BagCode = int
		self.AwardRate = self.GetEvalByString
		self.Price = int
		self.BeginTime = self.GetDatetimeByString
		self.EndTime = self.GetDatetimeByString
		self.NeedLevel = int
		self.BuyLimitCnt = int

	def PreCoding(self):
		RDM = Random.RandomRate()
		for index, rate in self.AwardRate:
			RDM.AddRandomItem(rate, index)
		self.RandomRate = RDM
		ItemUserClass.LuckyBag(self.BagCode, self)


class LuckyBagRewardConfig(TabFile.TabLine):
	
	FilePath = FILE_FOLDER_PATH.FilePath('LimitChestReward.txt')
	def __init__(self):
		self.Index = int
		self.Type = int
		self.IsRedHand = int
		self.Coding = self.GetIntByString
		self.Cnt = int

def LoadLuckyBagConfig():
	global LuckyBag_Config_Dict
	for config in LuckyBagConfig.ToClassType():
		if config.BagCode in LuckyBag_Config_Dict:
			print "GE_EXC, repeat config.BagCode(%s) in LuckyBag_Config_Dict" % config.BagCode

		config.PreCoding()
		LuckyBag_Config_Dict[config.BagCode] = config
		

def LoadLuckyBagReward():
	global LuckyBag_AwardIndex_Dict
	for config in LuckyBagRewardConfig.ToClassType():
		if config.Index in LuckyBag_AwardIndex_Dict:
			print "GE_EXC, repeat config.Index in LuckyBag_AwardIndex_Dict" % config.Index
		LuckyBag_AwardIndex_Dict[config.Index] = config


if "_HasLoad" not in dir():
	#仅繁体有这些内容 
	if Environment.EnvIsFT() or Environment.IsDevelop:
		if Environment.HasLogic:
			LoadLuckyBagConfig()
			LoadLuckyBagReward()
		
