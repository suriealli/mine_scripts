#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTJHCConfig")
#===============================================================================
# 天降横财 config
#===============================================================================
from Util.File import TabFile
import DynamicPath
import Environment
from Common.Other import EnumGameConfig

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	#天降横财奖励池配置 {rewardId:cfg,}
	TJHC_RewardConfig_Dict = {}
	#天降横财回合控制 {roundId:cfg,}
	TJHC_LotteryControl_Dict = {}
	#默认初始10奖励神石 再读配置
	TJHC_NomalReward = (28687,10)

class PassionTJHCReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTJHCReward.txt")
	def __init__(self):
		self.rewardId = int
		self.lotteryNeedCnt = int
		self.rewardItem = self.GetEvalByString
		self.isPrecious = int


def LoadPassionTJHCReward():
	global TJHC_NomalReward
	global TJHC_RewardConfig_Dict
	for cfg in PassionTJHCReward.ToClassType():
		rewardId = cfg.rewardId
		if rewardId in TJHC_RewardConfig_Dict:
			print "GE_EXC,repeat rewardId(%s) in TJHC_RewardConfig_Dict" % rewardId
		TJHC_RewardConfig_Dict[rewardId] = cfg
		
		if rewardId == EnumGameConfig.TJHC_NOMAL_REWARDID:
			TJHC_NomalReward = cfg.rewardItem
			

class PassionTJHCControl(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTJHCControl.txt")
	def __init__(self):
		self.roundId = int
		self.syncTime = self.GetDatetimeByString
		self.lotteryTime = self.GetDatetimeByString
		self.rewardPool = self.GetEvalByString


def LoadPassionTJHCControl():
	global TJHC_LotteryControl_Dict
	for cfg in PassionTJHCControl.ToClassType():
		roundId = cfg.roundId
		if roundId in TJHC_LotteryControl_Dict:
			print "GE_EXC,repeat roundId(%s) in TJHC_LotteryControl_Dict" % roundId
		
		for rewardId, _ in cfg.rewardPool:
			if rewardId not in TJHC_RewardConfig_Dict:
				print "GE_EXC, error rewardId(%s) of roundId(%s) that not in TJHC_RewardConfig_Dict" % (rewardId, roundId)
				
		TJHC_LotteryControl_Dict[roundId] = cfg

def LoadTJHCConfig():
	'''
	先加载奖励池
	'''
	LoadPassionTJHCReward()
	LoadPassionTJHCControl()
		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadTJHCConfig()
