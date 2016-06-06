#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZShopConfig")
#===============================================================================
# QQ蓝钻商店  @author: GaoShuai 2016
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QQLZ")
	QQLZShop_Dict = {}

class QQLZShopConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QQLZShop.txt")
	def __init__(self):
		self.index = int						#索引
		self.needRMB = int						#购买需要神石
		self.recharge = int						#是否充值神石
		self.dayMax = int						#每日限购，-1为不限购
		self.needLevel = self.GetEvalByString	#要求最低等级
		self.item = self.GetEvalByString		#物品
		
def LoadQQLZShopConfig():
	global QQLZShop_Dict
	
	for cfg in QQLZShopConfig.ToClassType():
		if cfg.index in QQLZShop_Dict:
			print "GE_EXC, repeat index(%s) in QQLZShop_Dict" % cfg.index
		QQLZShop_Dict[cfg.index] = cfg
		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZShopConfig()
