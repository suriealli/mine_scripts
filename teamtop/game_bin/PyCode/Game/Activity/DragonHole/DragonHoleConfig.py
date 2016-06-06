#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DragonHole.DragonHoleConfig")
#===============================================================================
# 勇闯龙窟配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DragonHole")
	DragonHoleConfigDict = {}	#勇闯龙窟击杀怪物奖励配置
	
class DragonHoleConfig(TabFile.TabLine):
	#副本杀怪奖励配置
	FilePath = FILE_FOLDER_PATH.FilePath("DragonHoleConfig.txt")
	def __init__(self):
		self.roleLevel	 = int
		self.maxExp		 = int
		self.addExp		 = int
		self.campId		 = int
		self.fightType	 = int

def LoadDragonHoleConfig():
	global DragonHoleConfigDict
	for cfg in DragonHoleConfig.ToClassType():
		if cfg.roleLevel in DragonHoleConfigDict:
			print "GE_EXC, repeat roleLevel(%s) in DragonHoleConfigDict" % cfg.roleLevel
		DragonHoleConfigDict[cfg.roleLevel] = cfg

#if "_HasLoad" not in dir():
#	if Environment.HasLogic:
#		LoadDragonHoleConfig()
