#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Holiday.HolidayOnlineRewardConfig")
#===============================================================================
# 元旦在线奖励Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Holiday")
	
	Holiday_OnlineReward_Config_Dict = {}	#元旦在线奖励配置{rewardIndex:cfg,}

class HolidayOnlineReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HolidayOnlineReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.VIPLevel = int
		self.needOnlineMin = int
		self.nomalReward = self.GetEvalByString
		self.VIPReward = self.GetEvalByString
		self.prayTime = int
		self.rewardMoney = int

def LoadHolidayOnlineReward():
	global Holiday_OnlineReward_Config_Dict
	for cfg in HolidayOnlineReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in Holiday_OnlineReward_Config_Dict:
			print "GE_EXC, repeat rewardIndex(%s) in Holiday_OnlineReward_Config_Dict" % rewardIndex
		Holiday_OnlineReward_Config_Dict[rewardIndex] = cfg		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadHolidayOnlineReward()