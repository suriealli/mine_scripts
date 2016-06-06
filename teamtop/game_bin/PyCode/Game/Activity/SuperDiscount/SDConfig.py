#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SuperDiscount.SDConfig")
#===============================================================================
# 超值大礼配置 akm
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("SuperDiscount")
	
	SUPERDISCOUNT_LIBAO_DICT = {}		#超值大礼礼包配置 	{LiBaoID：cfg}	
	SUPERDISCOUNT_LIBAO_TYPE_DICT = {}	#超值大礼礼包		{SDType:set([LiBaoID,])	

class SuperDiscountLiBao(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DiscountLiBao.txt")
	def __init__(self):
		self.LiBaoID = int 
		self.SDType = int 
		self.Cnt = int 
		self.RealPrice = int 
		self.MoneyType = int					#购买货币类型约束 
		self.RealItems = self.GetEvalByString
		self.RewardMoney = int 					#金币
		self.RewardRMB = int 					#奖励神石
		self.RewardBindRMB = int				#魔晶

def LoadSuperDiscountLiBao():
	global SUPERDISCOUNT_LIBAO_DICT
	global SUPERDISCOUNT_LIBAO_TYPE_DICT
	
	for config in SuperDiscountLiBao.ToClassType():
		if config.LiBaoID in SUPERDISCOUNT_LIBAO_DICT:
			print "GE_EXC, super discount::repeat LiBaoID(%s)" % config.LiBaoID
		if config.MoneyType != 0 and config.MoneyType != 1:
			print "GE_EXC,SuperDiscount::error MoneyType(%s)" % config.MoneyType
			continue
		SUPERDISCOUNT_LIBAO_DICT[config.LiBaoID] = config
		
		typeSet = SUPERDISCOUNT_LIBAO_TYPE_DICT.setdefault(config.SDType, set())
		if config.LiBaoID in typeSet:
			print "GE_EXC, super discount::repeat LiBaoID(%s) in type(%s)" % (config.LiBaoID,config.SDType)
		typeSet.add(config.LiBaoID)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadSuperDiscountLiBao()


