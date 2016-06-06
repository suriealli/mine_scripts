#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemUse.LevelRangeLibao")
#===============================================================================
# 等级区间礼包
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Item.ItemUse import ItemUserClass

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ItemConfig")
	
	LEVELRANGE_LIBAO_DICT = {}	#礼包配置

class LevelRangeLiBao(TabFile.TabLine):
	'''
	全民团购礼包
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("LevelRangeLiBao.txt")
	def __init__(self):
		self.itemId	= int
		self.gold		= int
		self.bindrmb	= int
		self.unbindrmb	= int
		self.items		= self.GetEvalByString
		
		self.levelVal1	= self.GetEvalByString
		self.levelitems1= self.GetEvalByString

		self.levelVal2	= self.GetEvalByString
		self.levelitems2= self.GetEvalByString

		self.levelVal3	= self.GetEvalByString
		self.levelitems3= self.GetEvalByString

		self.levelVal4	= self.GetEvalByString
		self.levelitems4= self.GetEvalByString

		self.levelVal5	= self.GetEvalByString
		self.levelitems5= self.GetEvalByString
		
		self.levelVal6	= self.GetEvalByString
		self.levelitems6= self.GetEvalByString
		
		self.levelVal7	= self.GetEvalByString
		self.levelitems7= self.GetEvalByString
		
		self.levelVal8 = self.GetEvalByString
		self.levelitems8= self.GetEvalByString
		
	def Preprocess(self):
		ItemUserClass.UniverLiBao(self.itemId, self)

def LoadLiBaoConfig():
	for cfg in LevelRangeLiBao.ToClassType():
		LEVELRANGE_LIBAO_DICT[cfg.itemId] = cfg
		cfg.Preprocess()
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLiBaoConfig()
