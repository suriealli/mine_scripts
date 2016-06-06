#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DailyMountLottery.DailyMountLotteryConfig")
#===============================================================================
# 天马行空配置
#===============================================================================
import copy
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DailyMountLottery")
	
	#抽奖配置
	DAILY_MOUNT_LOTTERY_CONFIG_DICT = {}	#{lotteryTimes:cfg,}
	DAILY_MOUNT_LOTTERY_TIMES_MAX	= 0		#配置项中最大抽奖次数

class DailyMountLottry(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('DailyMountLottery.txt')
	def __init__(self):
		self.lotteryTimes 	= int	#抽奖次数
		self.needRMB 		= int	#所需神石	 		
		self.rateItems = self.GetEvalByString	#随机奖励池
		self.extraItem = self.GetEvalByString	#额外奖励
		self.specialItem = self.GetEvalByString	#特殊奖励(PS:奖励池 = 随机奖励 + 额外奖励 若在奖励池中抽出奖励属于特殊奖励 广播之)
	
	def Preprocess(self):
		specialItemList = []
		for coding, cnt in self.specialItem:
			specialItemList.append(coding)
		
		self.randomer = Random.RandomRate()
		for coding, cnt, rate in self.rateItems:
			if coding in specialItemList:
				self.randomer.AddRandomItem(rate, (coding, cnt, 1))
			else:
				self.randomer.AddRandomItem(rate, (coding,cnt, 0))

def GetLotteryCfgByTimes(lotteryTimes = 1):
	'''
	获取此次请求抽奖所对应次数的配置
	'''
	if lotteryTimes < 1:
		print "GE_EXC,GetLotteryCfgByTimes::error lotteryTimes(%s)" % lotteryTimes
		return None
	
	lotteryCfg = DAILY_MOUNT_LOTTERY_CONFIG_DICT.get(lotteryTimes, None)
	if not lotteryCfg:
		lotteryCfg = DAILY_MOUNT_LOTTERY_CONFIG_DICT[DAILY_MOUNT_LOTTERY_TIMES_MAX]
	
	#外层逻辑 在今日抽奖总次数 和 当前未抽中特殊奖励累计次数不相同时 
	#会有 lotteryCfg_a.randomer = lotteryCfg_b.randomer的操作 组合出此次抽奖的完整配置项
	#为保证配置DAILY_MOUNT_LOTTERY_CONFIG_DICT不被改变  故返回deepcopy
	return copy.deepcopy(lotteryCfg)

def LoadDaliyMountLottery():
	tmpList = [] 
	global DAILY_MOUNT_LOTTERY_TIMES_MAX
	global DAILY_MOUNT_LOTTERY_CONFIG_DICT
	for cfg in DailyMountLottry.ToClassType():
		if cfg.lotteryTimes in DAILY_MOUNT_LOTTERY_CONFIG_DICT:
			print "GE_EXC,repeat lotteryTimes(%s) in DAILY_MOUNT_LOTTERY_CONFIG_DICT" % cfg.lotteryTimes
			
		DAILY_MOUNT_LOTTERY_CONFIG_DICT[cfg.lotteryTimes] = cfg
		tmpList.append(cfg.lotteryTimes)
		cfg.Preprocess()
	
	tmpList.sort()
	DAILY_MOUNT_LOTTERY_TIMES_MAX = tmpList[-1]

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDaliyMountLottery()