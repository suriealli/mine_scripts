#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.LoveTogetherConfig")
#===============================================================================
# 爱在一起配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DoubleTwelve")
	
	LoveTogether_OnlineReward_Dict = {}		#爱在一起在线奖励配置{rewardIndex:cfg,}

class LTOnlineReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LTOnlineReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needOnlineMins = int
		self.rewardLotteryTimes = int
		self.rewardItems = self.GetEvalByString
		self.rewardMoney = int
		self.rewardBindRMB = int

def LoadLTOnlineReward():
	global LoveTogether_OnlineReward_Dict
	for cfg in LTOnlineReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in LoveTogether_OnlineReward_Dict:
			print "GE_EXC,repeat rewardIndex(%s) in LTOnlineReward" % rewardIndex
		if rewardIndex > 1 and rewardIndex % 2 != 0:
			print "GE_EXC,error rewardIndex(%s) impossible mod 2 != 0" % rewardIndex
		LoveTogether_OnlineReward_Dict[rewardIndex] = cfg 

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadLTOnlineReward()