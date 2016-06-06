#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheCrazyRewardConfig")
#===============================================================================
# 奖励狂翻倍 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("WangZheGongCe")
	
	#奖励狂翻倍目标任务配置
	WZCR_TaskConfig_Dict = {}		#{taskIndex:cfg,}
	
class WangZheCrazyRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheCrazyReward.txt")
	def __init__(self):
		self.taskIndex = int
		self.rewardItems = self.GetEvalByString
	
def LoadWangZheCrazyRewardConfig():
	global WZCR_TaskConfig_Dict
	for cfg in WangZheCrazyRewardConfig.ToClassType():
		taskIndex = cfg.taskIndex
		if taskIndex in WZCR_TaskConfig_Dict:
			print "GE_EXC, repeat taskIndex (%s) in WZCR_TaskConfig_Dict" % taskIndex
		WZCR_TaskConfig_Dict[taskIndex] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadWangZheCrazyRewardConfig()
