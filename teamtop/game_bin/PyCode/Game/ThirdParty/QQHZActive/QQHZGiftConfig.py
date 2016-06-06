#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHZActive.QQHZGiftConfig")
#===============================================================================
# 黄钻大礼配置 akm
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QQHZGift")
	
	QQHZRG_RANDOMER = Random.RandomRate() 				#黄钻转大礼奖励随机器
	QQHZ_GIFT_ACTIVE_CONFIG_DICT 	= {}				#QQ黄钻大礼活动控制配置{activeID：cfg}
	QQHZ_GIFT_ROLL_GIFT_DICT		= {}				#QQ黄钻转大礼礼包配置{LiBaoID：cfg}
	QQHZ_GIFT_OFFER_GIFT_DICT		= {}				#QQ黄钻献大礼礼包配置{LiBaoID：cfg}
	

class QQHZGiftConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('QQHZGiftConfig.txt')
	def __init__(self):
		self.activeID = int							#活动ID
		self.activeType = int						#活动类型	
		self.beginDate = self.GetEvalByString		#开始时间
		self.endDate = self.GetEvalByString			#结束时间
		self.needLevel = int						#等级限制
		
class QQHZGiftRGLiBao(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QQHZGiftRGLiBao.txt")
	def __init__(self):
		self.LiBaoID 	= int 						#礼包ID 符合（1,2,4,8...模式）
		self.rate		= int						#随机概率
		self.itemCoding = self.GetEvalByString		#coding

class QQHZGiftOGLiBao(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QQHZGiftOGLiBao.txt")
	def __init__(self):
		self.LiBaoID = int 							#礼包ID
		self.randomItems = self.GetEvalByString		#随机物品集
		self.nomalItems = self.GetEvalByString		#必出物品集
	
	def pre_process(self):
		self.randomObj = Random.RandomRate()
		for item, rate in self.randomItems:
			self.randomObj.AddRandomItem(rate, item)

def LoadQQHZGiftConfig():
	global QQHZ_GIFT_ACTIVE_CONFIG_DICT
	for cfg in QQHZGiftConfig.ToClassType():
		if cfg.activeID in QQHZ_GIFT_ACTIVE_CONFIG_DICT:
			print "GE_EXC:repeat activeID(%s) in LoadQQHZGiftConfig!" % cfg.activeID
		QQHZ_GIFT_ACTIVE_CONFIG_DICT[cfg.activeID] = cfg
		
def LaodQQHZGiftRollGift():
	global QQHZ_GIFT_ROLL_GIFT_DICT
	for cfg in QQHZGiftRGLiBao.ToClassType():
		if cfg.LiBaoID in QQHZ_GIFT_ROLL_GIFT_DICT:
			print "GE_EXC,repeat LiBaoID(%d) in LaodQQHZGiftRollGift!" % cfg.LiBaoID
		QQHZ_GIFT_ROLL_GIFT_DICT[cfg.LiBaoID] = cfg
		QQHZRG_RANDOMER.AddRandomItem(cfg.rate, cfg.LiBaoID)

def LoadQQHZGiftOGLiBao():
	global QQHZ_GIFT_OFFER_GIFT_DICT
	for cfg in QQHZGiftOGLiBao.ToClassType():
		if 1 != cfg.LiBaoID:
			print "GE_EXC, QQHZ_GIFT_OFFER_GIFT_DICT::1 != cfg.LiBaoID(%s)" % cfg.LiBaoID
		if cfg.LiBaoID in QQHZ_GIFT_OFFER_GIFT_DICT:
			print "GE_EXC, repeat LiBaoID(%s) in LoadQQHZGiftOGLiBao!" % cfg.LiBaoID
		QQHZ_GIFT_OFFER_GIFT_DICT[cfg.LiBaoID] = cfg
		cfg.pre_process()
	
	if 1 not in QQHZ_GIFT_OFFER_GIFT_DICT:
		print "GE_EXC, 1 not in QQHZ_GIFT_OFFER_GIFT_DICT"

def GetRandomRG():
	'''
	根据玩家的记录 随机一个未开启的礼包
	'''
	NEW_RANDOM = Random.RandomRate()
	for _, cfg in QQHZ_GIFT_ROLL_GIFT_DICT.iteritems():
		NEW_RANDOM.AddRandomItem(cfg.rate, cfg.LiBaoID)
	return NEW_RANDOM.RandomOne()

def GetRandomOG():
	'''
	获取献大礼随机奖励的一个奖励物品
	@return: coding 物品编码 
	@return: cnt	物品数量
	'''
	cfg = QQHZ_GIFT_OFFER_GIFT_DICT.get(1)
	if not cfg:
		print "GE_EXC, QQLZ_GIFT_OFFER_GIFT_DICT.get(1) is None"
		return None
	
	return cfg.randomObj.RandomOne()

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQHZGiftConfig()
		LaodQQHZGiftRollGift()
		LoadQQHZGiftOGLiBao()
