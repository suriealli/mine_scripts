#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenAct.SevenActConfig")
#===============================================================================
# 七日活动配置
#===============================================================================
import DynamicPath
import Environment
import datetime
from Util.File import TabFile
import cDateTime

SEVEN_ACT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
SEVEN_ACT_FILE_FOLDER_PATH.AppendPath("SevenAct")

if "_HasLoad" not in dir():
	SEVEN_ACT_BASE = {}
	SEVEN_ACT_REWARD = {}
	SEVEN_ACT_ID_TO_IDX = {}		#七日活动ID索引活动枚举
	
	IsActive = False
	ActiveVersion = 1 #当前活动的版本号(每次调整时间都要加1)
	startDateTime = datetime.datetime(2015, 3, 8, 0, 0)
	endDateTime = datetime.datetime(2015, 3, 14, 23, 59)


def InitIsActive():
	global IsActive
	nowDateTime = cDateTime.Now()
	#判断活动是否已经结束
	if nowDateTime < startDateTime or nowDateTime > endDateTime:
		IsActive =  False
	else:
		IsActive = True


class SevenActBase(TabFile.TabLine):
	'''
	七日活动配置表
	'''
	FilePath = SEVEN_ACT_FILE_FOLDER_PATH.FilePath("SevenActBase.txt")
	def __init__(self):
		self.actId = int
		self.startDay = int
		self.endDay = int
		self.tabEndDay = int
		
class SevenActReward(TabFile.TabLine):
	'''
	七日活动奖励配置表
	'''
	FilePath = SEVEN_ACT_FILE_FOLDER_PATH.FilePath("SevenActReward.txt")
	def __init__(self):
		self.actId = int
		self.idx = int
		self.rewardMoney = int
		self.rewardRMB = int
		self.rewardItem = self.GetEvalByString
		
		self.needBuyUnbindRMB = int
		self.needGoldCnt = int
		self.needMountTrainCnt = int
		self.needLoginCnt = int
		self.needPurgatoryId = int
		self.needPurgatoryPassCnt = int
		self.needFinishGVEFBCnt = int
		self.needJJCCnt = int
		self.needFinishFBCnt = int
		self.needFinishUnionFBCnt = int
		self.needSlavePlayCnt = int
		self.needOnlineTime = int
		
		
def LoadSevenActBase():
	global SEVEN_ACT_BASE
	for config in SevenActBase.ToClassType():
		SEVEN_ACT_BASE[config.actId] = config 
		
def LoadSevenActReward():
	global SEVEN_ACT_REWARD
	global SEVEN_ACT_ID_TO_IDX
	for config in SevenActReward.ToClassType():
		SEVEN_ACT_REWARD[(config.actId, config.idx)] = config 
		SEVEN_ACT_ID_TO_IDX.setdefault(config.actId, []).append( config.idx)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		InitIsActive()
		LoadSevenActBase()
		LoadSevenActReward()
		
		
		