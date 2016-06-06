#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActD12OptionShopConfig")
#===============================================================================
# 双十二自选商城配置
#===============================================================================

import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	DES_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DES_FILE_FOLDER_PATH.AppendPath("PassionActDoubleTwelve")
	
	#
	D12ShopConfig_Dict = {}
	D12ShopDiscount_Dict = {}
	
#自选商城配置
class D12ShopConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("PassionShop.txt")
	def __init__(self):
		self.type 			= int 							#配置类型
		self.index			= int 							#物品索引
		self.needLevel		= self.GetEvalByString 			#兑换需要的角色等级段
		self.items			= self.GetEvalByString 			#物品(coding,cnt)
		self.isRMB_Q		= int 							#是否消耗充值神石
		self.needRMB		= int 							#物品单价
		self.daylimitCnt	= int 							#每日限购数量
		self.totallimitCnt	= int 							#活动期间限购数量
		

class D12ShopDisCountConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("PassionShopDiscount.txt")
	def __init__(self):
		self.needRMB 	= int 		#商品总价下限
		self.discount 	= int 	#折扣

	@classmethod
	def GetDiscount(cls,RMB):
		maxRMB = 0
		for needRMB,_ in D12ShopDiscount_Dict.iteritems():
			if RMB >= needRMB:
				maxRMB = max(maxRMB,needRMB)

		return D12ShopDiscount_Dict.get(maxRMB)

	
def LoadD12ShopConfig():
	global D12ShopConfig_Dict
	
	for cfg in D12ShopConfig.ToClassType():
		if cfg.index in D12ShopConfig_Dict:
			print "GE_EXC, repeat index (%s) in D12ShopConfig_Dict" % cfg.index
			continue
		D12ShopConfig_Dict[cfg.index] = cfg

def LoadD12DiscountConfig():
	global D12ShopDiscount_Dict

	for cfg in D12ShopDisCountConfig.ToClassType():
		if cfg.needRMB in D12ShopDiscount_Dict:
			print "GE_EXC, repeat needRMB (%s) in D12ShopDiscount_Dict " % cfg.needRMB 
			continue
		D12ShopDiscount_Dict[cfg.needRMB] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadD12ShopConfig()
		LoadD12DiscountConfig()