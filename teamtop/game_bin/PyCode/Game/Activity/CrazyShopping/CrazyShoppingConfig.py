#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CrazyShopping.CrazyShoppingConfig")
#===============================================================================
# 疯狂抢购乐配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("CrazyShopping")
	
	CrazyShoppingConfigDict = {}
	CrazyShoppingDateDict = {}
	
	
class CrazyShoppingConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CrazyShopping.txt")
	def __init__(self):
		self.index = int
		self.month = int
		self.date = int
		self.limit = int
		self.price = int
		self.coding = int


def LoadCrazyShoppingConfig():
	global CrazyShoppingConfigDict
	global CrazyShoppingDateDict
	for config in CrazyShoppingConfig.ToClassType():
		if config.index in CrazyShoppingConfigDict:
			print "GE_EXC,repeat index(%s) in CrazyShoppingConfigDict" % config.index
		if (config.month, config.date) in CrazyShoppingDateDict:
			print "GE_EXC,repeat (month,date)(%s,%s) in CrazyShoppingDateDict" % (config.month, config.date)
		
		CrazyShoppingConfigDict[config.index] = config
		CrazyShoppingDateDict[(config.month, config.date)] = config


if "_HasLoad" not in dir():
	if Environment.EnvIsFT() or Environment.IsDevelop:
		if Environment.HasLogic:
			LoadCrazyShoppingConfig()
