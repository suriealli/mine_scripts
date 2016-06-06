#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionGiftConfig")
#===============================================================================
# 激情有礼 config
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("PassionAct")
	
	#激情有礼任务达成累计奖励配置
	PassionGift_Reward_Dict = {}		#{rewardIndex:rewardItem,}


class PassionGiftReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("PassionGiftReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.rewardItem = self.GetEvalByString
	

def LoadPassionGiftReward():
	global PassionGift_Reward_Dict
	for cfg in PassionGiftReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		rewardItem = cfg.rewardItem
		if rewardIndex in PassionGift_Reward_Dict:
			print "GE_EXC,repeat rewardIndex(%s) in PassionGift_Reward_Dict" % rewardIndex
		PassionGift_Reward_Dict[rewardIndex] = rewardItem
		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionGiftReward()