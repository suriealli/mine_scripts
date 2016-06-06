#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianRechargeConfig")
#===============================================================================
# 累充送惊喜 Config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("KongJianDecennial")
	
	KJD_LevelRange_Dict = {}				#空间十周年等级段区分{LevelRangeId:LevelRange,}
	KJDRecharge_Unlock_Dict = {}			#空间十周年充值返利 解锁奖励条件{rewardIndex:needRechargeRMB,}
	KJDRecharge_RewardConfig_Dict = {}		#空间十周年充值返利奖励配置 {rewardIndex:{levelRangeId:rewardCfg,},}

class KongJianRechargeUnlock(TabFile.TabLine):
	'''
	解锁奖励条件
	'''
	FilePath = FILE_FLODER_PATH.FilePath("KongJianRechargeUnlock.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needRechargeRMB = int
	
def LoadKongJianRechargeUnlock():
	global KJDRecharge_Unlock_Dict
	for cfg in KongJianRechargeUnlock.ToClassType():
		rewardIndex = cfg.rewardIndex
		needRechargeRMB = cfg.needRechargeRMB
		if rewardIndex in KJDRecharge_Unlock_Dict:
			print "GE_EXC,repeat rewardIndex(%s) in KJDRecharge_Unlock_Dict" % rewardIndex
		KJDRecharge_Unlock_Dict[rewardIndex] = needRechargeRMB

class KongJianDecennialLevelRange(TabFile.TabLine):
	'''
	等级段区分
	'''
	FilePath = FILE_FLODER_PATH.FilePath("KongJianDecennialLevelRange.txt")
	def __init__(self):
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString

def LoadKongJianDecennialLevelRange():
	global KJD_LevelRange_Dict
	for cfg in KongJianDecennialLevelRange.ToClassType():
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		KJD_LevelRange_Dict[levelRangeId] = levelRange

def GetLevelRangeIdByLevel(roleLevel):
	'''
	返回对应等级所在等级区段的ID
	'''
	tmpLevelRangeId = None
	for levelRangeId, levelRange in KJD_LevelRange_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	return tmpLevelRangeId

class KongJianRechargeReward(TabFile.TabLine):
	'''
	奖励配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("KongJianRechargeReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.levelRangeId = int
		self.rewardItems = self.GetEvalByString
		self.rewardBindRMB = int
		self.rewardMoney = int
		self.rewardExchangeCoin = int

def LoadKongJianRechargeReward():
	global KJDRecharge_RewardConfig_Dict
	for cfg in KongJianRechargeReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		levelRangeId = cfg.levelRangeId
		rewardIndexDict = KJDRecharge_RewardConfig_Dict.setdefault(rewardIndex,{})
		if levelRangeId in rewardIndexDict:
			print "GE_EXC,repeat levelRangeId(%s) and rewardIndex(%s) in KJDRecharge_RewardConfig_Dict" % (levelRangeId, rewardIndex)
		rewardIndexDict[levelRangeId] = cfg

def GetCfgByIndexAndLevel(rewardIndex, roleLevel):
	'''
	根据返回对应rewardIndex和roleLevel的奖励配置
	'''
	rewardIndexDict = KJDRecharge_RewardConfig_Dict.get(rewardIndex)
	if not rewardIndexDict:
		return None
	
	levelRangeId = GetLevelRangeIdByLevel(roleLevel)
	if not levelRangeId:
		return None
	
	return rewardIndexDict.get(levelRangeId, None)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadKongJianRechargeUnlock()
		LoadKongJianDecennialLevelRange()
		LoadKongJianRechargeReward()