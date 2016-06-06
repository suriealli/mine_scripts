#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationDay.StrikeBossConfig")
#===============================================================================
# 击杀国庆boss配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("NationDay")
	
	StrikeBossConfigDict = {}			#奖励的索引，根据索引来获取奖励
	StrikeBossRateDict = {}				#存储奖励配置key是（等级区间，bossType）
	StrikeBossSetionDict = {}			#{玩家等级->对应等级区间}


class StrikeBossIndexConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("StrikeBossIndex.txt")
	def __init__(self):
		self.Index = int							#索引
		self.Item = self.GetEvalByString			#物品coding,cnt
		self.Type = int								#物品类型
		self.IsBroadcast = int						#获取的时候是否需要全服公告

class StrikeBossRateConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("StrikeBossRate.txt")
	def __init__(self):
		self.Section = int							#等级区间
		self.Type = int								#boss类型
		self.RateList = self.GetEvalByString		#奖励索引概率表
		self.CostCoding = int						#需要消耗的物品coding
		self.CostCnt = int							#需要消耗的物品数量
		
	def PreCoding(self):
		RDM = Random.RandomRate()
		for index , rate in self.RateList:
			RDM.AddRandomItem(rate, index)
		self.RandomRate = RDM

class StrikeBossSectionConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("StrikeBossSection.txt")
	def __init__(self):
		self.Level = int							#等级
		self.Section = int							#等级区间

def LoadStrikeBossIndexConfig():
	global StrikeBossConfigDict
	for config in StrikeBossIndexConfig.ToClassType():
		if config.Index in StrikeBossConfigDict:
			print "GE_EXC, repeat config.Index(%s) in StrikeBossConfigDict in NationDay" % config.Index
		StrikeBossConfigDict[config.Index] = config

def LoadStrikeBossRateConfig():
	global StrikeBossRateDict
	for config in StrikeBossRateConfig.ToClassType():
		if (config.Section, config.Type) in StrikeBossRateDict:
			print "GE_EXC, repeat (config.Section, config.Type)(%s,%s) in StrikeBossRateDict in NationDay" % (config.Section, config.Type)
		config.PreCoding()
		StrikeBossRateDict[(config.Section, config.Type)] = config

def LoadStrikeBossSectionConfig():
	global StrikeBossSetionDict
	for config in StrikeBossSectionConfig.ToClassType():
		if config.Level in StrikeBossSetionDict:
			print "GE_EXC, repeat config.Level(%s) in StrikeBossSetionDict in NationDay" % config.Level
		StrikeBossSetionDict[config.Level] = config.Section
			
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadStrikeBossIndexConfig()
		LoadStrikeBossRateConfig()
		LoadStrikeBossSectionConfig()
		
