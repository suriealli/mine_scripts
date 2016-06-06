#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheRechargeRebateConfig")
#===============================================================================
# 王者公测充值返利 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("WangZheGongCe")
	
	#王者公测充值返利返利配置 {rewardIndex:cfg,}
	WZRR_RebateConfig_Dict = {}
	#王者公测充值返利抽奖等级段配置 {levelRangeId:LevelRange,}
	WZRR_LevelRange2ID_Dict = {}
	#王者公测充值返利奖励池配置{waveIndex:{levelRangeId:{itemIndex:cfg,},},}
	WZRR_LotteryConfig_Dict = {}
	
	
class WangZheRechargeRebateConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheRechargeRebate.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needRechargeRMB = int
		self.rewardItems = self.GetEvalByString
	
def LoadWangZheRechargeRebateConfig():
	global WZRR_RebateConfig_Dict
	for cfg in WangZheRechargeRebateConfig.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in WZRR_RebateConfig_Dict:
			print "GE_EXC, repeat rewardIndex (%s) in WZRR_RebateConfig_Dict" % rewardIndex
		WZRR_RebateConfig_Dict[rewardIndex] = cfg
		
class WangZheRechargeLotteryConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheRechargeLottery.txt")
	def __init__(self):
		self.waveIndex = int
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		self.itemIndex = int
		self.rateValue = int
		self.isPrecious = int
		self.rewardItem = self.GetEvalByString

def LoadWangZheRechargeLotteryConfig():
	global WZRR_LevelRange2ID_Dict
	global WZRR_LotteryConfig_Dict
	for cfg in WangZheRechargeLotteryConfig.ToClassType():
		waveIndex = cfg.waveIndex
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		itemIndex = cfg.itemIndex
		#等级段配置
		WZRR_LevelRange2ID_Dict[levelRangeId] = levelRange
		#奖励池配置
		waveIndexDict = WZRR_LotteryConfig_Dict.setdefault(waveIndex, {})
		levelRangeIdDict = waveIndexDict.setdefault(levelRangeId, {})
		if itemIndex in levelRangeIdDict:
			print "GE_EXC, repeat itemIndex(%s) in WZRR_LotteryConfig_Dict with waveIndex(%s) and levelRangeId(%s)" % (itemIndex, waveIndex, levelRangeId)
		levelRangeIdDict[itemIndex] = cfg		

def GetLevelRangeIdByLevel(roleLevel):
	'''
	返回对应角色等级的等级段ID
	'''
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in WZRR_LevelRange2ID_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	return tmpLevelRangeId

def GetDynamicRandomObj(waveIndex, levelRangeId, lotteryRecordSet):
	'''
	返回对应波次 等级段ID 已抽取记录 的下次抽奖随机器
	'''
	waveIndexDict = WZRR_LotteryConfig_Dict.get(waveIndex, {})
	levelRangeIdDict = waveIndexDict.get(levelRangeId, {})
	
	tmpRandomObj = Random.RandomRate()
	for itemIndex, rewardCfg in levelRangeIdDict.iteritems():
		if itemIndex in lotteryRecordSet:
			continue
		else:
			coding, cnt = rewardCfg.rewardItem
			rewardInfo = [rewardCfg.waveIndex, rewardCfg.levelRangeId, rewardCfg.itemIndex, coding, cnt, rewardCfg.isPrecious]
			tmpRandomObj.AddRandomItem(rewardCfg.rateValue, rewardInfo)
	
	return tmpRandomObj	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadWangZheRechargeRebateConfig()
		LoadWangZheRechargeLotteryConfig()