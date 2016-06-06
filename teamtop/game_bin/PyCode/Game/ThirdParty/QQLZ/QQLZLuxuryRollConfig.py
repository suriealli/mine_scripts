#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZLuxuryRollConfig")
#===============================================================================
# 豪华蓝钻转大礼Config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQLZ")
	
	QQLZLuxuryRoll_Config_Base = None	#活动控制配置
	QQLZLuxuryRoll_RandomObj = None		#抽奖奖励随机器[rate, (rewardId, coding, cnt),]
	QQLZLuxuryRoll_Reward_Dict = {}		#抽奖奖励配置{rewardId:cfg,}
	QQLZLuxuryRoll_Exchange_Dict = {}	#兑换配置{exchangeId:cfg,}
	
class QQLZLuxuryRollBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZLuxuryRollBase.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString
		self.needLevel = int

class QQLZLuxuryRollReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZLuxuryRollReward.txt")
	def __init__(self):
		self.rewardId = int
		self.item = self.GetEvalByString
		self.rateValue = int

class QQLZLuxuryRollExchange(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZLuxuryRollExchange.txt")
	def __init__(self):
		self.exchangeId = int
		self.needCnt = int
		self.item = self.GetEvalByString

def LoadQQLZLuxuryRollBase():
	global QQLZLuxuryRoll_Config_Base
	for cfg in QQLZLuxuryRollBase.ToClassType():
		if QQLZLuxuryRoll_Config_Base:
			print "GE_EXC, QQLZLuxuryRoll_Config_Base already have data!"
		QQLZLuxuryRoll_Config_Base = cfg

def LoadQQLZLuxuryRollReward():
	global QQLZLuxuryRoll_RandomObj
	global QQLZLuxuryRoll_Reward_Dict
	for cfg in QQLZLuxuryRollReward.ToClassType():
		rewardId = cfg.rewardId
		coding, cnt = cfg.item
		rateValue = cfg.rateValue
		#基本抽奖配置
		if rewardId in QQLZLuxuryRoll_Reward_Dict:
			print "GE_EXC,repeat rewardId(%s) in QQLZLuxuryRoll_Reward_Dict" % rewardId
		QQLZLuxuryRoll_Reward_Dict[rewardId] = cfg
		#抽奖随机器
		if not QQLZLuxuryRoll_RandomObj:
			QQLZLuxuryRoll_RandomObj = Random.RandomRate()
		QQLZLuxuryRoll_RandomObj.AddRandomItem(rateValue, (rewardId, coding, cnt))

def LoadQQLZLuxuryRollExchange():
	global QQLZLuxuryRoll_Exchange_Dict
	for cfg in QQLZLuxuryRollExchange.ToClassType():
		exchangeId = cfg.exchangeId
		if exchangeId in QQLZLuxuryRoll_Exchange_Dict:
			print "GE_EXC,repeat exchangeId(%s) in QQLZLuxuryRoll_Exchange_Dict" % exchangeId
		QQLZLuxuryRoll_Exchange_Dict[exchangeId] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZLuxuryRollBase()
		LoadQQLZLuxuryRollReward()
		LoadQQLZLuxuryRollExchange()