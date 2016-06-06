#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.ElevenPointExchangeConfig")
#===============================================================================
# 双十一积分兑换配置  @author Gaoshuai 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DoubleEleven")
	
	ElevenPointExchange_Dict = {}
	ElevenPointControl_Dict = {}

class ElevenPointExchangeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ElevenPointExchange.txt")
	def __init__(self):
		self.index = int						#物品索引
		self.minLevel = int						#需要角色最小等级
		self.needPoint = int					#需要积分数
		self.items = self.GetEvalByString		#兑换的物品
		self.special = int						#是否极品道具，进行全服公告并记录
		self.limitCnt = int						#物品限购个数(-1表示不限购)
		
class ElevenPointControlConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ElevenPointControl.txt")
	def __init__(self):
		self.dayIndex = self.GetEvalByString				#物品索引
		self.itemIndex = self.GetEvalByString				#需要角色最小等级
		
		
def LoadElevenPointExchangeConfig():
	global ElevenPointExchange_Dict
	
	for cfg in ElevenPointExchangeConfig.ToClassType():
		if cfg.index in ElevenPointExchange_Dict:
			print "GE_EXC, repeat index(%s) in ElevenPointExchange_Dict" % cfg.index
		ElevenPointExchange_Dict[cfg.index] = cfg
		
def LoadElevenPointControlConfig():
	global ElevenPointControl_Dict
	
	for cfg in ElevenPointControlConfig.ToClassType():
		if cfg.dayIndex in ElevenPointControl_Dict:
			print "GE_EXC, repeat dayIndex(%s) in ElevenPointControl_Dict" % cfg.dayIndex
		ElevenPointControl_Dict[cfg.dayIndex] = cfg.itemIndex
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadElevenPointExchangeConfig()
		LoadElevenPointControlConfig()
