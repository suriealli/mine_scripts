#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SuperPromption.SuperPromptionConfig")
#===============================================================================
# 超值特惠 config
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment


OneDaySecs = 24 * 60 * 60

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("SuperPromption")
	
	SuperPromption_GoodsConfig_Dict = {}	#超值特惠商品配置 {goodsType:{serverType:cfg,},}
	SuperPromption_BaseConfig_Dict = {}		
	
class SuperPromptionGoods(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("SuperPromptionGoods.txt")
	def __init__(self):
		self.goodsId = int
		self.goodsType = int
		self.serverType = int
		self.kaifuDayRange = self.GetEvalByString
		self.limitCnt = int
		self.needLevel = int
		self.dayBuyRMBLimit = int
		self.needUnbindRMB = int
		self.realItems = self.GetEvalByString
		self.rewardMoney = int
		self.rewardRMB = int
		self.goodsName = str

def LoadSuperPromptionGoods():
	global SuperPromption_GoodsConfig_Dict
	for cfg in SuperPromptionGoods.ToClassType():
		goodsId = cfg.goodsId
		goodsType = cfg.goodsType
		serverType = cfg.serverType
		goodsTypeDict = SuperPromption_GoodsConfig_Dict.setdefault(goodsType, {})
		if serverType in goodsTypeDict:
			print "GE_EXC,repeat serverType(%s) in goodsType(%s)" % (serverType, goodsType)
		goodsTypeDict[serverType] = cfg
		if goodsId in SuperPromption_BaseConfig_Dict:
			print "GE_EX,repeat goodsId(%s) in SuperPromption_BaseConfig_Dict" % goodsId
		SuperPromption_BaseConfig_Dict[goodsId] = cfg

def GetCfgByTypeAndKaiFuDay(goodsType, kaifuDays):
	'''
	返回 对应商品类型goodsType 对应开服天数kaifuDays所属区段的商品配置
	'''
	retCfg = None
	goodsTypeDict =SuperPromption_GoodsConfig_Dict.get(goodsType, {})
	for _, cfg in goodsTypeDict.iteritems():
		dayDown, dayUp = cfg.kaifuDayRange
		if dayDown <= kaifuDays <= dayUp:
			retCfg = cfg
			break
		
	return retCfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadSuperPromptionGoods()