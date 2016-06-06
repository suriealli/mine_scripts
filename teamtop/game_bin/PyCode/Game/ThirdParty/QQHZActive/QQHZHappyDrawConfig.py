#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHZActive.QQHZHappyDrawConfig")
#===============================================================================
# 黄钻转转乐
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random
from Game.Role.Data import EnumObj

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQHZ")
	
	QQHZ_HAPPYDRAW_BASE = None
	QQHZ_HAPPYDRAW_REWARD = {}
	QQHZ_HAPPYDRAW_EXCHANGE = {}
	
class QQHZHappyDrawBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQHZHappyDrawBase.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString
		
def LoadQQHZHappyDrawBase():
	global QQHZ_HAPPYDRAW_BASE

	for cfg in QQHZHappyDrawBase.ToClassType():
		if QQHZ_HAPPYDRAW_BASE:
			print "GE_EXC, LoadQQHZHappyDrawBase already have data!"
		QQHZ_HAPPYDRAW_BASE = cfg
		
class QQHZHappyDraw(TabFile.TabLine):
	'''
	奖励配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("QQHZHappyDraw.txt")
	def __init__(self):
		self.rewardId = int
		self.item = self.GetEvalByString
		self.rateValue = int
		
def LoadQQHZHappyDraw():
	global QQHZ_HAPPYDRAW_REWARD
	
	for cfg in QQHZHappyDraw.ToClassType():
		if cfg.rewardId in QQHZ_HAPPYDRAW_REWARD:
			print "GE_EXC,repeat rewardId(%s) in LoadQQHZHappyDraw" % cfg.rewardId
		QQHZ_HAPPYDRAW_REWARD[cfg.rewardId] = cfg
		
class QQHZHappyDrawExchange(TabFile.TabLine):
	'''
	兑换奖励
	'''
	FilePath = FILE_FLODER_PATH.FilePath("QQHZHappyDrawExchange.txt")
	def __init__(self):
		self.exchangeId = int
		self.needCnt = int
		self.item = self.GetEvalByString
		
def LoadQQHZHappyDrawExchange():
	global QQHZ_HAPPYDRAW_EXCHANGE
	
	for cfg in QQHZHappyDrawExchange.ToClassType():
		if cfg.exchangeId in QQHZ_HAPPYDRAW_EXCHANGE:
			print "GE_EXC,repeat exchangeId(%s) in LoadQQHZHappyDrawExchange" % cfg.exchangeId
		QQHZ_HAPPYDRAW_EXCHANGE[cfg.exchangeId] = cfg
		
def GetRandomOne(role):
	'''
	除去已获取的奖励，从剩余中随机出一个奖励
	概率
	@param role:
	'''
	global QQHZ_HAPPYDRAW_REWARD
	#获取玩家已获得列表
	if role.GetObj(EnumObj.QQHZHDData) == {}:
		role.SetObj(EnumObj.QQHZHDData, set())
	getedData = role.GetObj(EnumObj.QQHZHDData)
	if len(getedData) >= 12:
		#一轮奖励全领完，制空进入下一轮
		role.SetObj(EnumObj.QQHZHDData, set())
		getedData = set()
	NEW_RANDOM = Random.RandomRate()
	for rewardId, cfg in QQHZ_HAPPYDRAW_REWARD.iteritems():
		if rewardId not in getedData:
			NEW_RANDOM.AddRandomItem(cfg.rateValue, (cfg.rewardId, cfg.item))
	return NEW_RANDOM.RandomOne()

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQHZHappyDrawBase()
		LoadQQHZHappyDraw()
		LoadQQHZHappyDrawExchange()