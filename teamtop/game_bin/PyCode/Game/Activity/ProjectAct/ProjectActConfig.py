#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ProjectAct.ProjectActConfig")
#===============================================================================
# 专题活动配置
#===============================================================================

import Environment
import DynamicPath
from Util.File import TabFile


if "_HasLoad" not in dir():
	PROACT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	PROACT_FILE_FOLDER_PATH.AppendPath("ProjectAct")
	
	ACT_BASE_DICT = {}	#专题基础配置
	ACT_REWARD_DICT = {}	#专题活动奖励配置
	
	
class ProjectAct(TabFile.TabLine):
	'''
	专题活动基础配置表
	'''
	FilePath = PROACT_FILE_FOLDER_PATH.FilePath("ProjectAct.txt")
	def __init__(self):
		self.actId		 = int
		self.daytick	 = int
		self.rewardList	 = self.GetEvalByString

class ProjectReward(TabFile.TabLine):
	'''
	专题活动奖励配置
	'''
	FilePath = PROACT_FILE_FOLDER_PATH.FilePath("ProjectActReward.txt")
	def __init__(self):
		self.rewardId	 = int
		self.level		 = int
		self.needZDL	 = int
		self.oneFlyNum	 = self.GetEvalByString
		self.mountLevel	 = int
		self.PetNum		 = self.GetEvalByString
		self.GemNum		 = self.GetEvalByString
		self.mountCulNum = int
		self.wishTimes	 = int
		self.wingTimes	 = int
		self.FuWenNum	 = self.GetEvalByString
		self.tarotTimes	 = self.GetEvalByString
		self.PetTimes	 = int
		self.RingTimes	 = int
		self.StarGirlStar= int
		self.rewardItem	 = self.GetEvalByString
		self.rewardTiLi	 = int
		self.rewardTarot = int
		self.rewardHero	 = int
		self.bindRMB	 = int
		self.money		 = int
		self.UnbindRMB_S = int
		self.Reputation	 = int
		self.TaortHP	 = int
		self.TempBless	 = self.GetEvalByString
		
def LoadProjectAct():
	global ACT_BASE_DICT
	
	for cfg in ProjectAct.ToClassType():
		if cfg.actId in ACT_BASE_DICT:
			print "GE_EXC, repeat actId(%s) in LoadProjectAct" % cfg.actId
			continue
		ACT_BASE_DICT[cfg.actId] = cfg
		
def LoadProjectActReward():
	global ACT_REWARD_DICT
	
	for cfg in ProjectReward.ToClassType():
		if cfg.rewardId in ACT_REWARD_DICT:
			print "GE_EXC, repeat rewardId(%s) in LoadProjectActReward" % cfg.rewardId
			continue
		ACT_REWARD_DICT[cfg.rewardId] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadProjectAct()
		LoadProjectActReward()
		