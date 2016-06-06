#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OnLineReward.OnLineRewardConfig")
#===============================================================================
# 在线奖励配置信息
#===============================================================================

import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	OLR_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	OLR_FILE_FOLDER_PATH.AppendPath("OnLineReward")
	#在线奖励配置字典
	OLRConfig_Dict = {}


class OLRConfig(TabFile.TabLine):
	FilePath = OLR_FILE_FOLDER_PATH.FilePath("OnLineReward.txt")
	def __init__(self):
		self.onlineRewardtype = int									#累计类型
		self.sec = int												#时长
		self.serverItem = self.GetEvalByString						#奖励物品类型
		self.rewardmoney = int										#奖励金币
		self.rewardrmb = int										#奖励魔晶
		self.nextRewardtype = int									#继续类型
		
def LoadOLRConfig():
	#读取配置
	global OLRConfig_Dict
	for olr in OLRConfig.ToClassType():
		if olr.onlineRewardtype in OLRConfig_Dict:
			print "GE_EXC, repeat onlineRewardtype in LoadOLRConfig  (%s)" % olr.onlineRewardtype
		OLRConfig_Dict[olr.onlineRewardtype] = olr
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadOLRConfig()
