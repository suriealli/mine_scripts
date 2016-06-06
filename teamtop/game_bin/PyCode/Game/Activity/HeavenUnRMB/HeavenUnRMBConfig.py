#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HeavenUnRMB.HeavenUnRMBConfig")
#===============================================================================
# 天降神石配置表
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	GOLD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	GOLD_FILE_FOLDER_PATH.AppendPath("HeavenUnRMB")

	HEAVEN_BASE_DICT = {}
	
class HeavenUnRMB(TabFile.TabLine):
	'''
	天降神石配置表
	'''
	FilePath = GOLD_FILE_FOLDER_PATH.FilePath("HeavenUnRMB.txt")
	def __init__(self):
		self.Index 		= int
		self.InputRMB 	= int
		self.ReturnRMB 	= self.GetEvalByString
		self.ReturnRMB_QQ = int
		self.ExtendReturnRMB = int
		self.ExtendReturnPro = int
		self.ExtendReturnCnt = int
		
def LoadHeavenUnRMB():
	global HEAVEN_BASE_DICT
	global RANDOM
	for cfg in HeavenUnRMB.ToClassType():
		if cfg.Index in HEAVEN_BASE_DICT:
			print "GE_EXC,repeat index=(%s) in HeavenUnRMB" % cfg.Index
		RANDOM = Random.RandomRate()
		for reward in cfg.ReturnRMB:
			if len(reward) < 3:
				print "GE_EXC,HeavenUnRMB ReturnRMB length is Wrong, index=(%s)" % cfg.Index
			RANDOM.AddRandomItem(reward[2], (reward[0], reward[1]))
		HEAVEN_BASE_DICT[cfg.Index] = (cfg, RANDOM)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadHeavenUnRMB()