#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.GlamourCoinExchangeConfig")
#===============================================================================
# 魅力币兑换Config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ValentineDay")
	
	GlamourCoinExchange_ExchangeConfig_Dict = {}
	
class GlamourCoinExchange(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GlamourCoinExchange.txt")
	def __init__(self):
		self.coding = int							#物品coding
		self.needCoding = int						#需要物品coding
		self.needLevel = int						#兑换需要的角色等级
		self.needWorldLevel = int					#兑换需要的世界等级
		self.limitCnt = int							#限购个数(0-不限购)
		self.needItemCnt = int						#兑换需要的物品个数
	
def LoadGlamourCoinExchange():
	global GlamourCoinExchange_ExchangeConfig_Dict
	
	for NSC in GlamourCoinExchange.ToClassType():
		if NSC.coding in GlamourCoinExchange_ExchangeConfig_Dict:
			print "GE_EXC, repeat coding (%s) in GlamourCoinExchange_ExchangeConfig_Dict" % NSC.coding
			continue
		GlamourCoinExchange_ExchangeConfig_Dict[NSC.coding] = NSC
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGlamourCoinExchange()