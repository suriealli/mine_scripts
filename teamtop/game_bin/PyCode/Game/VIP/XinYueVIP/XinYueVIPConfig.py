#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.VIP.XinYueVIP.XinYueVIPConfig")
#===============================================================================
# 心悦VIP配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile


if "_HasLoad" not in dir():
	XINYUE_VIP_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	XINYUE_VIP_FILE_FOLDER_PATH.AppendPath("XinYueVIP")
	
	XINYUE_ROLE_LEVEL_DICT = {}	#心悦玩家等级礼包配置
	XINYUE_REWARD_DICT = {}		#心悦奖励配置
	
class XinYueRoleLevelReward(TabFile.TabLine):
	'''
	心悦玩家等级礼包配置
	'''
	FilePath = XINYUE_VIP_FILE_FOLDER_PATH.FilePath("XinYueRoleLevelReward.txt")
	def __init__(self):
		self.index = int
		self.needVIPLevel = int
		self.needLevel = int
		self.codingRrward = self.GetEvalByString
		
def LoadXinYueRoleLevelReward():
	global XINYUE_ROLE_LEVEL_DICT
	
	for cfg in XinYueRoleLevelReward.ToClassType():
		if cfg.index in XINYUE_ROLE_LEVEL_DICT:
			print "GE_EXC,repeat index(%s) in LoadXinYueRoleLevelReward" % cfg.index
		XINYUE_ROLE_LEVEL_DICT[cfg.index] = cfg
	
class XinYuelReward(TabFile.TabLine):
	'''
	心悦vip等级奖励，每日，每周，每月奖励
	'''
	FilePath = XINYUE_VIP_FILE_FOLDER_PATH.FilePath("XinYuelReward.txt")
	def __init__(self):
		self.index = int
		self.needVIPLevel = int
		self.VIPLevelReward = self.GetEvalByString
		self.dayReward = self.GetEvalByString
		self.weekReward = self.GetEvalByString
		self.monthReward = self.GetEvalByString
		
def LoadXinYueReward():
	global XINYUE_REWARD_DICT
	
	for cfg in XinYuelReward.ToClassType():
		if cfg.index in XINYUE_REWARD_DICT:
			print "GE_EXC,repeat index(%s) in LoadXinYueReward" % cfg.index
		XINYUE_REWARD_DICT[cfg.index] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadXinYueRoleLevelReward()
		LoadXinYueReward()