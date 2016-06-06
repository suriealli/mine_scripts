#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTG3in2Config")
#===============================================================================
# 买二送一
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	DES_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DES_FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	TG3in2Config_Dict = {}
	
class TG3in2Config(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("PassionActTG3in2.txt")
	def __init__(self):
		self.coding		= int                            #物品coding
		self.needRMB	= int                           #需要充值神石数
		self.needLevel	= int                         #兑换需要的角色等级
	
def LoadTG3in2Config():
	global TG3in2Config_Dict
	
	for cfg in TG3in2Config.ToClassType():
		if cfg.coding in TG3in2Config_Dict:
			print "GE_EXC, repeat coding (%s) in TG3in2Config_Dict" % cfg.coding
			continue
		TG3in2Config_Dict[cfg.coding] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTG3in2Config()
