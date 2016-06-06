#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonKnightChallenge.DragonKnightChallengeConfig")
#===============================================================================
# 龙骑试炼Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DragonKnightChallenge")
	
	DKC_BASECONFIG_DICT = {}	#龙骑试炼基本配置{DKCLevel:cfg,}
	
class DragonKnightChallengeBase(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DragonKnightChallengeBase.txt")
	def __init__(self):
		self.DKCLevel = int 
		self.levelName = str
		self.needZDL = self.GetIntByString
		self.rewardItem = self.GetEvalByString
		self.rewardTitle = self.GetIntByString
		self.titleName = str
		self.campId = int
		self.fightType = int

def LoadDragonKnightChallengeBase():
	global DKC_BASECONFIG_DICT
	for cfg in DragonKnightChallengeBase.ToClassType():
		DKCLevel = cfg.DKCLevel
		if DKCLevel in DKC_BASECONFIG_DICT:
			print "GE_EXC,repeat DKCLevel(%s) in DKC_BASECONFIG_DICT" % DKCLevel
		DKC_BASECONFIG_DICT[DKCLevel] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDragonKnightChallengeBase()
