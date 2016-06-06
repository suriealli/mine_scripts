#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionExchangeConfig")
#===============================================================================
# 激情活动 -- 限时兑换配置
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment
from Util import Random

if "_HasLoad" not in dir():
	PA_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	PA_FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	PassionExchangeFresh_Dict = {}
	PassionExchangeFreshMaxCnt = 0
	
	PassionExchange_Dict = {}				#总物品
	PassionExchangeAdvance_Dict = {}		#高档物品
	PassionExchangeNormal_Dict = {}			#普通物品
	PassionExchangeAdvanceLV_List = []		#高档物品列表
	PassionExchangeNormalLV_List = []		#普通物品列表
	PassionExchangeAdvanceRD_Dict = {}		#高档物品随机
	PassionExchangeNormalRD_Dict = {}		#普通物品随机
	
class PassionExchangeFresh(TabFile.TabLine):
	FilePath = PA_FILE_FOLDER_PATH.FilePath("PassionExchangeFresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.needRMB = int
	
def LoadPassionExchangeFresh():
	global PassionExchangeFresh_Dict, PassionExchangeFreshMaxCnt
	
	for PEF in PassionExchangeFresh.ToClassType():
		if PEF.refreshCnt in PassionExchangeFresh_Dict:
			print 'GE_EXC, repeat refreshCnt %s in PassionExchangeFresh_Dict' % PEF.refreshCnt
		PassionExchangeFresh_Dict[PEF.refreshCnt] = PEF
		
		if PEF.refreshCnt > PassionExchangeFreshMaxCnt:
			PassionExchangeFreshMaxCnt = PEF.refreshCnt
	
class PassionExchageConfig(TabFile.TabLine):
	FilePath = PA_FILE_FOLDER_PATH.FilePath("PassionExchange.txt")
	def __init__(self):
		self.goodId = int
		self.goodType = int				#商品类型(1-普通, 2-高级)
		self.minLevel = eval			#等级段
		self.items = eval				#物品
		self.rate = int					#可购买数量
		self.limitCnt = int				#概率
		self.needCoding = int			#兑换需要道具coding
		self.needCnt = int				#兑换需要道具个数
		self.isRecord = int				#是否记录
		
	def PreGrade(self):
		global PassionExchangeAdvance_Dict, PassionExchangeNormal_Dict, PassionExchangeAdvanceRD_Dict, PassionExchangeNormalRD_Dict, PassionExchangeAdvanceLV_List, PassionExchangeNormalLV_List
		
		if self.goodType == 1:
			if self.minLevel not in PassionExchangeNormal_Dict:
				PassionExchangeNormal_Dict[self.minLevel] = {}
				PassionExchangeNormalLV_List.append(self.minLevel)
				
			if self.minLevel not in PassionExchangeNormalRD_Dict:
				PassionExchangeNormalRD_Dict[self.minLevel] = Random.RandomRate()
				
			PassionExchangeNormal_Dict[self.minLevel][self.goodId] = self
			PassionExchangeNormalRD_Dict[self.minLevel].AddRandomItem(self.rate, self.goodId)
			
		elif self.goodType == 2:
			if self.minLevel not in PassionExchangeAdvance_Dict:
				PassionExchangeAdvance_Dict[self.minLevel] = {}
				PassionExchangeAdvanceLV_List.append(self.minLevel)
				
			if self.minLevel not in PassionExchangeAdvanceRD_Dict:
				PassionExchangeAdvanceRD_Dict[self.minLevel] = Random.RandomRate()
				
			PassionExchangeAdvance_Dict[self.minLevel][self.goodId] = self
			PassionExchangeAdvanceRD_Dict[self.minLevel].AddRandomItem(self.rate, self.goodId)
			
		else:
			print 'GE_EXC, PassionExchangeConfig PreGrade goodType %s error' % self.goodType
		
def LoadPassionExchageConfig():
	global PassionExchange_Dict, PassionExchangeAdvance_Dict, PassionExchangeNormal_Dict, PassionExchangeAdvanceRD_Dict, PassionExchangeNormalRD_Dict, PassionExchangeAdvanceLV_List, PassionExchangeNormalLV_List
	
	for PEC in PassionExchageConfig.ToClassType():
		if PEC.goodId in PassionExchange_Dict:
			print 'GE_EXC, repeat goodId %s in NYDiscount_Dict' % PEC.goodId
		PEC.PreGrade()
		PassionExchange_Dict[PEC.goodId] = PEC
	
	#正序
	PassionExchangeAdvanceLV_List.sort(reverse=False)
	PassionExchangeNormalLV_List.sort(reverse=False)
	
	#合并物品和概率
	lastLevel = 0
	for nowLevel in PassionExchangeAdvanceLV_List:
		if not lastLevel:
			lastLevel = nowLevel
			continue
		#上一个等级段的物品 + 这个等级段的物品
		PassionExchangeAdvance_Dict[nowLevel].update(PassionExchangeAdvance_Dict[lastLevel])
		#上个等级段的物品概率 + 这个等级段的物品概率
		for goodId, cfg in PassionExchangeAdvance_Dict[lastLevel].iteritems():
			PassionExchangeAdvanceRD_Dict[nowLevel].AddRandomItem(cfg.rate, goodId)
		#判断一下可随机物品个数
		if len(PassionExchangeAdvanceRD_Dict[nowLevel].randomList) < 2:
			print 'GE_EXC, PassionExchangeConfig PassionExchangeAdvanceRD_Dict[%s] len(randomList) = %s, min 2' % (nowLevel, len(PassionExchangeAdvanceRD_Dict[nowLevel].randomList))
		lastLevel = nowLevel
		
	lastLevel = 0
	for nowLevel in PassionExchangeNormalLV_List:
		if not lastLevel:
			lastLevel = nowLevel
			if len(PassionExchangeNormalRD_Dict[nowLevel].randomList) < 4:
				print 'GE_EXC, PassionExchangeConfig PassionExchangeNormalRD_Dict[%s] len(randomList) = %s, min 4' % (nowLevel, len(PassionExchangeNormalRD_Dict[nowLevel].randomList))
			continue
		PassionExchangeNormal_Dict[nowLevel].update(PassionExchangeNormal_Dict[lastLevel])
		for goodId, cfg in PassionExchangeNormal_Dict[lastLevel].iteritems():
			PassionExchangeNormalRD_Dict[nowLevel].AddRandomItem(cfg.rate, goodId)
		if len(PassionExchangeNormalRD_Dict[nowLevel].randomList) < 4:
			print 'GE_EXC, PassionExchangeConfig PassionExchangeNormalRD_Dict[%s] len(randomList) = %s, min 4' % (nowLevel, len(PassionExchangeNormalRD_Dict[nowLevel].randomList))
		lastLevel = nowLevel
	
	#逆序 -- 为了不设上线
	PassionExchangeAdvanceLV_List.sort(reverse=True)
	PassionExchangeNormalLV_List.sort(reverse=True)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassionExchangeFresh()
		LoadPassionExchageConfig()
		
	
