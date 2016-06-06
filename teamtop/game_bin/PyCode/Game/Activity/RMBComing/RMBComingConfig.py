#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RMBComing.RMBComingConfig")
#===============================================================================
# 神石滚滚来配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	RMBCOMING_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	RMBCOMING_FILE_FOLDER_PATH.AppendPath("RMBComing")
	
	RMB_COMING_DICT = {}
	RMB_COMING_REWARD_DICT = {}
	
class RMBComing(TabFile.TabLine):
	'''
	神石滚滚来配置
	'''
	FilePath = RMBCOMING_FILE_FOLDER_PATH.FilePath("RMBComing.txt")
	def __init__(self):
		self.index = int
		self.needUnbindRMB_Q = int
		self.fillRMB = int
		self.needDay1 = int
		self.day1 = int
		self.needDay2 = int
		self.day2 = int
		self.needDay3 = int
		self.day3 = int
		self.needDay4 = int
		self.day4 = int
		self.needDay5 = int
		self.day5 = int
		self.needDay6 = int
		self.day6 = int
		self.needDay7 = int
		self.day7 = int
		
class RMBComingReward(TabFile.TabLine):
	'''
	购买红包后给的奖励
	'''
	FilePath = RMBCOMING_FILE_FOLDER_PATH.FilePath("RMBComingReward.txt")
	def __init__(self):
		self.level = int
		self.reward1 = self.GetEvalByString
		self.reward2 = self.GetEvalByString
		self.reward3 = self.GetEvalByString
		
def LoadRedEnvelopeReward():
	global RMB_COMING_REWARD_DICT
	
	for cfg in RMBComingReward.ToClassType():
		if cfg.level in RMB_COMING_REWARD_DICT:
			print "GE_EXC,repeat level(%s) in LoadRedEnvelopeReward" % cfg.level
		RMB_COMING_REWARD_DICT[cfg.level] = cfg
		
def LoadRMBComing():
	global RMB_COMING_DICT
	
	for cfg in RMBComing.ToClassType():
		if cfg.index in RMB_COMING_DICT:
			print "GE_EXC,repeat index(%s) in LoadRedEnvelope" % cfg.index
		RMB_COMING_DICT[cfg.index] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRMBComing()
		LoadRedEnvelopeReward()
		