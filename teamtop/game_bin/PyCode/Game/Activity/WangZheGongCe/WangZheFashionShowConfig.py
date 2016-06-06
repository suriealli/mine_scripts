#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheFashionShowConfig")
#===============================================================================
# 最炫时装秀 Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("WangZheGongCe")
	
	WangZheFashionShow_GoodsConfig_Dict = {}	 #最炫时装秀商品配置{goodId:cfg,}
	
class WangZheFashionShowGoods(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheFashionShow.txt")
	def __init__(self):
		self.goodId = int
		self.item = self.GetEvalByString
		self.needUnbindRMB = int
		self.rebateItem = self.GetEvalByString
		self.limitCnt = int

def LoadWangZheFashionShowGoods():
	global WangZheFashionShow_GoodsConfig_Dict
	for cfg in WangZheFashionShowGoods.ToClassType():
		goodId = cfg.goodId
		if goodId in WangZheFashionShow_GoodsConfig_Dict:
			print "GE_EXC, repeat goodId(%s) in WangZheFashionShow_GoodsConfig_Dict" % goodId
		WangZheFashionShow_GoodsConfig_Dict[goodId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadWangZheFashionShowGoods()