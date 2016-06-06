#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationDay.DailyLiBaoConfig")
#===============================================================================
# 国庆每日登陆礼包配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("NationDay")
	
	ND_DAILY_LIBAO_DICT = {}	#国庆登陆礼包配置字典{dayIndex：cfg}
	
class DailyLiBaoConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DailyLiBao.txt")
	def __init__(self):
		self.dayIndex 	= int 	#礼包“天数索引” 
		self.item 		= eval	#(礼包coding，cnt)
		self.costRMB 	= int	#补领对应所需神石
	
def LoadDailyLiBaoConfig():
	global ND_DAILY_LIBAO_DICT
	for cfg in DailyLiBaoConfig.ToClassType():
		if cfg.dayIndex in ND_DAILY_LIBAO_DICT:
			print "GE_EXC, repeat dayIndex(%s) in ND_DAILY_LIBAO_DICT" % cfg.dayIndex
		ND_DAILY_LIBAO_DICT[cfg.dayIndex] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDailyLiBaoConfig()