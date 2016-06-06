#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.StrayMerchant.StrayMerchantConfig")
#===============================================================================
# 流浪商人配置表
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	STRAY_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	STRAY_FILE_FOLDER_PATH.AppendPath("StaryMerchant")
	
	STRAY_MERCHANT_DICT = {}	#流浪商人基础配置
	RANDOM_DICT = {}	#缓存普通商品随机
	TREASURE_RANDOM_DICT = {}	#缓存珍品商品随机
	FRESH_COST_DICT = {}	#刷新配置表

class StrayMerchant(TabFile.TabLine):
	'''
	流浪商人
	'''
	FilePath = STRAY_FILE_FOLDER_PATH.FilePath("StrayMerchant.txt")
	def __init__(self):
		self.goodsId	= int
		self.goodsType	= int
		self.isTreasure = int
		self.valIndex	= int
		self.LevelVal	= self.GetEvalByString
		self.apperaPro	= int
		self.golds		= int
		self.bindRMB	= int
		self.unbindRMB	= int
		self.needCoding	= self.GetEvalByString
		self.rewards	= self.GetEvalByString

class FreshStrayCost(TabFile.TabLine):
	'''
	刷新商品消耗
	'''
	FilePath = STRAY_FILE_FOLDER_PATH.FilePath("StrayRefresh.txt")
	def __init__(self):
		self.refreshCnt	 = int
		self.reFreshUnbindRMB  = int

def LoadStrayMerchant():
	global STRAY_MERCHANT_DICT
	global RANDOM_DICT
	global TREASURE_RANDOM_DICT
	for cfg in StrayMerchant.ToClassType():
		if cfg.goodsId in STRAY_MERCHANT_DICT:
			print "GE_EXC,repeat goodsId(%s) in LoadStrayMerchant" % cfg.goodsId
		STRAY_MERCHANT_DICT[cfg.goodsId] = cfg
		
	TREASURE_RAMDOM_1 = Random.RandomRate()
	TREASURE_RAMDOM_2 = Random.RandomRate()
	TREASURE_RAMDOM_3 = Random.RandomRate()
	TREASURE_RAMDOM_4 = Random.RandomRate()
	TREASURE_RAMDOM_5 = Random.RandomRate()
	TREASURE_RAMDOM_6 = Random.RandomRate()
	TREASURE_RAMDOM_7 = Random.RandomRate()
	NEW_RANDOM_1 = Random.RandomRate()
	NEW_RANDOM_2 = Random.RandomRate()
	NEW_RANDOM_3 = Random.RandomRate()
	NEW_RANDOM_4 = Random.RandomRate()
	NEW_RANDOM_5 = Random.RandomRate()
	NEW_RANDOM_6 = Random.RandomRate()
	NEW_RANDOM_7 = Random.RandomRate()
	#需要区分商品类型和各个等级区间,将不同商品类型按不同等级区间各建一个随机对象
	for _, cfg in STRAY_MERCHANT_DICT.iteritems():
		if cfg.goodsType == 2:#商品类型是珍品
			if cfg.valIndex == 1:
				TREASURE_RAMDOM_1.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if TREASURE_RAMDOM_1 not in TREASURE_RANDOM_DICT:
					TREASURE_RANDOM_DICT[TREASURE_RAMDOM_1] = cfg.LevelVal
			elif cfg.valIndex == 2:
				TREASURE_RAMDOM_2.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if TREASURE_RAMDOM_2 not in TREASURE_RANDOM_DICT:
					TREASURE_RANDOM_DICT[TREASURE_RAMDOM_2] = cfg.LevelVal
			elif cfg.valIndex == 3:
				TREASURE_RAMDOM_3.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if TREASURE_RAMDOM_3 not in TREASURE_RANDOM_DICT:
					TREASURE_RANDOM_DICT[TREASURE_RAMDOM_3] = cfg.LevelVal
			elif cfg.valIndex == 4:
				TREASURE_RAMDOM_4.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if TREASURE_RAMDOM_4 not in TREASURE_RANDOM_DICT:
					TREASURE_RANDOM_DICT[TREASURE_RAMDOM_4] = cfg.LevelVal
			elif cfg.valIndex == 5:
				TREASURE_RAMDOM_5.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if TREASURE_RAMDOM_5 not in TREASURE_RANDOM_DICT:
					TREASURE_RANDOM_DICT[TREASURE_RAMDOM_5] = cfg.LevelVal
			elif cfg.valIndex == 6:
				TREASURE_RAMDOM_6.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if TREASURE_RAMDOM_6 not in TREASURE_RANDOM_DICT:
					TREASURE_RANDOM_DICT[TREASURE_RAMDOM_6] = cfg.LevelVal
			elif cfg.valIndex == 7:
				TREASURE_RAMDOM_7.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if TREASURE_RAMDOM_7 not in TREASURE_RANDOM_DICT:
					TREASURE_RANDOM_DICT[TREASURE_RAMDOM_7] = cfg.LevelVal
		elif cfg.goodsType == 1:#普通
			if cfg.valIndex == 1:
				NEW_RANDOM_1.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if NEW_RANDOM_1 not in RANDOM_DICT:
					RANDOM_DICT[NEW_RANDOM_1] = cfg.LevelVal
			elif cfg.valIndex == 2:
				NEW_RANDOM_2.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if NEW_RANDOM_2 not in RANDOM_DICT:
					RANDOM_DICT[NEW_RANDOM_2] = cfg.LevelVal
			elif cfg.valIndex == 3:
				NEW_RANDOM_3.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if NEW_RANDOM_3 not in RANDOM_DICT:
					RANDOM_DICT[NEW_RANDOM_3] = cfg.LevelVal
			elif cfg.valIndex == 4:
				NEW_RANDOM_4.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if NEW_RANDOM_4 not in RANDOM_DICT:
					RANDOM_DICT[NEW_RANDOM_4] = cfg.LevelVal
			elif cfg.valIndex == 5:
				NEW_RANDOM_5.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if NEW_RANDOM_5 not in RANDOM_DICT:
					RANDOM_DICT[NEW_RANDOM_5] = cfg.LevelVal
			elif cfg.valIndex == 6:
				NEW_RANDOM_6.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if NEW_RANDOM_6 not in RANDOM_DICT:
					RANDOM_DICT[NEW_RANDOM_6] = cfg.LevelVal
			elif cfg.valIndex == 7:
				NEW_RANDOM_7.AddRandomItem(cfg.apperaPro, cfg.goodsId)
				if NEW_RANDOM_7 not in RANDOM_DICT:
					RANDOM_DICT[NEW_RANDOM_7] = cfg.LevelVal
		else:
			pass

def LoadFreshStrayCost():
	global FRESH_COST_DICT
	for cfg in FreshStrayCost.ToClassType():
		if cfg.refreshCnt in FRESH_COST_DICT:
			print "GE_EXC,repeat refreshCnt(%s) in LoadFreshStrayCost" % cfg.refreshCnt
		FRESH_COST_DICT[cfg.refreshCnt] = cfg

def GetRandomByLevel(role, goodsType1_cnt, goodsType2_cnt):
	#根据玩家和需要的随机个数，获取刷新的商品
	global RANDOM_DICT
	global TREASURE_RANDOM_DICT
	
	level = role.GetLevel()
	ranobj = None
	treasure_ranobj = None
	for randomObj, levelList in RANDOM_DICT.iteritems():
		if levelList[0] <= level <= levelList[1]:
			ranobj = randomObj
			break
	for randomObj2, levelList2 in TREASURE_RANDOM_DICT.iteritems():
		if levelList2[0] <= level <= levelList2[1]:
			treasure_ranobj = randomObj2
			break
	if not ranobj or not treasure_ranobj:
		print "GE_EXC, ranobj is None in StrayMerchantConfig.GetRandomByLevel roleLevel(%s)" % level
		return
	goods_list = []
	goods_list += ranobj.RandomMany(goodsType1_cnt)
	goods_list += treasure_ranobj.RandomMany(goodsType2_cnt)

	return goods_list

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadStrayMerchant()
		LoadFreshStrayCost()
	