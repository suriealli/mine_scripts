#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHZActive.QQHZRollConfig")
#===============================================================================
# 黄钻兑好礼Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQHZ")
	
	QQHZRoll_Config_Base = None		#活动控制配置
	QQHZRoll_RandomObj = None		#抽奖奖励随机器[rate, (rewardId, coding, cnt),]
	QQHZRoll_Reward_Dict = {}		#抽奖奖励配置{rewardId:cfg,}
	QQHZRoll_Exchange_Dict = {}		#兑换配置{exchangeId:cfg,}
	
class QQHZRollBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQHZRollBase.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString
		self.needLevel = int

class QQHZRollReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQHZRollReward.txt")
	def __init__(self):
		self.rewardId = int
		self.item = self.GetEvalByString
		self.rateValue = int

class QQHZRollExchange(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQHZRollExchange.txt")
	def __init__(self):
		self.exchangeId = int
		self.needCnt = int
		self.item = self.GetEvalByString

def LoadQQHZRollBase():
	global QQHZRoll_Config_Base
	for cfg in QQHZRollBase.ToClassType():
		if QQHZRoll_Config_Base:
			print "GE_EXC, QQHZRoll_Config_Base already have data!"
		QQHZRoll_Config_Base = cfg

def LoadQQHZRollReward():
	global QQHZRoll_RandomObj
	global QQHZRoll_Reward_Dict
	for cfg in QQHZRollReward.ToClassType():
		rewardId = cfg.rewardId
		coding, cnt = cfg.item
		rateValue = cfg.rateValue
		#基本抽奖配置
		if rewardId in QQHZRoll_Reward_Dict:
			print "GE_EXC,repeat rewardId(%s) in QQHZRoll_Reward_Dict" % rewardId
		QQHZRoll_Reward_Dict[rewardId] = cfg
		#抽奖随机器
		if not QQHZRoll_RandomObj:
			QQHZRoll_RandomObj = Random.RandomRate()
		QQHZRoll_RandomObj.AddRandomItem(rateValue, (rewardId, coding, cnt))

def LoadQQHZRollExchange():
	global QQHZRoll_Exchange_Dict
	for cfg in QQHZRollExchange.ToClassType():
		exchangeId = cfg.exchangeId
		if exchangeId in QQHZRoll_Exchange_Dict:
			print "GE_EXC,repeat exchangeId(%s) in QQHZRoll_Exchange_Dict" % exchangeId
		QQHZRoll_Exchange_Dict[exchangeId] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQHZRollBase()
		LoadQQHZRollReward()
		LoadQQHZRollExchange()