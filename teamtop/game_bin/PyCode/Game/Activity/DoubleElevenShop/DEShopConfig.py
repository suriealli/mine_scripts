#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleElevenShop.DEShopConfig")
#===============================================================================
# 狂欢兑不停配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	DES_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DES_FILE_FOLDER_PATH.AppendPath("DoubleElevenShop")
	
	DoubleElevenShop_Dict = {}
	
class DoubleElevenShopConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("DoubleElevenShop.txt")
	def __init__(self):
		self.coding = int							#物品coding
		self.needCoding = int						#需要物品coding
		self.needLevel = int						#兑换需要的角色等级
		self.needWorldLevel = int					#兑换需要的世界等级
		self.limitCnt = int							#限购个数(0-不限购)
		self.needItemCnt = int						#兑换需要的物品个数
	
def LoadDoubleElevenShopConfig():
	global DoubleElevenShop_Dict
	
	for DES in DoubleElevenShopConfig.ToClassType():
		if DES.coding in DoubleElevenShop_Dict:
			print "GE_EXC, repeat coding (%s) in DoubleElevenShop_Dict" % DES.coding
			continue
		DoubleElevenShop_Dict[DES.coding] = DES

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadDoubleElevenShopConfig()
	