#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionDiscountConfig")
#===============================================================================
# 特惠商品 config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	PassionDiscount_GoodsConfig_Dict = {}	 #最炫时装秀商品配置{goodId:cfg,}
	
class PassionDiscount(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionDiscount.txt")
	def __init__(self):
		self.goodId = int
		self.item = self.GetEvalByString
		self.needLevel = int
		self.needUnbindRMB = int
		self.limitCnt = int

def LoadPassionDiscount():
	global PassionDiscount_GoodsConfig_Dict
	for cfg in PassionDiscount.ToClassType():
		goodId = cfg.goodId
		if goodId in PassionDiscount_GoodsConfig_Dict:
			print "GE_EXC, repeat goodId(%s) in PassionDiscount_GoodsConfig_Dict" % goodId
		PassionDiscount_GoodsConfig_Dict[goodId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionDiscount()