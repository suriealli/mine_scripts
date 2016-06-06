#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ShenMiBaoXiang.ShenMiBaoXiangConfig")
#===============================================================================
# 神秘宝箱配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ShenMiBaoXiang")
	
	
	SMBX_REWARD_DICT = {}			#配置总表
	SMBX_SUPERITEM_DICT = {}				#极品道具字典
	SMBX_REWARD_RANDOM_DICT_ALL = Random.RandomRate()		#神秘宝箱所有随机字典
	SMBX_MONEY_DICT = {}					#神秘宝箱开启次数对应神石数
	

class ShenMiBaoXiangConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ShenMiBaoXiangConfig.txt")
	def __init__(self):
		self.cnt = int
		self.rmb = int

class ShenMiBaoXiangReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ShenMiBaoXiangReward.txt")
	def __init__(self):
		self.id = int
		self.item = int
		self.num = int
		self.weight = int
		self.superItem = int
		self.cnt = int

def LoadShenMiBaoXiangBase():
	global SMBX_MONEY_DICT
	for cfg in ShenMiBaoXiangConfig.ToClassType():
		if cfg.cnt in SMBX_MONEY_DICT:
			print "GE_EXC, repeat cnt(%s) in LoadShenMiBaoXiangBase" % cfg.cnt
		SMBX_MONEY_DICT[cfg.cnt] = cfg.rmb

def LoadShenMiBaoXiangReward():
	global SMBX_REWARD_RANDOM_DICT_ALL
	global SMBX_SUPERITEM_DICT
	global SMBX_SUPER_DICT
	global SMBX_REWARD_DICT
	for config in ShenMiBaoXiangReward.ToClassType():
		if config.id in SMBX_REWARD_DICT:
			print "GE_EXC, repeat id(%s) in LoadShenMiBaoXiangReward" % config.id
		SMBX_REWARD_RANDOM_DICT_ALL.AddRandomItem(config.weight, config.id)
		if config.superItem:
			SMBX_SUPERITEM_DICT[config.id] = config.cnt
		
		SMBX_REWARD_DICT[config.id] = config



if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadShenMiBaoXiangBase()
		LoadShenMiBaoXiangReward()
