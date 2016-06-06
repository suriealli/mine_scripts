#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PreciousStore.PreciousStoreConfig")
#===============================================================================
# 珍宝商店配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("PreciousStore")
	
	PreciousStoreConfigDict = {}


class PreciousStoreConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("PreciousStore.txt")
	def __init__(self):
		self.index = int
		self.item = eval
		self.needLevel = int
		self.Limittype	 = int
		self.LimitNum = int
		self.currencyCoding	 = int
		self.currencyCnt = int


def LoadPreciousStoreConfig():
	global PreciousStoreConfigDict
	for config in PreciousStoreConfig.ToClassType():
		if config.index in PreciousStoreConfigDict:
			print "GE_EXC, repeat index(%s) in PreciousStoreConfigDict" % config.index
		PreciousStoreConfigDict[config.index] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPreciousStoreConfig()
