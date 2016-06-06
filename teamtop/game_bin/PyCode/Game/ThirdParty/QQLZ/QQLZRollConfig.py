#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZRollConfig")
#===============================================================================
# 蓝钻兑好礼Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQLZ")
	
	QQLZRoll_Config_Base = None		#活动控制配置
	QQLZRoll_RandomObj = None		#抽奖奖励随机器[rate, (rewardId, coding, cnt),]
	QQLZRoll_Reward_Dict = {}		#抽奖奖励配置{rewardId:cfg,}
	QQLZRoll_Exchange_Dict = {}		#兑换配置{exchangeId:cfg,}
	
class QQLZRollBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZRollBase.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString
		self.needLevel = int

class QQLZRollReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZRollReward.txt")
	def __init__(self):
		self.rewardId = int
		self.item = self.GetEvalByString
		self.rateValue = int

class QQLZRollExchange(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZRollExchange.txt")
	def __init__(self):
		self.exchangeId = int
		self.needCnt = int
		self.item = self.GetEvalByString

def LoadQQLZRollBase():
	global QQLZRoll_Config_Base
	for cfg in QQLZRollBase.ToClassType():
		if QQLZRoll_Config_Base:
			print "GE_EXC, QQLZRoll_Config_Base already have data!"
		QQLZRoll_Config_Base = cfg

def LoadQQLZRollReward():
	global QQLZRoll_RandomObj
	global QQLZRoll_Reward_Dict
	for cfg in QQLZRollReward.ToClassType():
		rewardId = cfg.rewardId
		coding, cnt = cfg.item
		rateValue = cfg.rateValue
		#基本抽奖配置
		if rewardId in QQLZRoll_Reward_Dict:
			print "GE_EXC,repeat rewardId(%s) in QQLZRoll_Reward_Dict" % rewardId
		QQLZRoll_Reward_Dict[rewardId] = cfg
		#抽奖随机器
		if not QQLZRoll_RandomObj:
			QQLZRoll_RandomObj = Random.RandomRate()
		QQLZRoll_RandomObj.AddRandomItem(rateValue, (rewardId, coding, cnt))

def LoadQQLZRollExchange():
	global QQLZRoll_Exchange_Dict
	for cfg in QQLZRollExchange.ToClassType():
		exchangeId = cfg.exchangeId
		if exchangeId in QQLZRoll_Exchange_Dict:
			print "GE_EXC,repeat exchangeId(%s) in QQLZRoll_Exchange_Dict" % exchangeId
		QQLZRoll_Exchange_Dict[exchangeId] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZRollBase()
		LoadQQLZRollReward()
		LoadQQLZRollExchange()