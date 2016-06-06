#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasFashionShowConfig")
#===============================================================================
# 圣诞时装秀Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Christmas")
	
	ChristmasFashionShow_GoodsConfig_Dict = {}	 #圣诞时装秀商品配置{goodId:cfg,}
	
class ChristmasFashionShowGoods(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ChristmasFashionShowGoods.txt")
	def __init__(self):
		self.goodId = int
		self.item = self.GetEvalByString
		self.needUnbindRMB = int
		self.rebateItem = self.GetEvalByString
		self.limitCnt = int

def LoadChristmasFashionShowGoods():
	global ChristmasFashionShow_GoodsConfig_Dict
	for cfg in ChristmasFashionShowGoods.ToClassType():
		goodId = cfg.goodId
		if goodId in ChristmasFashionShow_GoodsConfig_Dict:
			print "GE_EXC, repeat goodId(%s) in ChristmasFashionShow_GoodsConfig_Dict" % goodId
		ChristmasFashionShow_GoodsConfig_Dict[goodId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadChristmasFashionShowGoods()