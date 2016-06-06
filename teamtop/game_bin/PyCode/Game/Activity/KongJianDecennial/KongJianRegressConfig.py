#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianRegressConfig")
#===============================================================================
# 空间回归Config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Common.Other import EnumGameConfig

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("KongJianDecennial")
	
	KongJianRegress_RewardsConfig_Dict = {}		#空间回归奖励字典{rewardIndex:cfg,}

class KongJianRegressRewards(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("RegressRewards.txt")
	def __init__(self):
		self.rewardIndex = int
		self.rewardItems = self.GetEvalByString
		self.rewardMoney = int
		self.rewardBindRMB = int

def GetRewardCfg():
	'''
	返回回归奖励配置
	'''
	return KongJianRegress_RewardsConfig_Dict.get( EnumGameConfig.KJD_RegressReward_DefaultKey)
	
def LoadKongJianRegressRewards():
	global KongJianRegress_RewardsConfig_Dict
	for cfg in KongJianRegressRewards.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in KongJianRegress_RewardsConfig_Dict:
			print "GE_EXC,repeat rewardIndex(%s) in KongJianRegress_RewardsConfig_Dict" % rewardIndex
		KongJianRegress_RewardsConfig_Dict[rewardIndex] = cfg
	
	if EnumGameConfig.KJD_RegressReward_DefaultKey not in KongJianRegress_RewardsConfig_Dict:
		print "GE_EXC, default key(%s) not in KongJianRegress_RewardsConfig_Dict" % EnumGameConfig.KJD_RegressReward_DefaultKey
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadKongJianRegressRewards()