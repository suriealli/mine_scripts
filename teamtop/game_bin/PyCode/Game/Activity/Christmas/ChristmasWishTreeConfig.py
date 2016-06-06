#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasWishTreeConfig")
#===============================================================================
# 圣诞许愿树config
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile
from Common.Other import EnumGameConfig

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Christmas")
	
	MAX_REFRESHCNT = 0	#配置最大刷新次数
	ChristmasWishTree_RefreshConfig_Dict = {}	#手动刷新圣诞许愿树商品消耗神石{rehfreshCnt:needUnbindRMB,}
	
	ChristmasWishTree_GoodsConfig_Dict = {}		#圣诞许愿树商品池{rangeId:{goodId:goodCfg,},}
	ChristmasWishTree_GoodsRange2Id_Dict = {}	#圣诞许愿树商品等级区段和区段ID关联{rangeId:levelRange}
	ChristmasWishTree_GoodsRandomObj_Dict = {}	#圣诞许愿树商品随机器{rangeId:randomObj,} randomList->[rate,(goodId, coding, cnt, itemCnt, needUnbindRMB, RMBType, needSockCnt]
	
class ChristmasWishTreeRefresh(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ChristmasWishTreeRefresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.needSockCnt = int

def LoadChristmasWishTreeRefresh():
	global MAX_REFRESHCNT
	global ChristmasWishTree_RefreshConfig_Dict
	for cfg in ChristmasWishTreeRefresh.ToClassType():
		refreshCnt = cfg.refreshCnt
		needSockCnt = cfg.needSockCnt
		#缓存配置最大刷新次数
		if refreshCnt > MAX_REFRESHCNT:
			MAX_REFRESHCNT = refreshCnt
		
		if refreshCnt in ChristmasWishTree_RefreshConfig_Dict:
			print "GE_EXC, repeat refreshCnt(%s) in ChristmasWishTree_RefreshConfig_Dict " % refreshCnt
		ChristmasWishTree_RefreshConfig_Dict[refreshCnt] = needSockCnt


class ChristmasWishTreeGoods(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ChristmasWishTreeGoods.txt")
	def __init__(self):
		self.goodId = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.item = self.GetEvalByString
		self.itemCnt = int
		self.rateValue = int
		self.needUnbindRMB = int
		self.RMBType = int
		self.needSockCnt = int

def LoadChristmasWishTreeGoods():
	global ChristmasWishTree_GoodsConfig_Dict
	global ChristmasWishTree_GoodsRange2Id_Dict
	global ChristmasWishTree_GoodsRandomObj_Dict
	for cfg in ChristmasWishTreeGoods.ToClassType():
		goodId = cfg.goodId
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		coding, cnt = cfg.item
		itemCnt = cfg.itemCnt
		rateValue = cfg.rateValue
		needUnbindRMB = cfg.needUnbindRMB
		RMBType = cfg.RMBType
		needSockCnt = cfg.needSockCnt
		
		#商品池
		goodsCfgDict = ChristmasWishTree_GoodsConfig_Dict.setdefault(rangeId, {})
		if goodId in goodsCfgDict:
			print "GE_EXC,repeat goodId(%s) in ChristmasWishTree_GoodsConfig_Dict" % goodId
		goodsCfgDict[goodId] = cfg
		#等级区段关联区段ID
		ChristmasWishTree_GoodsRange2Id_Dict[rangeId] = levelRange
		#商品随机器
		if rangeId not in ChristmasWishTree_GoodsRandomObj_Dict:
			ChristmasWishTree_GoodsRandomObj_Dict[rangeId] = Random.RandomRate()
		
		randomObj = ChristmasWishTree_GoodsRandomObj_Dict[rangeId]
		randomObj.AddRandomItem(rateValue, (goodId, coding, cnt, itemCnt, needUnbindRMB, RMBType, needSockCnt))

def GetRandomGoodsByLevel(roleLevel):
	'''
	根据玩家等级 获取随机的货架商品列表
	'''
	tmpRangeId = 1
	for rangeId, levelRange in ChristmasWishTree_GoodsRange2Id_Dict.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel and roleLevel <= levelUp:
			break
	
	randomObj = ChristmasWishTree_GoodsRandomObj_Dict.get(tmpRangeId)
	if not randomObj:
		print "GE_EXC, can not get randomObj by roleLevel(%s) to rangeId(%s)" % (roleLevel, tmpRangeId)
		return None
	
	return randomObj.RandomMany(EnumGameConfig.ChristmasWishTree_ShelfGoodsCnt)

def GetGoodCfgByID(goodId):
	'''
	返回goodId对应配置项
	'''
	tmpGoodCfg = None
	for _, goodCfgDict in ChristmasWishTree_GoodsConfig_Dict.iteritems():
		if goodId in goodCfgDict:
			tmpGoodCfg = goodCfgDict[goodId]
			break
	
	return tmpGoodCfg

def GetSockCntByRefreshCnt(refreshCnt):
	'''
	根据此次请求刷新的刷新次数 获得刷新所需要的神石消耗
	'''
	if refreshCnt not in ChristmasWishTree_RefreshConfig_Dict:
		return ChristmasWishTree_RefreshConfig_Dict[MAX_REFRESHCNT]
	else:
		return ChristmasWishTree_RefreshConfig_Dict[refreshCnt]
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadChristmasWishTreeRefresh()
		LoadChristmasWishTreeGoods()