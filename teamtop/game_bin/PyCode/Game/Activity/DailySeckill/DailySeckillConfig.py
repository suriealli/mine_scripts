#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DailySeckill.DailySeckillConfig")
#===============================================================================
# 天天秒杀配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DailySeckill")
	
	DailySeckillConfig_Dict = {}					#配置表统统都载到这个字典里来
	DailySeckillRDM = Random.RandomRate()			#RDM就是random的缩写
	DailySeckillWLS_List = []						#WLS就是WorldLevelSection世界等级区间的缩写
	DailySeckillWLSConfig_Dict = {}

class DailySeckillConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("dailyseckill.txt")
	def __init__(self):
		self.Index = int
		self.ItemCode = self.GetEvalByString
		self.Type = int
		self.Cnt = int		#每次刷新后，限制的数量
		self.Price = int
		self.IsBroadcast = int
		self.CanSysRMB = int

class DailySeckillWorldLevelConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("worldlevelsection.txt")
	def __init__(self):
		self.Section = int
		self.MaxWorldLevel = int
		self.RandomList = self.GetEvalByString

	def PreCoding(self):
		randomrate = Random.RandomRate()
		for index, rate in self.RandomList:
			randomrate.AddRandomItem(rate, index)
		self.Randomrate = randomrate

	def GetRandom(self, cnt):
		return self.Randomrate.RandomMany(cnt)
			

def LoadDailySeckillConfig():
	global DailySeckillConfig_Dict
	for config in DailySeckillConfig.ToClassType():
		#种类必须是1：道具，2：命魂 ，3：天赋卡中的一个
		if config.Type < 1 or config.Type > 3:
			print "GE_EXC,error type(%s) on LoadDailySeckillConfig" % config.Type
			continue
		if config.Index in DailySeckillConfig_Dict:
			print "GE_EXC, repeat Index(%s) in DailySeckillConfig" % config.Index
		DailySeckillConfig_Dict[config.Index] = config

def LoadWorldLevelConfig():
	global DailySeckillWLSConfig_Dict
	global DailySeckillWLS_List
	for config in DailySeckillWorldLevelConfig.ToClassType():
		if config.Section in DailySeckillWLSConfig_Dict:
			print "GE_EXC,repeat config.Section(%s) in DailySeckillWorldLevelConfig" % config.Section
		config.PreCoding()
		DailySeckillWLSConfig_Dict[config.Section] = config
		#这里把每个世界等级区间的最大世界等级取出来放到列表里,则将世界等级插入到这个列表后排序，世界等级的下标+1即是世界等级区间
		if config.MaxWorldLevel in DailySeckillWLS_List:
			print "GE_EXC,repeat config.MaxWorldLevel(%s) in DailySeckillWLS_List" % config.MaxWorldLevel
			continue
		DailySeckillWLS_List.append(config.MaxWorldLevel)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadDailySeckillConfig()
		LoadWorldLevelConfig()
