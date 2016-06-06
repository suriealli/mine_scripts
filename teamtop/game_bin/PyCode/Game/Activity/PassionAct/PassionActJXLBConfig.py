#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActJXLBConfig")
#===============================================================================
# 惊喜礼包配置
#===============================================================================

import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	DES_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DES_FILE_FOLDER_PATH.AppendPath("NewYearDay")
	

	JXLB_Dict 	= {}		#惊喜礼包字典
	
#惊喜礼包配置
class JXLBConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("HappyNewYearJXLB.txt")
	def __init__(self):
		self.id 				= int 							#礼包索引
		self.needRMB			= self.GetEvalByString 			#消耗神石[第n-1次消耗神石,第n次消耗神石]
		self.randomItems		= self.GetEvalByString 			#随机奖励[(coding,cnt,rate)]
		self.extReward			= self.GetEvalByString 			#至尊奖励(coding,cnt)

	def pre_process(self):
		self.RandomRate = Random.RandomRate()
		for coding,cnt,rate in self.randomItems:
			self.RandomRate.AddRandomItem(rate,(coding,cnt))

	
def LoadJXLBConfig():
	global JXLB_Dict
	
	for cfg in JXLBConfig.ToClassType():
		if cfg.id in JXLB_Dict:
			print "GE_EXC, repeat id (%s) in JXLB_Dict" % cfg.index
		if len(cfg.needRMB) < 10:
			print "GE_EXC, there must have 10 times in JXLB_Dict where id(%s)", cfg.index

		JXLB_Dict[cfg.id] = cfg
		cfg.pre_process()

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadJXLBConfig()
