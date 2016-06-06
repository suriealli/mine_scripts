#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QQHallLottery.QQHallLotteryConfig")
#===============================================================================
# 大厅搏饼配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QQHallLottery")
	
	QQHALL_LOTTERY_REWARD_DICT = {}			#大厅搏饼奖励{rewardId:{levelRange:cfg,},}	
	QQHALL_LATTERY_EXTRA_TIMES_DICT = {}	#大厅每日充值神石获得额外搏饼次数配置{id:cfg,}

class QQHallLotteryReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('QQHallLotteryReward.txt')
	def __init__(self):
		self.rewardId = int 
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		
		self.name = str
		self.rewardCoin = int
		self.nomalItems = self.GetEvalByString
		
class QQHallLotteryTimes(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('QQHallLotteryTimes.txt')
	def __init__(self):
		self.id = int
		self.value = int 
		self.extraNum = int 
		
def LoadQQHallLatteryReward():
	global QQHALL_LOTTERY_REWARD_DICT
	for cfg in QQHallLotteryReward.ToClassType():
		rewardId, levelRangeId = cfg.rewardId, cfg.levelRangeId
		if rewardId not in QQHALL_LOTTERY_REWARD_DICT:
			QQHALL_LOTTERY_REWARD_DICT[rewardId] = {}
		if levelRangeId in QQHALL_LOTTERY_REWARD_DICT[rewardId]:
			print "GE_EXC,LoadQQHallLatteryReward::repeat cfg with rewardId(%s),levelRangeId(%s)" % (rewardId, levelRangeId)
		QQHALL_LOTTERY_REWARD_DICT[rewardId][levelRangeId] = cfg

def LoadQQHallLotteryTimes():
	global QQHALL_LATTERY_EXTRA_TIMES_DICT
	for cfg in QQHallLotteryTimes.ToClassType():
		if cfg.id in QQHALL_LATTERY_EXTRA_TIMES_DICT:
			print "GE_EXC, LoadQQHallLotteryTimes::repeat id(%s)" % cfg.id
		QQHALL_LATTERY_EXTRA_TIMES_DICT[cfg.id] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQHallLatteryReward()
		LoadQQHallLotteryTimes()