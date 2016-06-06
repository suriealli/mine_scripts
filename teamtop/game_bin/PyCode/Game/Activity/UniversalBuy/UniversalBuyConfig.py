#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.UniversalBuy.UniversalBuyConfig")
#===============================================================================
# 全民团购配置表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	UNIVERBUY_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	UNIVERBUY_FILE_FOLDER_PATH.AppendPath("UniversalBuy")
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("CircularActive")
	
	UNIVER_BUY_BASE = None	#基础配置表
	UNIVER_KEY_LIST = set()	#缓存商品INDEX
	UNIVER_REWARD_DICT = {}	#奖励配置表

class UniversalBuy(TabFile.TabLine):
	'''
	全民团购基础配置
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("UniversalBuy.txt")
	def __init__(self):
		self.StartTime	= self.GetDatetimeByString
		self.EndTime	= self.GetDatetimeByString

class UniversalReward(TabFile.TabLine):
	'''
	全民团购奖励
	'''
	FilePath = UNIVERBUY_FILE_FOLDER_PATH.FilePath("UniversalReward.txt")
	def __init__(self):
		self.Index		= int
		self.awardEnum	= int
		self.times		= int
		self.ItemId		= int
		self.BuyCnt		= int
		self.discountRMB= int

		self.needCnt1	= int
		self.libao1		= self.GetEvalByString
		
		self.needCnt2	= int
		self.libao2		= self.GetEvalByString

		self.needCnt3	= int
		self.libao3		= self.GetEvalByString
		
		self.needCnt4	= int
		self.libao4		= self.GetEvalByString
		
		self.needCnt5	= int
		self.libao5		= self.GetEvalByString
		
		self.needCnt6	= int
		self.libao6		= self.GetEvalByString
		
		self.needCnt7	= int
		self.libao7		= self.GetEvalByString

def LoadUniverBase():
	global UNIVER_BUY_BASE
	for cfg in UniversalBuy.ToClassType():
		UNIVER_BUY_BASE = cfg

def LoadUniverReward():
	global UNIVER_REWARD_DICT
	global UNIVER_KEY_LIST
	for cfg in UniversalReward.ToClassType():
		if cfg.Index in UNIVER_REWARD_DICT:
			print "GE_EXC,repeat index(%s) in LoadUniverReward" % cfg.Index
		UNIVER_KEY_LIST.add(cfg.Index)
		UNIVER_REWARD_DICT[cfg.Index] = cfg


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadUniverBase()
		LoadUniverReward()
