#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.FeastWheelConfig")
#===============================================================================
# 盛宴摩天轮配置
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DoubleTwelve")
	
	FeastWheel_LotteryReward_Dict = {}	#抽奖奖励池配置
	FeastWheel_RechargeReward_Dict = {}	#充值奖励抽奖次数配置
	
	FeastWheel_LotteryReward_RandomObj_RMB = Random.RandomRate()	#盛宴摩天轮抽奖随机器-RMB[(rate,(rewardId,isPrecious, item)),]
	FeastWheel_LotteryReward_RandomObj_Nomal = Random.RandomRate()	#盛宴摩天轮抽奖随机器-普通[(rate,(rewardId,isPrecious, item)),]

class FWLotteryReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("FWLotteryReward.txt")
	def __init__(self):
		self.rewardId = int
		self.item = self.GetEvalByString
		self.isPrecious = int
		self.RMBRate = int		#充值获得次数抽奖概率
		self.nomalRate = int 	#普通次数抽奖概率
	
class FWRechargeReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("FWRechargeReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needRechargeRMB = int
		self.rewardTimes = int

def LoadFWLotteryReward():
	global FeastWheel_LotteryReward_Dict
	for cfg in FWLotteryReward.ToClassType():
		if cfg.rewardId in FeastWheel_LotteryReward_Dict:
			print "GE_EXC,repeat rewardId(%s) in FWLotteryReward" % cfg.rewardId
		FeastWheel_LotteryReward_Dict[cfg.rewardId] = cfg
	
	AfterLoadFWLotteryReward()

def AfterLoadFWLotteryReward():
	'''
	构建抽奖的奖励随机器
	'''
	global FeastWheel_LotteryReward_RandomObj_RMB
	global FeastWheel_LotteryReward_RandomObj_Nomal
	for rewardId, rewardCfg in FeastWheel_LotteryReward_Dict.iteritems():
		rewardInfo = (rewardId,rewardCfg.isPrecious, rewardCfg.item)
		FeastWheel_LotteryReward_RandomObj_RMB.AddRandomItem(rewardCfg.RMBRate, rewardInfo)
		FeastWheel_LotteryReward_RandomObj_Nomal.AddRandomItem(rewardCfg.nomalRate, rewardInfo)
	
def LoadFWRechargeReward():
	global FeastWheel_RechargeReward_Dict
	for cfg in FWRechargeReward.ToClassType():
		if cfg.rewardIndex in FeastWheel_RechargeReward_Dict:
			print "GE_EXC,repeat rewardIndex(%s) in FWRechargeReward" % cfg.rewardIndex
		if cfg.rewardIndex > 1 and cfg.rewardIndex % 2 != 0:
			print "GE_EXC,error rewardIndex(%s) mod 2 != 0" % cfg.rewardIndex
		FeastWheel_RechargeReward_Dict[cfg.rewardIndex] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadFWLotteryReward()
		LoadFWRechargeReward()