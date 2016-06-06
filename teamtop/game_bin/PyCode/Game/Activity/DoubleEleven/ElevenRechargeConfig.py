#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.ElevenRechargeConfig")
#===============================================================================
# 双十一活动 --充值大放送 @author: Gaoshuai 2015
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment

if "_HasLoad" not in dir():
	PA_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	PA_FILE_FOLDER_PATH.AppendPath("DoubleEleven")
	
	ElevenRechargeDict = {}
	
class ElevenRechargeConfig(TabFile.TabLine):
	FilePath = PA_FILE_FOLDER_PATH.FilePath("ElevenRechargeConfig.txt")
	def __init__(self):
		self.index = int							#奖励索引
		self.needRechargeRMB = int					#需要充值神石
		self.rewardItems = eval						#奖励道具
	
def LoadElevenRechargeConfig():
	global ElevenRechargeDict
	
	for PRC in ElevenRechargeConfig.ToClassType():
		if PRC.index in ElevenRechargeDict:
			print "GE_EXC, repeat index (%s) in ElevenRecharge_Dict" % PRC.index
		ElevenRechargeDict[PRC.index] = PRC
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadElevenRechargeConfig()
	
