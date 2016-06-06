#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZhongQiu.HuoYueDaLiConifg")
#===============================================================================
# 活跃大礼 Config
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ZhongQiu")
	
	#活跃大礼奖励配置{rewardIndex:cfg,}
	HuoYueDaLi_RewardConfig_Dict = {}

class HuoYueDaLiReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("HuoYueDaLiReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.rewardItem = self.GetEvalByString


def GetRewardByIndexInteval(lowIndex, highIndex):
	'''
	返回 奖励索引区间[lowIndex, highIndex]中所有奖励
	'''
	if lowIndex > highIndex:
		print "GE_EXC, HuoYueDaLiConifg::GetRewardByIndexInteval::lowIndex(%s) > highIndex(%s)" % (lowIndex, highIndex)
		return {}
	
	tRewardDict = {}	
	for tIndex in xrange(lowIndex, highIndex + 1):
		if tIndex in HuoYueDaLi_RewardConfig_Dict:
			rewardCfg = HuoYueDaLi_RewardConfig_Dict[tIndex]
			coding, cnt = rewardCfg.rewardItem 
			if coding not in tRewardDict:
				tRewardDict[coding] = cnt
			else:
				tRewardDict[coding] += cnt
	
	return tRewardDict
			

def LoadHuoYueDaLiReward():
	global HuoYueDaLi_RewardConfig_Dict
	for cfg in HuoYueDaLiReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in HuoYueDaLi_RewardConfig_Dict:
			print "GE_EXC, repeat rewardIndex(%s) in HuoYueDaLi_RewardConfig_Dict" % rewardIndex
		HuoYueDaLi_RewardConfig_Dict[rewardIndex] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadHuoYueDaLiReward()