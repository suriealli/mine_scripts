#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaiFuAct.KaiFuActConfig")
#===============================================================================
# 开服活动配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

KAI_FU_ACT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
KAI_FU_ACT_FILE_FOLDER_PATH.AppendPath("KaiFuAct")

if "_HasLoad" not in dir():
	KAI_FU_ACT_BASE = {}
	KAI_FU_ACT_REWARD = {}
	KAI_FU_ACT_ID_TO_IDX = {}		#开服活动ID索引活动枚举
	
class KaiFuActBase(TabFile.TabLine):
	'''
	开服活动配置表
	'''
	FilePath = KAI_FU_ACT_FILE_FOLDER_PATH.FilePath("KaiFuActBase.txt")
	def __init__(self):
		self.actId = int
		self.startDay = int
		self.endDay = int
		self.tabEndDay = int
		
class KaiFuActReward(TabFile.TabLine):
	'''
	开服活动奖励配置表
	'''
	FilePath = KAI_FU_ACT_FILE_FOLDER_PATH.FilePath("KaiFuActReward.txt")
	def __init__(self):
		self.actId = int
		self.idx = int
		self.rewardMoney = int
		self.rewardRMB = int
		self.rewardItem = self.GetEvalByString
		
		self.needTiLi = int
		self.needDailyDoScore = int
		self.needMountEvolveId = int
		self.needGoldCnt = int
		self.needOnlineTime = int
		self.needYellowTarotCnt = int
		self.needTarotLevel = int
		self.needXinYueChangGong = int
		self.needXinYueZhanFu = int
		self.needUnionFB = self.GetEvalByString
		self.needDragonLevel = int
		self.needRuneCnt = int
		self.needMountTrainCnt = int
		self.needMountLevelCnt = self.GetEvalByString
		self.needWingTrainCnt = int
		self.needWingLevel = int
		self.needVIP = int
		self.needPetCulCnt = int
		self.needPetLevelCnt = self.GetEvalByString
		self.needFuwenLevel = int
		
def LoadKaiFuActBase():
	global KAI_FU_ACT_BASE
	for config in KaiFuActBase.ToClassType():
		KAI_FU_ACT_BASE[config.actId] = config 
		
def LoadKaiFuActReward():
	global KAI_FU_ACT_REWARD
	global KAI_FU_ACT_ID_TO_IDX
	for config in KaiFuActReward.ToClassType():
		KAI_FU_ACT_REWARD[(config.actId, config.idx)] = config 
		KAI_FU_ACT_ID_TO_IDX.setdefault(config.actId, []).append( config.idx)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadKaiFuActBase()
		LoadKaiFuActReward()
		
		
		