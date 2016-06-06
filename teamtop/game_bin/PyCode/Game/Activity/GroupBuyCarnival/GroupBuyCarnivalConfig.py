#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GroupBuyCarnival.GroupBuyCarnivalConfig")
#===============================================================================
# 团购嘉年华配置
#===============================================================================
from Util.File import TabFile
import DynamicPath
import Environment

if "_HasLoad" not in dir():
	
	FILE_FLOOR_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLOOR_PATH.AppendPath("GroupBuyCarnival")
	
	GBC_BASE_CONFIG = None	#活动基础配置
	GBC_REWARD_CONFIG_DICT = {}	#团购及奖励配置{dayIndex:{cfg},}

class GroupBuyCarnivalConfig(TabFile.TabLine):
	FilePath = FILE_FLOOR_PATH.FilePath("GroupBuyCarnival.txt")
	def __init__(self):
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.totalDay = int
				
class GroupBuyCarnivalReward(TabFile.TabLine):
	FilePath = FILE_FLOOR_PATH.FilePath("GroupBuyCarnivalReward.txt")
	def __init__(self):
		self.dayIndex = int 
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.item = self.GetEvalByString
		self.needRMB = int
		self.rewards = self.GetEvalByString

def GetGBCConfig(dayIndex = 1, roleLevel = 1):
	'''
	根据天数索引和等级 获取cfg
	'''
	dayCfgDict = GBC_REWARD_CONFIG_DICT.get(dayIndex)
	if not dayCfgDict:
		print "GE_EXC,can not find dayCfgDict with dayIndex(%s)" % dayIndex
		return None
	retCfg = None
	for _, retCfg in dayCfgDict.iteritems():
		levelDown, levelUp = retCfg.levelRange
		if levelDown <= roleLevel <= levelUp:
			return retCfg
	return retCfg

def LoadGroupBuyCarnivalConfig():
	global GBC_BASE_CONFIG
	for cfg in GroupBuyCarnivalConfig.ToClassType():
		GBC_BASE_CONFIG = cfg
	
	
		
def LoadGroupBuyCarnivalReward():
	global GBC_REWARD_CONFIG_DICT
	for cfg in GroupBuyCarnivalReward.ToClassType():
		dayCfgDict = GBC_REWARD_CONFIG_DICT.setdefault(cfg.dayIndex,{})
		if cfg.rangeId in dayCfgDict:
			print "GE_EXC,repeat rangeId(%s) in dayIndex(%s) of GroupBuyCarnivalReward" % (cfg.rangeId,cfg.dayIndex)
		dayCfgDict[cfg.rangeId] = cfg
	
	global GBC_BASE_CONFIG
	if GBC_BASE_CONFIG.totalDay != len(GBC_REWARD_CONFIG_DICT):
		print "GE_EXC,GroupBuyCarnivalConfig::GBC_BASE_CONFIG.totalDay != len(GBC_REWARD_CONFIG_DICT)"

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadGroupBuyCarnivalConfig()
		LoadGroupBuyCarnivalReward() 