#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.DEQiangHongBaoConfig")
#===============================================================================
# 双十一2015 抢红包 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

TYPE_NO = 0
TYPE_QHB = 1
TYPE_QG = 2


if "_HasLod" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DoubleEleven")
	
	#抢红包商品配置{goodsId:cfg,}
	DEQiangHongBao_GoodsConfig_Dict = {}
	#抢红包控制配置 {roundIndex:cfg,}
	DEQiangHongBao_RoundControl_Dict = {}
	#红包优惠卷配置 {itemCoding:cfg,}
	DEQiangHongBao_CouponsConfig_Dict = {}
	

class DEQiangHongBaoGoods(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DEQiangHongBaoGoods.txt")
	def __init__(self):
		self.goodsId = int
		self.goodsItem = self.GetEvalByString
		self.needUnbindRMB = int
		
		
def LoadDEQiangHongBaoGoods():
	global DEQiangHongBao_GoodsConfig_Dict
	for cfg in DEQiangHongBaoGoods.ToClassType():
		goodsId = cfg.goodsId
		if goodsId in DEQiangHongBao_GoodsConfig_Dict:
			print "GE_EXC,repeat goodsId(%s) in DEQiangHongBao_GoodsConfig_Dict" % goodsId
		DEQiangHongBao_GoodsConfig_Dict[goodsId] = cfg


class DEQiangHongBaoControl(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DEQiangHongBaoControl.txt")
	def __init__(self):
		self.roundIndex = int
		self.roundType = int
		self.beginTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.goodsPool = self.GetEvalByString
		self.hongBaoPool = self.GetEvalByString
		self.nextRoundIndex = int
	
	def pre_process(self):
		if self.beginTime > self.endTime:
			print "GE_EXC, DEQiangHongBao::self.beginTime > self.endTime,self.roundIndex(%s)" % self.roundIndex
		
		if self.roundType == TYPE_QHB and not self.hongBaoPool:
			print "GE_EXC, DEQiangHongBao::round qiang hong bao but not hongbao! roundIndex(%s)" % self.roundIndex
			
		if self.roundType == TYPE_QG and not self.goodsPool:
			print "GE_EXC, DEQiangHongBao::round kuang gou but not goodsPool! roundIndex(%s)" % self.roundIndex

def LoadDEQiangHongBaoControl():
	global DEQiangHongBao_RoundControl_Dict
	for cfg in DEQiangHongBaoControl.ToClassType():
		roundIndex = cfg.roundIndex
		if roundIndex in DEQiangHongBao_RoundControl_Dict:
			print "GE_EXC,repeat roundIndex(%s) in DEQiangHongBao_RoundControl_Dict" % roundIndex
		cfg.pre_process()
		DEQiangHongBao_RoundControl_Dict[roundIndex] = cfg


class DECoupons(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DECoupons.txt")
	def __init__(self):
		self.itemCoding = int
		self.discountPercent = int
		self.maxDiscount = int


def LoadDECoupons():
	global DEQiangHongBao_CouponsConfig_Dict
	for cfg in DECoupons.ToClassType():
		itemCoding = cfg.itemCoding
		if itemCoding in DEQiangHongBao_CouponsConfig_Dict:
			print "GE_EXC, repeat itemCoding(%s) in DEQiangHongBao_CouponsConfig_Dict" % itemCoding
		DEQiangHongBao_CouponsConfig_Dict[itemCoding] = cfg


def LoadAndCheckConfig():
	'''
	加载配置
	'''
	LoadDEQiangHongBaoGoods()
	LoadDEQiangHongBaoControl()
	LoadDECoupons()
	
	for tRoundIndex, tCfg in DEQiangHongBao_RoundControl_Dict.iteritems():
		isError = False
		for roundIndex, cfg in DEQiangHongBao_RoundControl_Dict.iteritems():
			if tRoundIndex != roundIndex:
				if not (tCfg.endTime > cfg.beginTime or cfg.endTime > tCfg.beginTime):
					print "GE_EXC,DEQiangHongBao::time error found in roundindex(%s) and roundIndex(%s)" % (tCfg.roundIndex, cfg.roundIndex)
					isError = True
					break
		
		if isError:
			break


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadAndCheckConfig()		