#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianLoginRewardConfig")
#===============================================================================
# 天天领好礼 Config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Common.Other import EnumGameConfig

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("KongJianDecennial")
	
	KongJianFirstRecharge_RewardsConfig_Dict = {}		#首冲拿大礼奖励字典{rewardIndex:cfg,}

class KongJianLoginRewards(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("KongJianLoginReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.rewardItems = self.GetEvalByString
		self.rewardMoney = int
		self.rewardBindRMB = int

def GetRewardCfg():
	'''
	返回首冲拿大礼奖励配置
	'''
	return KongJianFirstRecharge_RewardsConfig_Dict.get( EnumGameConfig.KJD_LoginReward_DefaultKey)
	
def LoadKongJianLoginRewards():
	global KongJianFirstRecharge_RewardsConfig_Dict
	for cfg in KongJianLoginRewards.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in KongJianFirstRecharge_RewardsConfig_Dict:
			print "GE_EXC,repeat rewardIndex(%s) in KongJianFirstRecharge_RewardsConfig_Dict" % rewardIndex
		KongJianFirstRecharge_RewardsConfig_Dict[rewardIndex] = cfg
	
	if EnumGameConfig.KJD_LoginReward_DefaultKey not in KongJianFirstRecharge_RewardsConfig_Dict:
		print "GE_EXC, default key(%s) not in KongJianFirstRecharge_RewardsConfig_Dict" % EnumGameConfig.KJD_LoginReward_DefaultKey
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadKongJianLoginRewards()