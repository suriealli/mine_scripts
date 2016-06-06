#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationalDayFB.NationalDayFBConfig")
#===============================================================================
# 国庆副本配置表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	NDFB_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	NDFB_FILE_FOLDER_PATH.AppendPath("NationDay")

	NATION_KILL_REWARD_DICT = {}	#副本击杀配置
	NATION_GLOBAL_REWARD_DICT = {}	#全民击杀奖励
	NATION_KILLCNT_LIST = set()
	
class NationFBKillReward(TabFile.TabLine):
	#副本杀怪奖励配置
	FilePath = NDFB_FILE_FOLDER_PATH.FilePath("NationFBKillReward.txt")
	def __init__(self):
		self.roleLevel	= int
		self.maxExp		= int
		self.addExp		= int
		self.pro1		= int
		self.rewards1	= self.GetEvalByString
		self.pro2		= int
		self.rewards2	= self.GetEvalByString
		self.campId		= int
		self.fightType	= int
		
class NationFBReward(TabFile.TabLine):
	#副本全民击杀奖励
	FilePath = NDFB_FILE_FOLDER_PATH.FilePath("NationFBReward.txt")
	def __init__(self):
		self.Index		 = int
		self.FightCnt	 = int
		self.rewards	 = self.GetEvalByString
		
def LoadNationFBExp():
	global NATION_KILL_REWARD_DICT
	
	for cfg in NationFBKillReward.ToClassType():
		if cfg.roleLevel in NATION_KILL_REWARD_DICT:
			print "GE_EXC, repeat roleLevel(%s) in LoadNationFBExp" % cfg.roleLevel
		NATION_KILL_REWARD_DICT[cfg.roleLevel] = cfg
		
def LoadNationFBReward():
	global NATION_GLOBAL_REWARD_DICT
	global NATION_KILLCNT_LIST
	
	for cfg in NationFBReward.ToClassType():
		if cfg.Index in NATION_GLOBAL_REWARD_DICT:
			print "GE_EXC, repeat Index(%s) in LoadNationFBReward" % cfg.Index
		NATION_GLOBAL_REWARD_DICT[cfg.Index] = cfg
		NATION_KILLCNT_LIST.add(cfg.FightCnt)
			
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadNationFBExp()
		LoadNationFBReward()
		