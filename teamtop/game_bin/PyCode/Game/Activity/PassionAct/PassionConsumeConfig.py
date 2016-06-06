#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionConsumeConfig")
#===============================================================================
# 激情活动 -- 消费返利配置
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment

if "_HasLoad" not in dir():
	PA_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	PA_FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	PassionConsume_Dict = {}
	PassionConsumeLevel_List = []
	
class PassionConsumeConfig(TabFile.TabLine):
	FilePath = PA_FILE_FOLDER_PATH.FilePath("PassionConsumeConfig.txt")
	def __init__(self):
		self.index = int							#奖励索引
		self.minLevel = int							#最小等级
		self.needConsumeRMB = int					#需要消费神石
		self.rewardItems = eval						#奖励道具
	
def LoadPassionConsumeConfig():
	global PassionConsume_Dict, PassionConsumeLevel_List
	
	for PCC in PassionConsumeConfig.ToClassType():
		if (PCC.index, PCC.minLevel) in PassionConsume_Dict:
			print "GE_EXC, repeat index (%s), minLevel (%s) in PassionConsume_Dict" % (PCC.index, PCC.minLevel)
		PassionConsume_Dict[(PCC.index, PCC.minLevel)] = PCC
		PassionConsumeLevel_List.append(PCC.minLevel)
	PassionConsumeLevel_List = list(set(PassionConsumeLevel_List))
	PassionConsumeLevel_List.sort()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassionConsumeConfig()
	
