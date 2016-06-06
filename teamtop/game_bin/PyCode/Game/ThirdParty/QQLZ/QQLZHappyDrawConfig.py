#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZHappyDrawConfig")
#===============================================================================
# 蓝钻转转乐配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random
from Game.Role.Data import EnumObj

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQLZ")
	
	QQLZ_HAPPYDRAW_BASE = None
	QQLZ_HAPPYDRAW_REWARD = {}
	QQLZ_HAPPYDRAW_EXCHANGE = {}
	
class QQLZHappyDrawBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZHappyDrawBase.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString
		
def LoadQQLZHappyDrawBase():
	global QQLZ_HAPPYDRAW_BASE

	for cfg in QQLZHappyDrawBase.ToClassType():
		if QQLZ_HAPPYDRAW_BASE:
			print "GE_EXC, LoadQQLZHappyDrawBase already have data!"
		QQLZ_HAPPYDRAW_BASE = cfg
		
class QQLZHappyDraw(TabFile.TabLine):
	'''
	奖励配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("QQLZHappyDraw.txt")
	def __init__(self):
		self.rewardId = int
		self.item = self.GetEvalByString
		self.rateValue = int
		
def LoadQQLZHappyDraw():
	global QQLZ_HAPPYDRAW_REWARD
	
	for cfg in QQLZHappyDraw.ToClassType():
		if cfg.rewardId in QQLZ_HAPPYDRAW_REWARD:
			print "GE_EXC,repeat rewardId(%s) in LoadQQLZHappyDraw" % cfg.rewardId
		QQLZ_HAPPYDRAW_REWARD[cfg.rewardId] = cfg
		
class QQLZHappyDrawExchange(TabFile.TabLine):
	'''
	兑换奖励
	'''
	FilePath = FILE_FLODER_PATH.FilePath("QQLZHappyDrawExchange.txt")
	def __init__(self):
		self.exchangeId = int
		self.needCnt = int
		self.item = self.GetEvalByString
		
def LoadQQLZHappyDrawExchange():
	global QQLZ_HAPPYDRAW_EXCHANGE
	
	for cfg in QQLZHappyDrawExchange.ToClassType():
		if cfg.exchangeId in QQLZ_HAPPYDRAW_EXCHANGE:
			print "GE_EXC,repeat exchangeId(%s) in LoadQQLZHappyDrawExchange" % cfg.exchangeId
		QQLZ_HAPPYDRAW_EXCHANGE[cfg.exchangeId] = cfg
		
def GetRandomOne(role):
	'''
	除去已获取的奖励，从剩余中随机出一个奖励
	概率
	@param role:
	'''
	global QQLZ_HAPPYDRAW_REWARD
	#获取玩家已获得列表
	if role.GetObj(EnumObj.QQLZHDData) == {}:
		role.SetObj(EnumObj.QQLZHDData, set())
	getedData = role.GetObj(EnumObj.QQLZHDData)
	if len(getedData) >= 12:
		#一轮奖励全领完，制空进入下一轮
		role.SetObj(EnumObj.QQLZHDData, set())
		getedData = set()
	NEW_RANDOM = Random.RandomRate()
	for rewardId, cfg in QQLZ_HAPPYDRAW_REWARD.iteritems():
		if rewardId not in getedData:
			NEW_RANDOM.AddRandomItem(cfg.rateValue, (cfg.rewardId, cfg.item))
	return NEW_RANDOM.RandomOne()

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZHappyDrawBase()
		LoadQQLZHappyDraw()
		LoadQQLZHappyDrawExchange()