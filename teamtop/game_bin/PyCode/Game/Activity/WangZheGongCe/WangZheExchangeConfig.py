#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheExchangeConfig")
#===============================================================================
# 兑换由我定 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("WangZheGongCe")
	
	#兑换由我定 商品配置
	WZE_GoodsConfig_Dict = {}		#{itemCoding:cfg,}
	
class WangZheExchange(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheExchange.txt")
	def __init__(self):
		self.itemCoding = int
		self.needCoding = int
		self.needItemCnt = int
		self.needLevel = int
		self.isLimit = int
		self.limitCnt = int
	
def LoadWangZheExchangeConfig():
	global WZE_GoodsConfig_Dict
	for cfg in WangZheExchange.ToClassType():
		if cfg.itemCoding in WZE_GoodsConfig_Dict:
			print "GE_EXC, repeat itemCoding (%s) in WZE_GoodsConfig_Dict" % cfg.itemCoding
		WZE_GoodsConfig_Dict[cfg.itemCoding] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadWangZheExchangeConfig()