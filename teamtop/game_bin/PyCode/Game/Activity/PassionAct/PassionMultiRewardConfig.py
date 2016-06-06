#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionMultiRewardConfig")
#===============================================================================
# 激情奖励翻倍config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	#奖励狂翻倍目标任务配置
	PassionMultiReward_TaskConfig_Dict = {}		#{taskIndex:cfg,}
	
class PassionMultiReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionMultiReward.txt")
	def __init__(self):
		self.taskIndex = int
		self.rewardItems = self.GetEvalByString
	
def LoadPassionMultiReward():
	global PassionMultiReward_TaskConfig_Dict
	for cfg in PassionMultiReward.ToClassType():
		taskIndex = cfg.taskIndex
		if taskIndex in PassionMultiReward_TaskConfig_Dict:
			print "GE_EXC, repeat taskIndex (%s) in PassionMultiReward_TaskConfig_Dict" % taskIndex
		PassionMultiReward_TaskConfig_Dict[taskIndex] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionMultiReward()
		if Environment.EnvIsQQ() :
			del PassionMultiReward_TaskConfig_Dict[4]
