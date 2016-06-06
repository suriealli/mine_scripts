#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.DELoginRewardConfig")
#===============================================================================
# 双十一2015 登陆有礼 config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DoubleEleven")
	
	CIRCULAR_FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CIRCULAR_FILE_FLODER_PATH.AppendPath("CircularActive")
	
	#登录有礼 基本配置 {dayIndex:{rewardIndex:cfg,},}
	DELoginReward_BaseConfig_Dict = {}
	
	#活动控制配置
	DELoginRewardActive_cfg = None


class DELoginReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DELoginReward.txt")
	def __init__(self):
		self.dayIndex = int
		self.rewardIndex = int
		self.needDayBuyRMB = int
		self.rewardItems = self.GetEvalByString
	

def LoadDELoginReward():
	global DELoginReward_BaseConfig_Dict
	for cfg in DELoginReward.ToClassType():
		dayIndex = cfg.dayIndex
		rewardIndex = cfg.rewardIndex
		dayIndexDict = DELoginReward_BaseConfig_Dict.setdefault(dayIndex, {})
		if rewardIndex in dayIndexDict:
			print "GE_EXC, repeat rewardIndex(%s) in DELoginReward_BaseConfig_Dict On dayIndex(%s) " % (rewardIndex, dayIndex)
		dayIndexDict[rewardIndex] = cfg


def GetCfgByIndex(dayIndex, rewardIndex):
	'''
	返回 天数索引dayIndex  的 奖励索引rewardIndex 对应配置 
	'''
	dayIndexDict = DELoginReward_BaseConfig_Dict.get(dayIndex, {})
	if rewardIndex not in dayIndexDict:
		return None
	else:
		return dayIndexDict[rewardIndex]


class DELoginRewardActive(TabFile.TabLine):
	FilePath = CIRCULAR_FILE_FLODER_PATH.FilePath("DELoginRewardActive.txt")
	def __init__(self):
		self.activeIndex = int
		self.activeName = str
		self.beginTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.totalDay = int
	
def LoadDELoginRewardActive():
	'''
	加载并启动活动
	'''
	global DELoginRewardActive_cfg
	for cfg in DELoginRewardActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in DELoginRewardActive_Dict"
			continue
		DELoginRewardActive_cfg = cfg
			

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDELoginReward()
		LoadDELoginRewardActive()
