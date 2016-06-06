#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TouchGoldReward.TouchGoldRewardConfig")
#===============================================================================
# 注释
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment
if "_HasLoad" not in dir():
	T_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	T_FILE_FOLDER_PATH.AppendPath("TouchGoldReward")
	
	TouchGoldReward_Dict = {}
	TouchGoldRewardStone_Dict = {}
	
class TouchGoldReward(TabFile.TabLine):
	FilePath = T_FILE_FOLDER_PATH.FilePath("TouchGoldReward.txt")
	def __init__(self):
		self.index = int
		self.needCnt = int
		self.rewardItems = eval
		self.rewardBuffIndex = int
		self.rewardStone = eval
		
def LoadTouchGoldReward():
	global TouchGoldReward_Dict, TouchGoldRewardStone_Dict
	
	for cfg in TouchGoldReward.ToClassType():
		if cfg.index in TouchGoldReward_Dict:
			print "GE_EXC, repeat index(%s) in TouchGoldReward_Dict" % cfg.index
		TouchGoldReward_Dict[cfg.index] = cfg
		
		if cfg.rewardBuffIndex:
			TouchGoldRewardStone_Dict[cfg.index] = cfg.needCnt
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTouchGoldReward()
	
	
