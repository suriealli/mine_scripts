#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionHongBaoConfig")
#===============================================================================
# 幸运红包配置  @author: Gaoshuai 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionActDoubleTwelve")
	HongBaoDict = {}

class PassionHongBaoConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionHongBao.txt")
	def __init__(self):
		self.itemCoding = self.GetEvalByString
		self.cnts = self.GetEvalByString
		self.RMB = int
		self.maxPercent = int
		
def LoadPassionHongBaoConfig():
	global HongBaoDict
	
	for cfg in PassionHongBaoConfig.ToClassType():
		if cfg.itemCoding in HongBaoDict:
			print "GE_EXC, repeat index(%s) in HongBaoDict" % cfg.itemCoding
		HongBaoDict[cfg.itemCoding] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionHongBaoConfig()
