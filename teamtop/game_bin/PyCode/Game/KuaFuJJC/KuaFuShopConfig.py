#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.KuaFuJJC.KuaFuShopConfig")
#===============================================================================
# 跨服商店Config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("KuaFuJJC")
	
	KuaFuShop_GoodsConfig_Dict = {}		#{goodId:cfg,}

class KuaFuShopConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("KuaFuShop.txt")
	def __init__(self):
		self.goodId = int
		self.exchangeType = int
		self.item = self.GetEvalByString
		self.needCoding = int
		self.needCnt = int
		self.needRoleLevel = int
		self.needWorldLevel = int
		self.isLimit = int
		self.limitCnt = self.GetIntByString
		self.isDayClear = int

def LoadKuaFuShopConfig():
	global KuaFuShop_GoodsConfig_Dict
	for cfg in KuaFuShopConfig.ToClassType():
		goodId = cfg.goodId
		isLimit = cfg.isLimit
		limitCnt = cfg.limitCnt
		if goodId in KuaFuShop_GoodsConfig_Dict:
			print "GE_EXC,repeat goodId(%s) in KuaFuShop_GoodsConfig_Dict" % goodId
		if isLimit and not limitCnt:
			print "GE_EXC, KuaFuShopConfig is Limite without limitCnt!"
		KuaFuShop_GoodsConfig_Dict[goodId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadKuaFuShopConfig()