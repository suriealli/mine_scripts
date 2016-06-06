#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.MysteryShop.MysteryShopConfig")
#===============================================================================
# 神秘商店配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	MS_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	MS_FILE_FOLDER_PATH.AppendPath("MysteryShop")
	
	#矮人矿洞
	MysterShopMine_Dict = {}
	#神秘商店
	MysterShop_Dict = {}
	
class MineShopConfig(TabFile.TabLine):
	FilePath = MS_FILE_FOLDER_PATH.FilePath("MineShopConfig.txt")
	def __init__(self):
		self.itemCoding = int
		self.needUnbindRMB = int
	
class MysteryShopConfig(TabFile.TabLine):
	FilePath = MS_FILE_FOLDER_PATH.FilePath("MysteryShopConfig.txt")
	def __init__(self):
		self.itemCoding = int
		self.needCoding = int
		self.needItemCnt = int
		self.needLevel = int
		self.needWorldLevel = int
		self.isItem = int
		self.isLimit = int
		self.limitCnt = int
		
def LoadMineShopConfig():
	global MysterShopMine_Dict
	
	for MS in MineShopConfig.ToClassType():
		if MS.itemCoding in MysterShopMine_Dict:
			print "GE_EXC, repeat itemCoding (%s) in MineShopConfig" % MS.itemCoding
			continue
		MysterShopMine_Dict[MS.itemCoding] = MS
	
def LoadMysteryShopConfig():
	global MysterShop_Dict
	
	for MS in MysteryShopConfig.ToClassType():
		if MS.itemCoding in MysterShop_Dict:
			print "GE_EXC, repeat itemCoding (%s) in MysterShop_Dict" % MS.itemCoding
			continue
		MysterShop_Dict[MS.itemCoding] = MS

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadMineShopConfig()
		LoadMysteryShopConfig()
		