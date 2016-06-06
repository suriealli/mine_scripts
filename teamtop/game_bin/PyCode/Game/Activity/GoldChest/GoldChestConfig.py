#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoldChest.GoldChestConfig")
#===============================================================================
# 黄金宝箱配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("GoldChest")
	
	GoldChestConfigDict = {}		#宝箱配置字典
	CntLevelDict = {}				#开启宝箱次数区间的字典{活动id->每个次数区间对应的最大次数}，这里是通过排序来获取次数区间的 
	GoldChestCostDict = {}			#每次开启宝箱扣除的物品数量从这里取 
	ItemConfigDict = {}				#这里的index对应物品的coding和数量 

class GoldChestConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GoldChest.txt")
	def __init__(self):
		self.activeID = int						#活动id
		self.cntlevel = int						#玩家打开宝箱的次数区间
		self.maxcnt = int						#次数区间对应的最大次数<=self.maxcnt
		self.rdmitems = self.GetEvalByString	#随机物品index配置


class GoldChestItemConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GoldChestItemIndex.txt")
	def __init__(self):
		self.Index = int
		self.Item = self.GetEvalByString

class GoldChestCostConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GoldChestCost.txt")
	def __init__(self):
		self.Times = int
		self.Cost = int

def LoadGoldChestConfig():
	'''
	载入黄金宝箱的奖励概率等配置
	'''	
	global GoldChestConfigDict
	for config in GoldChestConfig.ToClassType():
		#这里使用（活动id,次数区间）来作为字典的key,因为不同的活动id对应的开箱物品的情况是不同的
		if (config.activeID, config.cntlevel) in GoldChestConfigDict:
			print "GE_EXC,repeat (config.activeID, config.cntlevel)(%s,%s) in GoldChestConfigDict" % (config.activeID, config.cntlevel)
		GoldChestConfigDict[(config.activeID, config.cntlevel)] = config
	
	#这里获取活动id不同的情况下次数区间的最大次数的列表，通过玩家开启次数在这个列表的排序可以获取玩家的次数区间
	#将玩家当前开启的次数的值插入列表中，与列表中每个区间最大的值放到一起进行排序，则获得排序后该值得索引+1即可获得所处的次数区间
	global CntLevelDict
	for (activeID, _), config in GoldChestConfigDict.iteritems():
		cntlevellist = CntLevelDict.setdefault(activeID, [])
		#列表里的值是不能重复的，而set不能排序，故这里使用列表
		if config.maxcnt in cntlevellist:
			print "GE_EXC,repeat maxcnt(%s) in CntLevelDict, activeID = %s" % (config.maxcnt, activeID)
			continue
		cntlevellist.append(config.maxcnt)

def LoadGoldChestItemConfig():
	'''
	载入黄金宝箱的的物品index，不同的index下的物品coding和数量是允许完全相同的
	'''	
	global ItemConfigDict
	for config in GoldChestItemConfig.ToClassType():
		if config.Index in ItemConfigDict:
			print "GE_EXC, repeat config.Index(%s) in ItemConfigDict in GoldChest" % config.Index
		ItemConfigDict[config.Index ] = config.Item

def LoadGoldChestCostConfig():
	'''
	载入黄金宝箱的开启的次数与对应扣除物品数量的配置
	'''	
	global GoldChestCostDict
	for config in GoldChestCostConfig.ToClassType():
		if config.Times in GoldChestCostDict:
			print "GE_EXC, repeat Times(%s) in GoldChestCostDict" % config.Times
		GoldChestCostDict[config.Times] = config.Cost

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGoldChestConfig()
		LoadGoldChestItemConfig()
		LoadGoldChestCostConfig()
