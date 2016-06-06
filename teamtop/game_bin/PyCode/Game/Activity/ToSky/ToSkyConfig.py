#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ToSky.ToSkyConfig")
#===============================================================================
# 冲上云霄配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	TS_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	TS_FILE_FOLDER_PATH.AppendPath("ToSky")
	
	ToSky_Dict = {}
	
	ToSkyRandomIndex = Random.RandomRate()

class ToSkyConfig(TabFile.TabLine):
	FilePath = TS_FILE_FOLDER_PATH.FilePath("ToSkyConfig.txt")
	def __init__(self):
		self.index = int
		self.rate = int
		self.items = eval

def LoadToSkyConfig():
	global ToSky_Dict
	
	for TS in ToSkyConfig.ToClassType():
		if TS.index in ToSky_Dict:
			print "GE_EXC, repeat index(%s) in ToSky_Dict" % TS.index
			continue
		ToSky_Dict[TS.index] = TS
		
		ToSkyRandomIndex.AddRandomItem(TS.rate, TS.index)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadToSkyConfig()
		