#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.CouplesFashionShopConfig")
#===============================================================================
# 情侣炫酷时装 config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ValentineDay")
	
	CouplesFashionShop_GoodsConfig_Dict = {}	 #情侣炫酷时装商品配置{goodId:cfg,}
	
class CouplesFashionShop(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CouplesFashionShop.txt")
	def __init__(self):
		self.goodId = int
		self.item = self.GetEvalByString
		self.needUnbindRMB = int
		self.rebateItem = self.GetEvalByString
		self.limitCnt = int

def LoadCouplesFashionShop():
	global CouplesFashionShop_GoodsConfig_Dict
	for cfg in CouplesFashionShop.ToClassType():
		goodId = cfg.goodId
		if goodId in CouplesFashionShop_GoodsConfig_Dict:
			print "GE_EXC, repeat goodId(%s) in CouplesFashionShop_GoodsConfig_Dict" % goodId
		CouplesFashionShop_GoodsConfig_Dict[goodId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadCouplesFashionShop()