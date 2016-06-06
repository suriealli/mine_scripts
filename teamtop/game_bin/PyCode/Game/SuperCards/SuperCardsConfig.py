#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.SuperCards.SuperCardsConfig")
#===============================================================================
# 至尊周卡配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	SC_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SC_FILE_FOLDER_PATH.AppendPath("SuperCards")
	
	SuperCardsReward_Dict = {}

class SuperCardsRewardConfig(TabFile.TabLine):
	FilePath = SC_FILE_FOLDER_PATH.FilePath("SuperCardsReward.txt")
	def __init__(self):
		self.days = int								#天数
		self.rewardItems = eval						#奖励物品
	
def LoadSCRConfig():
	global SuperCardsReward_Dict
	
	for SCR in SuperCardsRewardConfig.ToClassType():
		if SCR.days in SuperCardsReward_Dict:
			print "GE_EXC, repeat days (%s) in SuperCardsReward_Dict" % SCR.days
		SuperCardsReward_Dict[SCR.days] = SCR
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSCRConfig()
	
