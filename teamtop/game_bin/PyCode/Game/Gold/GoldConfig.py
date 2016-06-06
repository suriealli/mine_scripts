#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Gold.GoldConfig")
#===============================================================================
# 炼金配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	GOLD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	GOLD_FILE_FOLDER_PATH.AppendPath("Gold")

	GOLD_BASE_DICT = {}
	GOLD_TIMES_DCIT = {}
	GOLD_TIMES_VIP_DICT = {}
	
class GoldConfig(TabFile.TabLine):
	'''
	炼金配置表
	'''
	FilePath = GOLD_FILE_FOLDER_PATH.FilePath("GoldConfig.txt")
	def __init__(self):
		self.level        = int
		self.perfectMoney = int
		self.advanceMoney = int
		self.assistMoney  = int
		self.perfectMoney_fcm = int                   #完美炼金奖励
		self.advanceMoney_fcm = int                   #提前收获炼金奖励
		self.assistMoney_fcm = int                    #协助奖励

class GoldTimes(TabFile.TabLine):
	'''
	炼金次数对应消耗表
	'''
	FilePath = GOLD_FILE_FOLDER_PATH.FilePath("GoldTimes.txt")
	def __init__(self):
		self.times = int
		self.cost  = int 
		
def LoadGoldConfig():
	global GOLD_BASE_DICT
	for CFG in GoldConfig.ToClassType():
		if CFG.level in GOLD_BASE_DICT:
			print "GE_EXC,repeate level in GoldConfig,(%s)", CFG.level
		GOLD_BASE_DICT[CFG.level] = CFG

def LoadGoldTimes():
	global GOLD_TIMES_DCIT
	for CFG in GoldTimes.ToClassType():
		if CFG.times in GOLD_TIMES_DCIT:
			print "GE_EXC,repeate times in GoldTimes,(%S)", CFG.times
		GOLD_TIMES_DCIT[CFG.times] = CFG 
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		LoadGoldConfig()
		LoadGoldTimes()
	
