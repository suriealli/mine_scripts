#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActSuperTurnTableConfig")
#===============================================================================
# 超级转盘配置
#===============================================================================

import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	DES_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DES_FILE_FOLDER_PATH.AppendPath("NewYearDay")
	

	SuperTurnTable_Dict 		= {}								#超级转盘字典{levelRange:{1:普通,2:超级}}

	SuperTurnTableBonus_Dict	= {}								#抽奖福利字典
	BiSuperTurnTableBonus_Dict	= {}
	
#惊喜礼包配置
class SuperTurnTableConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("HappyNewYearSuperTurnTable.txt")
	def __init__(self):
		self.id 				= int 							#物品索引
		self.item				= self.GetEvalByString 			#物品
		self.levelRange			= self.GetEvalByString 			#等级段
		self.rate				= int 							#抽奖概率
		self.isSuperReward		= int 							#超级抽奖
		self.isLocal			= int 							#本服榜广播
		self.isCross			= int 							#全服榜广播

#抽奖福利
class SuperTurnTableBonusConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("HappyNewYearSuperTurnTableBonus.txt")
	def __init__(self):
		self.rewardId			= int 						#
		self.needTimes 			= int 						#抽奖需要次数
		self.itemReward 		= self.GetEvalByString 		#抽奖福利奖励道具
	
def GetSTTBonus(lottery_times):
	'''
	获取福利id
	没有找到返回0
	'''
	global BiSuperTurnTableBonus_Dict

	maxTimes = 0
	for needTimes in BiSuperTurnTableBonus_Dict.keys():
		if lottery_times > needTimes:
			maxTimes = max(maxTimes,needTimes)

	return BiSuperTurnTableBonus_Dict.get(needTimes,0)

def GetRandomObj(level):
	'''
	根据等级获取随机对象
	没有找到返回None
	'''
	global SuperTurnTable_Dict

	levelKey = None
	for (minLevel,maxLevel) in SuperTurnTable_Dict.keys():
		if level >= minLevel and level <= maxLevel:
			levelKey = (minLevel,maxLevel)

	if not levelKey:
		return
	else:
		return SuperTurnTable_Dict[levelKey][1]

def GetLuckyRandomObj(level):
	'''
	根据等级获取超级抽奖随机对象
	没有找到返回None
	'''

	global SuperTurnTable_Dict

	levelKey = None
	for (minLevel,maxLevel) in SuperTurnTable_Dict.keys():
		if level >= minLevel and level <= maxLevel:
			levelKey = (minLevel,maxLevel)

	if not levelKey:
		return
	else:
		return SuperTurnTable_Dict[levelKey][2]


def LoadSuperTurnTableConfig():
	global SuperTurnTable_Dict
	global SuperTurnTable_List
	
	for cfg in SuperTurnTableConfig.ToClassType():
		key = (cfg.levelRange[0],cfg.levelRange[1])

		if key not in SuperTurnTable_Dict:
			SuperTurnTable_Dict[key] = {1:Random.RandomRate(),2:Random.RandomRate()}

		itemid_list = [ temp_cfg.id for _,temp_cfg in SuperTurnTable_Dict[key][1].randomList]
		if cfg.id in itemid_list:
			print "GE_EXC, repeat id (%s) in SuperTurnTable_Dict where levelRange is[%s,%s]"% \
			(cfg.id,cfg.levelRange[0],cfg.levelRange[1])
		#分等级 添加随机对象
		SuperTurnTable_Dict[key][1].AddRandomItem(cfg.rate,cfg)

		#超级抽奖可抽
		if cfg.isSuperReward:
			itemid_list = [ temp_cfg.id for _,temp_cfg in SuperTurnTable_Dict[key][2].randomList]
			if cfg.id in itemid_list:
				print "GE_EXC, repeat id (%s) in SuperTurnTable_Dict LucyLottery where levelRange is[%s,%s]"% \
				(cfg.id,cfg.levelRange[0],cfg.levelRange[1])
			SuperTurnTable_Dict[key][2].AddRandomItem(cfg.rate,cfg)

def LoadSuperTurnTableBonusConfig():
	global SuperTurnTableBonus_Dict
	global BiSuperTurnTableBonus_Dict

	for cfg in SuperTurnTableBonusConfig.ToClassType():

		if cfg.rewardId in SuperTurnTableBonus_Dict:
			print "GE_EXC, repeat rewardId (%s) in SuperTurnTableBonus_Dict" % cfg.rewardId
		if cfg.needTimes in BiSuperTurnTableBonus_Dict:
			print "GE_EXC, repeat needTimes (%s) in SuperTurnTableBonus_List" % cfg.needTimes

		SuperTurnTableBonus_Dict[cfg.rewardId] = cfg
		BiSuperTurnTableBonus_Dict[cfg.needTimes] = cfg.rewardId

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSuperTurnTableConfig()
		LoadSuperTurnTableBonusConfig()
