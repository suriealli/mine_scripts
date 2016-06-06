#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.SeckillConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

DOUBLE_ELEVEN_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
DOUBLE_ELEVEN_FILE_FOLDER_PATH.AppendPath("DoubleEleven")

if "_HasLoad" not in dir():
	SECKILL_WORLD_LEVEL_TO_WAVE_BASE = {}
	SECKILL_ITEM = {}
	
class SeckillBase(TabFile.TabLine):
	'''
	秒杀汇基础配置
	'''
	FilePath = DOUBLE_ELEVEN_FILE_FOLDER_PATH.FilePath("SeckillBase.txt")
	def __init__(self):
		self.worldLevel = int
		self.wave = int
		self.startDate = self.GetEvalByString
		self.endDate = self.GetEvalByString
		self.itemData = self.GetEvalByString
		
class SeckillItem(TabFile.TabLine):
	'''
	秒杀汇物品配置
	'''
	FilePath = DOUBLE_ELEVEN_FILE_FOLDER_PATH.FilePath("SeckillItem.txt")
	def __init__(self):
		self.itemDataId = int
		self.itemCoding = int
		self.itemCnt = int
		self.isLimitCnt = int
		self.limitCnt = int
		self.isLimitTime = int
		self.limitTime = int
		self.isNeedUnbindRMB_Q = int
		self.currentPrice = int

def LoadSeckillBase():
	global SECKILL_WORLD_LEVEL_TO_WAVE_BASE
	for config in SeckillBase.ToClassType():
		
		if config.worldLevel not in SECKILL_WORLD_LEVEL_TO_WAVE_BASE:
			SECKILL_WORLD_LEVEL_TO_WAVE_BASE.setdefault(config.worldLevel, {})
			
		SECKILL_WORLD_LEVEL_TO_WAVE_BASE[config.worldLevel][config.wave] = config
		
def LoadSeckillItem():
	global SECKILL_ITEM
	for config in SeckillItem.ToClassType():
		SECKILL_ITEM[config.itemDataId] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSeckillBase()
		LoadSeckillItem()
		
		