#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActD12GroupBuyConfig")
#===============================================================================
# 超值团购配置  @author liujia 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionActDoubleTwelve")

	PassionActD12GB_Dict = {}
	PassionActD12GBControl_Dict = {}


class PassionActD12Config(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionGroupBuy.txt")
	def __init__(self):
		self.index = int 							#物品索引
		self.needLevel = int 						#需要角色最小等级
		self.items = self.GetEvalByString			#道具
		self.needRMB = int 							#需要神石
		self.isRMB_Q = int 							#是否充值神石

class PassionActD12ControlConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GruopBuyControl.txt")
	def __init__(self):
		self.dayIndex = self.GetEvalByString				#物品索引
		self.itemIndex = self.GetEvalByString				#需要角色最小等级

def LoadD12GBConfig():
	global PassionActD12GB_Dict

	for cfg in PassionActD12Config.ToClassType():
		if cfg.index in PassionActD12GB_Dict:
			print "GE_EXC, repeat index(%s) in PassionActD12GB_Dict" % cfg.index
		PassionActD12GB_Dict[cfg.index] = cfg

def LoadElevenPointControlConfig():
	global PassionActD12GBControl_Dict
	
	for cfg in PassionActD12ControlConfig.ToClassType():
		if cfg.dayIndex in PassionActD12GBControl_Dict:
			print "GE_EXC, repeat dayIndex(%s) in PassionActD12GBControl_Dict" % cfg.dayIndex
		PassionActD12GBControl_Dict[cfg.dayIndex] = cfg.itemIndex

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadD12GBConfig()
		LoadElevenPointControlConfig()
