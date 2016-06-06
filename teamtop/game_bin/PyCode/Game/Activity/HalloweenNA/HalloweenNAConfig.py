#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HalloweenNA.HalloweenNAConfig")
#===============================================================================
# 北美万圣节配置
#===============================================================================
import datetime
import DynamicPath
import Environment
import cDateTime
from Util.File import TabFile
from Game.Role import Event
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	NA_HALLOWEEN_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	NA_HALLOWEEN_FILE_FOLDER_PATH.AppendPath("HalloweenNA")

	ActiveVersion = 14 #当前活动的版本号(每次调整时间都要加1)
	
	HALLOWEENNA_ACT_BASE = {}	#基础配置
	HALLOWEENNA_ACT_REWARD = {}	#奖励配置表
	HALLOWEENNA_ID_TO_IDX = {}	#活动ID对应idx
	HALLOWEENNA_STARING_SET = set()	#正在开启的活动
	
def InitIsActive():
	global HALLOWEENNA_ACT_BASE
	global HALLOWEENNA_STARING_SET
	
	HALLOWEENNA_STARING_SET = set()	#清空正在开启的活动
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for actId, cfg in HALLOWEENNA_ACT_BASE.iteritems():
		if cfg.startDateTime == datetime.datetime(2038, 1, 1) or \
			cfg.endDateTime == datetime.datetime(2038, 1, 1):
			continue
		nowDateTime = cDateTime.Now()
		if nowDateTime < cfg.startDateTime or nowDateTime > cfg.endDateTime:
			continue
		else:
			if kaifuDay < cfg.kaifuDays:
				continue
			HALLOWEENNA_STARING_SET.add(actId)
		
class HalloweenNABase(TabFile.TabLine):
	'''
	北美万圣节基础配置
	'''
	FilePath = NA_HALLOWEEN_FILE_FOLDER_PATH.FilePath("HalloweenNABase.txt")
	def __init__(self):
		self.actId	 = int
		self.startDateTime = self.GetDatetimeByString
		self.endDateTime = self.GetDatetimeByString
		self.tabEndDay = int
		self.level	 = int
		self.kaifuDays = int
		
class HalloweenNAReward(TabFile.TabLine):
	'''
	北美万圣节奖励配置
	'''
	FilePath = NA_HALLOWEEN_FILE_FOLDER_PATH.FilePath("HalloweenNAReward.txt")
	def __init__(self):
		self.actId	 = int
		self.idx	 = int
		self.rewardMoney = int
		self.rewardRMB = int
		self.rewardTarot = int
		self.rewardItem = self.GetEvalByString
		self.needBuyUnbindRMB = int
		self.needPurgatoryId = int
		self.needPurgatoryPassCnt = int
		self.needFinishGVEFBCnt = int
		self.needJJCCnt = int
		self.needFinishFBCnt = int
		self.needFinishUnionFBCnt = int
		self.needSlavePlayCnt = int
		self.needOnlineTime = int
		self.HeroLevel = self.GetEvalByString
		self.HeroIds = self.GetEvalByString
		self.maxCnt = int
		self.needGoldCnt = int
		self.WingculCnt = int
		self.GemsynCnt = self.GetEvalByString
		self.SaveSlaveCnt = int
		self.challengeTimes = int
		self.costRMB = self.GetEvalByString
		self.PetevlTimes = int
		self.Petstar = int
		self.needMountTrainCnt = int
		self.needMountRMBTrainCnt = int
		self.EvlHoleTimes = int
		self.CatchSlaveTimes = int
		self.ChallengHeroTimes = int
		self.TotalcostRMB = int
		self.PetSpiritLevel = int
		self.PetLuckyDraw = int
		self.EquipmentStengCnt = int
		self.PetEvoId = int
		self.tarotCntDict = self.GetEvalByString
		self.tarotCnt = int
		self.dayBuyGem = int
		self.fuwenSyn = self.GetEvalByString
		self.partytimes = self.GetEvalByString
		self.CFbtimes = int
		
class HalloweenNAVersion(TabFile.TabLine):
	'''
	活动版本号
	'''
	FilePath = NA_HALLOWEEN_FILE_FOLDER_PATH.FilePath("HalloweenNAVersion.txt")
	def __init__(self):
		self.Version = int
		
def LoadHallowNAVersion():
	global ActiveVersion
	for cfg in HalloweenNAVersion.ToClassType():
		ActiveVersion = cfg.Version
	
def LoadHalloweenNABase():
	global HALLOWEENNA_ACT_BASE
	
	for cfg in HalloweenNABase.ToClassType():
		if cfg.actId in HALLOWEENNA_ACT_BASE:
			print "GE_EXC,repeat actid(%s) in LoadHalloweenNABase" % cfg.actId
		HALLOWEENNA_ACT_BASE[cfg.actId] = cfg
		
def LoadHalloweenNAReward():
	global HALLOWEENNA_ACT_REWARD
	global HALLOWEENNA_ID_TO_IDX
	
	for cfg in HalloweenNAReward.ToClassType():
		key = (cfg.actId, cfg.idx)
		if key in HALLOWEENNA_ACT_REWARD:
			print "GE_EXC,repeat actId(%s) and idx(%s) in LoadHalloweenNAReward" % (cfg.actId, cfg.idx)
		HALLOWEENNA_ACT_REWARD[key] = cfg
		HALLOWEENNA_ID_TO_IDX.setdefault(cfg.actId, []).append( cfg.idx)
		
def AfterLoadWorldData(param1, param2):
	InitIsActive()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadHalloweenNABase()
		LoadHalloweenNAReward()
		LoadHallowNAVersion()
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		