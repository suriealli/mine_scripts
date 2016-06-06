#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.YeYouJieKuangHuan.YeYouJieRechargeConfig")
#===============================================================================
# 页游节充值返利 config
#===============================================================================
from Util.File import TabFile
import DynamicPath
import Environment


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("YeYouJieRecharge")
	
	YYJRecharge_Unlock_Dict = {}			#页游节充值返利 解锁奖励条件{rewardIndex:needRechargeRMB,}
	YYJRecharge_LevelRange_Dict = {}		#页游节充值返利等级段区分{LevelRangeId:LevelRange,}
	YYJRecharge_RewardConfig_Dict = {}		#页游节充值返利奖励配置 {dayIndex:{rewardIndex:{levelRangeId:rewardCfg,},},}

class YeYouJieRechargeUnlock(TabFile.TabLine):
	'''
	解锁奖励条件
	'''
	FilePath = FILE_FLODER_PATH.FilePath("YeYouJieRechargeUnlock.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needRechargeRMB = int

def LoadYeYouJieRechargeUnlock():
	global YYJRecharge_Unlock_Dict
	for cfg in YeYouJieRechargeUnlock.ToClassType():
		rewardIndex = cfg.rewardIndex
		needRechargeRMB = cfg.needRechargeRMB
		if rewardIndex in YYJRecharge_Unlock_Dict:
			print "GE_EXC,repeat rewardIndex(%s) in YYJRecharge_Unlock_Dict" % rewardIndex
		YYJRecharge_Unlock_Dict[rewardIndex] = needRechargeRMB

def GetRewardIndexByRechargeRMB(rechargeRMB):
	'''
	返回充值神石 解锁最高奖励index
	'''
	tmpRewardIndex = None
	tmpRechargeRMB = 0
	for rewardIndex, needRechargeRMB in YYJRecharge_Unlock_Dict.iteritems():
		if rechargeRMB >= needRechargeRMB and needRechargeRMB > tmpRechargeRMB:
			tmpRewardIndex = rewardIndex
			tmpRechargeRMB = needRechargeRMB
	
	return tmpRewardIndex

class YeYouJieRechargeLevelRange(TabFile.TabLine):
	'''
	等级段区分
	'''
	FilePath = FILE_FLODER_PATH.FilePath("YeYouJieRechargeLevelRange.txt")
	def __init__(self):
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString

def LoadYeYouJieRechargeLevelRange():
	global YYJRecharge_LevelRange_Dict
	for cfg in YeYouJieRechargeLevelRange.ToClassType():
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		YYJRecharge_LevelRange_Dict[levelRangeId] = levelRange

def GetLevelRangeIdByLevel(roleLevel):
	'''
	返回对应等级所在等级区段的ID
	'''
	tmpLevelRangeId = None
	for levelRangeId, levelRange in YYJRecharge_LevelRange_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	return tmpLevelRangeId
	

class YeYouJieRechargeReward(TabFile.TabLine):
	'''
	奖励配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("YeYouJieRechargeReward.txt")
	def __init__(self):
		self.dayIndex = int
		self.rewardIndex = int
		self.levelRangeId = int
		self.rewardItems = self.GetEvalByString
		self.rewardBindRMB = int
		self.rewardMoney = int

def LoadYeYouJieRechargeReward():
	global YYJRecharge_RewardConfig_Dict
	for cfg in YeYouJieRechargeReward.ToClassType():
		dayIndex = cfg.dayIndex
		rewardIndex = cfg.rewardIndex
		levelRangeId = cfg.levelRangeId
		dayIndexDictDict = YYJRecharge_RewardConfig_Dict.setdefault(dayIndex, {})
		rewardIndexDict = dayIndexDictDict.setdefault(rewardIndex,{})
		if levelRangeId in rewardIndexDict:
			print "GE_EXC,repeat levelRangeId(%s) with dayInde(%s) and rewardIndex(%s) in YYJRecharge_RewardConfig_Dict" % (levelRangeId, dayIndex, rewardIndex)
		rewardIndexDict[levelRangeId] = cfg

def GetCfgByDayAndRMBAndLevel(dayIndex, rechargeRMB, roleLevel):
	'''
	根据天数 和 充值神石 返回最高解锁奖励配置
	'''
	dayIndexDictDict = YYJRecharge_RewardConfig_Dict.get(dayIndex)
	if not dayIndexDictDict:
		return None

	rewardIndex = GetRewardIndexByRechargeRMB(rechargeRMB)
	if not rewardIndex:
		return None
	
	rewardIndexDict = dayIndexDictDict.get(rewardIndex)
	if not rewardIndexDict:
		return None
	
	levelRangeId = GetLevelRangeIdByLevel(roleLevel)
	if not levelRangeId:
		return None
	
	return rewardIndexDict.get(levelRangeId, None)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadYeYouJieRechargeUnlock()
		LoadYeYouJieRechargeLevelRange()
		LoadYeYouJieRechargeReward()