#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionOnlineGiftConfig")
#===============================================================================
# 在线有礼活动配置（七夕新增）
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	OnlineGiftConfigDict = {}


class OnlineGiftConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionOnlineGift.txt")
	def __init__(self):
		self.rewardIndex = int
		self.rewardItem = eval
		self.rate = int


def LoadOnlineGiftConfig():
	global OnlineGiftConfigDict
	for config in OnlineGiftConfig.ToClassType():
		if config.rewardIndex in OnlineGiftConfigDict:
			print "GE_EXC,repeat rewardIndex(%s) in OnlineGiftConfigDict in PassionAct" % config.rewardIndex
		OnlineGiftConfigDict[config.rewardIndex] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadOnlineGiftConfig()
