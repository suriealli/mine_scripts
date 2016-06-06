#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.MoLingDraw.MoLingLuckyDrawConfig")
#===============================================================================
# 魔灵大转盘配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile



if "_HasLoad" not in dir():
	MOLING_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	MOLING_FILE_FOLDER_PATH.AppendPath("MoLing")
	
	MOLING_LUCKY_DRAW = {}			#魔灵大转盘配置
	MOLING_LUCKY_DRAW_VIP_CONFIG = {}	#魔灵大转盘VIP次数配置
	LUCKY_DRAW_RANDOM = Random.RandomRate()	#魔灵大转盘随机对象
	
class MoLingLuckyDraw(TabFile.TabLine):
	'''
	魔灵大转盘配置
	'''
	FilePath = MOLING_FILE_FOLDER_PATH.FilePath("MoLingLuckyDraw.txt")
	def __init__(self):
		self.rewardId = int
		self.rate = int
		self.itemCoding = int
		self.cnt = int
		
class MoLingLuckyDrawVIPConfig(TabFile.TabLine):
	'''
	魔灵大转盘配置
	'''
	FilePath = MOLING_FILE_FOLDER_PATH.FilePath("MoLingVIPConfig.txt")
	def __init__(self):
		self.level = int					#vip等级
		self.MoLingDrawCnt = int			#魔灵大转盘次数
		
def LoadMoLingLuckyDrawVIPConfig():
	global MOLING_LUCKY_DRAW_VIP_CONFIG
	
	for config in MoLingLuckyDrawVIPConfig.ToClassType():
		if config.level in MOLING_LUCKY_DRAW_VIP_CONFIG:
			print "GE_EXC repeat key(%s) in _VIP_BASE in LoadVIPBaseConfig" % config.level
		MOLING_LUCKY_DRAW_VIP_CONFIG[config.level] = config.MoLingDrawCnt
		
def LoadMoLingLuckyDraw():
	global MOLING_LUCKY_DRAW
	global LUCKY_DRAW_RANDOM
	for config in MoLingLuckyDraw.ToClassType():
		MOLING_LUCKY_DRAW[config.rewardId] = config
		LUCKY_DRAW_RANDOM.AddRandomItem(config.rate, config.rewardId)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadMoLingLuckyDraw()
		LoadMoLingLuckyDrawVIPConfig()