#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionRechargeConfig")
#===============================================================================
# 激情活动 -- 充值返利配置
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment

if "_HasLoad" not in dir():
	PA_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	PA_FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	PassionRecharge_Dict = {}
	PassionRechargeLevel_List = []
	
class PassionRechargeConfig(TabFile.TabLine):
	FilePath = PA_FILE_FOLDER_PATH.FilePath("PassionRechargeConfig.txt")
	def __init__(self):
		self.index = int							#奖励索引
		self.minLevel = int							#最小等级
		self.needRechargeRMB = int					#需要充值神石
		self.rewardItems = eval						#奖励道具
	
def LoadPassionRechargeConfig():
	global PassionRecharge_Dict, PassionRechargeLevel_List
	
	for PRC in PassionRechargeConfig.ToClassType():
		if (PRC.index, PRC.minLevel) in PassionRecharge_Dict:
			print "GE_EXC, repeat index (%s), minLevel (%s) in PassionRecharge_Dict" % (PRC.index, PRC.minLevel)
		PassionRecharge_Dict[(PRC.index, PRC.minLevel)] = PRC
		PassionRechargeLevel_List.append(PRC.minLevel)
	
	PassionRechargeLevel_List = list(set(PassionRechargeLevel_List))
	PassionRechargeLevel_List.sort()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassionRechargeConfig()
	
