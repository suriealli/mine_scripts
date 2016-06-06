#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZOfferGiftConfig")
#===============================================================================
# 蓝钻献大礼配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():	
	QQHZ_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	QQHZ_FILE_FOLDER_PATH.AppendPath("QQLZ")
	
	QQLZ_GIFT_OFFER_GIFT_DICT	= {}	#QQ蓝钻献大礼礼包配置{LiBaoID：cfg}

class QQLZGiftOGLiBao(TabFile.TabLine):
	'''
	蓝钻献大礼奖励
	'''
	FilePath = QQHZ_FILE_FOLDER_PATH.FilePath("QQLZGiftOGLiBao.txt")
	def __init__(self):
		self.LiBaoID = int 							#礼包ID
		self.randomItems = self.GetEvalByString		#随机物品集
		self.nomalItems = self.GetEvalByString		#必出物品集
	
	def pre_process(self):
		self.randomObj = Random.RandomRate()
		for item, rate in self.randomItems:
			self.randomObj.AddRandomItem(rate, item)

def GetRandomOG():
	'''
	获取献大礼随机奖励的一个奖励物品
	@return: coding 物品编码 
	@return: cnt	物品数量
	'''
	cfg = QQLZ_GIFT_OFFER_GIFT_DICT.get(1)
	if not cfg:
		print "GE_EXC, QQLZ_GIFT_OFFER_GIFT_DICT.get(1) is None"
		return None
	
	return cfg.randomObj.RandomOne()

def LoadQQLZOfferGiftReward():
	global QQLZ_GIFT_OFFER_GIFT_DICT
	for cfg in QQLZGiftOGLiBao.ToClassType():
		if 1 != cfg.LiBaoID:
			print "GE_EXC, LoadQQLZOfferGiftReward::cfg.LiBaoID(%s) != 1" % cfg.LiBaoID
		if cfg.LiBaoID in QQLZ_GIFT_OFFER_GIFT_DICT:
			print "GE_EXC, repeat LiBaoID(%s) in LoadQQLZOfferGiftReward!" % cfg.LiBaoID
		QQLZ_GIFT_OFFER_GIFT_DICT[cfg.LiBaoID] = cfg
		cfg.pre_process()
	
	if 1 not in QQLZ_GIFT_OFFER_GIFT_DICT:
		print "GE_EXC, 1 not in QQHZ_GIFT_OFFER_GIFT_DICT"
	
if '_HasLoad' not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZOfferGiftReward()