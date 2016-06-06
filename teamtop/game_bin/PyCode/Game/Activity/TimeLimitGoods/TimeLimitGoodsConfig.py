#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TimeLimitGoods.TimeLimitGoodsConfig")
#===============================================================================
# 限时商城配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	TIMELIMIT_GOODS_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	TIMELIMIT_GOODS_FOLDER_PATH.AppendPath("TimeLimitGoods")
	
	TIME_LIMIT_GOODS_DICT = {}
	
class TimeLimitGoods(TabFile.TabLine):
	'''
	限时商城配置
	'''
	FilePath = TIMELIMIT_GOODS_FOLDER_PATH.FilePath("TimeLimitGoods.txt")
	def __init__(self):
		self.goodsId	= int
		self.startTime	= self.GetDatetimeByString
		self.endTime	= self.GetDatetimeByString
		self.needQ		= int
		self.needUnbindRMB = int
		self.needLevel	= int
		self.coding		= int
		self.goodsType	= int
		self.buyLimit	= self.GetEvalByString
		
def LoadTimeLimitGoods():
	global TIME_LIMIT_GOODS_DICT
	
	for cfg in TimeLimitGoods.ToClassType():
		if cfg.goodsId in TIME_LIMIT_GOODS_DICT:
			print "GE_EXC, repeat goodsId(%s) in LoadTimeLimitGoods" % cfg.goodsId
		TIME_LIMIT_GOODS_DICT[cfg.goodsId] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTimeLimitGoods()
	