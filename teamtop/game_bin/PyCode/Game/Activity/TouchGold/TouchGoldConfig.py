#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TouchGold.TouchGoldConfig")
#===============================================================================
# 点石成金配置
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	T_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	T_FILE_FOLDER_PATH.AppendPath("TouchGold")
	
	TOUCH_GOLD_DICT = {}	#点石成金基础配置
	GET_STONE_DICT = {}		#获取原石配置
	BUY_TIMES_COST = {}		#购买次数消耗
	MAX_BUY_TIMES = 0		#已配的最大购买次数
	POINT_EXCHANGE_DICT = {}#积分兑换配置

class TouchGold(TabFile.TabLine):
	FilePath = T_FILE_FOLDER_PATH.FilePath("TouchGold.txt")
	def __init__(self):
		self.stone = int
		self.rewardpoint = int
		self.rewarditem = self.GetEvalByString
		self.randomcnt = self.GetEvalByString
		self.randomitem = self.GetEvalByString
		self.backPoint = int

	def InitRandom(self):
		self.RANDOM_CNT = Random.RandomRate()
		for cnt, rate in self.randomcnt.iteritems():
			self.RANDOM_CNT.AddRandomItem(rate, cnt)
			
		self.RANDOM_ITEM = Random.RandomRate()
		for reward, rate in self.randomitem.iteritems():
			self.RANDOM_ITEM.AddRandomItem(rate, reward)
			
def LoadTouchGold():
	global TOUCH_GOLD_DICT
	
	for cfg in TouchGold.ToClassType():
		if cfg.stone in TOUCH_GOLD_DICT:
			print "GE_EXC,repeat stone(%s) in LoadTouchGold.TOUCH_GOLD_DICT" % cfg.stone
		cfg.InitRandom()
		TOUCH_GOLD_DICT[cfg.stone] = cfg
		
class GetStone(TabFile.TabLine):
	FilePath = T_FILE_FOLDER_PATH.FilePath("GetStone.txt")
	def __init__(self):
		self.gettype = int
		self.costUnbind_Q = int
		self.cd = int
		self.randomcnt = int
		self.stonepro = self.GetEvalByString
		self.limitCnt = int
	
	def RandomItem(self):
		self.RANDOM_STONE = Random.RandomRate()
		for stonetype, rate in self.stonepro.iteritems():
			self.RANDOM_STONE.AddRandomItem(rate, stonetype)
			
def LoadGetStone():
	global GET_STONE_DICT
	
	for cfg in GetStone.ToClassType():
		if cfg.gettype in GET_STONE_DICT:
			print "GE_EXC, repeat gettype(%s) in LoadTouchGold.LoadGetStone" % cfg.gettype
		cfg.RandomItem()
		GET_STONE_DICT[cfg.gettype] = cfg
		
class BuyStoneTimes(TabFile.TabLine):
	FilePath = T_FILE_FOLDER_PATH.FilePath("BuyStoneTimes.txt")
	def __init__(self):
		self.buytimes = int
		self.needUnbindRMB_Q = int
		
def LoadBuyStoneTimes():
	global BUY_TIMES_COST
	global MAX_BUY_TIMES
	for cfg in BuyStoneTimes.ToClassType():
		if cfg.buytimes in BUY_TIMES_COST:
			print "GE_EXC, repeat buytimes(%s) in LoadTouchGold.LoadBuyStoneTimes" % cfg.buytimes
		BUY_TIMES_COST[cfg.buytimes] = cfg.needUnbindRMB_Q
		if cfg.buytimes > MAX_BUY_TIMES:
			MAX_BUY_TIMES = cfg.buytimes
			
class PointExchange(TabFile.TabLine):
	FilePath = T_FILE_FOLDER_PATH.FilePath("PointExchange.txt")
	def __init__(self):
		self.goodsId = int
		self.needPoint = int
		self.items = self.GetEvalByString
		
def LoadPointExchange():
	global POINT_EXCHANGE_DICT
	
	for cfg in PointExchange.ToClassType():
		if cfg.goodsId in POINT_EXCHANGE_DICT:
			print "GE_EXC,repeat goodsId(%S) in LoadTouchGold.LoadPointExchange" % cfg.goodsId
		POINT_EXCHANGE_DICT[cfg.goodsId] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTouchGold()
		LoadGetStone()
		LoadBuyStoneTimes()
		LoadPointExchange()