#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WonderfulAct.WonderfulActConfig")
#===============================================================================
# 精彩活动配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.SysData import WorldData


if "_HasLoad" not in dir():
	WONDERFUL_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	WONDERFUL_FILE_FOLDER_PATH.AppendPath("WonderfulAct")
	
	WONDERFUL_BASE_DICT = {}#精彩活动总配置
	WONDER_REWARD_DICT = {} #奖励配置表
	WONDER_FOREVER_REWARD = {} #记录合服前无时限的活动
	WONDER_HEFU_FOREVER_REWARD = {}	#记录合服后的无时限的活动
	WONDER_DAY_FRESH_LIST = [] #缓存份需要每日刷新的活动列表


class WonderfulAct(TabFile.TabLine):
	'''
	精彩活动总配置
	'''
	FilePath = WONDERFUL_FILE_FOLDER_PATH.FilePath("WonderfulAct.txt")
	def __init__(self):
		self.actId = int
		self.desc = str
		self.starttime = self.GetDatetimeByString
		self.endtime = self.GetDatetimeByString
		self.IsHefu = int
		self.hefutime = int
		self.kaifutime = int
		self.keepday = int
		self.rewardday = int
		self.dayfresh = int
		self.daytick = int
		self.rewardList = self.GetEvalByString
		self.processIds = self.GetEvalByString
		
class WonderfulReward(TabFile.TabLine):
	'''
	精彩活动奖励配置表
	'''
	FilePath = WONDERFUL_FILE_FOLDER_PATH.FilePath("WonderfulReward.txt")
	def __init__(self):
		self.rewardId		= int
		self.needVIP		= int
		self.level			= int
		self.needZDL		= int
		self.needFill		= int
		self.bugCard		= int
		self.fillNum		= int
		self.cardNum		= int
		self.oneFlyNum		= self.GetEvalByString
		self.VIPNum			= self.GetEvalByString
		self.orangeHeroNum	= self.GetEvalByString
		self.needGemNum		= int
		self.needGemNumDay	= int
		self.TarotNum		= int
		self.TarotNumDay	= int
		self.mountLevel		= int
		self.singleFill		= int
		self.equipNum		= self.GetEvalByString
		self.mountNumber	= self.GetEvalByString
		self.TotalFill		= int
		self.TotalGem		= int
		self.totalTaro		= int
		self.MallWing		= self.GetEvalByString
		self.UnionTreNum	= self.GetEvalByString
		self.TotalRMB		= int
		self.PetNum			= self.GetEvalByString
		self.MarryCnt		= int
		self.RingLevel		= int
		self.HefuDay		= int
		self.WingTimes		= int
		self.TogWingTimes	= int
		self.PetTimes		= int
		self.TogPetTimes	= int
		self.unionFill		= int
		self.needFeedTimes	= int
		self.unionGod		= self.GetEvalByString
		self.petEvoTimes	= int
		self.totalPetTimes	= int
		self.upstartimes	= int
		self.totalUpstar	= int
		self.upordertimes	= int
		self.totalUpOrder	= int
		self.StarGirlLevel	= int
		self.totalStarGirlLevel = int
		self.StarGirlStar	= int
		self.totalStarGirlStar = int
		self.dragonLevel	= int
		self.totaldragonLevel = int
		self.dragonEvo		= int
		self.totaldragonEvo	= int
		self.titleLevel		= int
		self.totaltitleLevel= int
		self.maxNum			= int
		self.rewardItem		= self.GetEvalByString
		self.bindRMB		= int
		self.money			= int
		self.rewardTarot 	= int
		self.rewardHero 	= int
		self.UnbindRMB_S	= int
		self.Reputation		= int
		self.rewardTiLi		= int
		self.TaortHP		= int
		
def LoadWonderfulActBase():
	global WONDERFUL_BASE_DICT
	global WONDER_FOREVER_REWARD
	global WONDER_HEFU_FOREVER_REWARD
	global WONDER_DAY_FRESH_LIST
	
	for cfg in WonderfulAct.ToClassType():
		if cfg.actId in WONDERFUL_BASE_DICT:
			print "GE_EXC,repeat actId in WonderfulAct,(%s)" % cfg.actId
		WONDERFUL_BASE_DICT[cfg.actId] = cfg
	#将无时限的活动缓存
	for actId, cfg in WONDERFUL_BASE_DICT.iteritems():
		if cfg.keepday == -1:
			if cfg.IsHefu == 1:#合服前开启
				if actId not in WONDER_FOREVER_REWARD:
					WONDER_FOREVER_REWARD[actId] = set()
				if type(cfg.rewardList) == int:
					WONDER_FOREVER_REWARD[actId].add(cfg.rewardList)
				elif type(cfg.rewardList) == list:
					for rewardId in cfg.rewardList:
						WONDER_FOREVER_REWARD[actId].add(rewardId)
			elif cfg.IsHefu == 2:#合服后开启
				if actId not in WONDER_HEFU_FOREVER_REWARD:
					WONDER_HEFU_FOREVER_REWARD[actId] = set()
				if type(cfg.rewardList) == int:
					WONDER_HEFU_FOREVER_REWARD[actId].add(cfg.rewardList)
				elif type(cfg.rewardList) == list:
					for rewardId in cfg.rewardList:
						WONDER_HEFU_FOREVER_REWARD[actId].add(rewardId)
			else:#和合服不相关的无时限活动
				if actId not in WONDER_FOREVER_REWARD:
					WONDER_FOREVER_REWARD[actId] = set()
				if type(cfg.rewardList) == int:
					WONDER_FOREVER_REWARD[actId].add(cfg.rewardList)
				elif type(cfg.rewardList) == list:
					for rewardId in cfg.rewardList:
						WONDER_FOREVER_REWARD[actId].add(rewardId)
				if actId not in WONDER_HEFU_FOREVER_REWARD:
					WONDER_HEFU_FOREVER_REWARD[actId] = set()
				if type(cfg.rewardList) == int:
					WONDER_HEFU_FOREVER_REWARD[actId].add(cfg.rewardList)
				elif type(cfg.rewardList) == list:
					for rewardId in cfg.rewardList:
						WONDER_HEFU_FOREVER_REWARD[actId].add(rewardId)
		if cfg.dayfresh:#缓存份每日刷新的活动列表
			WONDER_DAY_FRESH_LIST.append(actId)

def LoadWonderfulReward():
	global WONDER_REWARD_DICT
	for cfg in WonderfulReward.ToClassType():
		if cfg.rewardId in WONDER_REWARD_DICT:
			print "GE_EXC,repeat rewardId in WonderfulReward,(%s)" % cfg.rewardId
		WONDER_REWARD_DICT[cfg.rewardId] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadWonderfulActBase()
		LoadWonderfulReward()
		