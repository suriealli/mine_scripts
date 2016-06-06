#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionLoginGiftConfig")
#===============================================================================
# 激情活动登录有礼配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	DayIndexConfigDict = {}
	LoginGiftConfigDict = {}
	

class LoginGiftConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionLoginGift.txt")
	def __init__(self):
		self.dayIndex = int	
		self.theDate = eval	
		self.loginItems = eval	
		self.loginMoney = int	
		self.needRechargeRMB = int	
		self.rechargeItems = eval


def LoadLoginGiftConfig():
	global LoginGiftConfigDict
	global DayIndexConfigDict
	for config in LoginGiftConfig.ToClassType():
		if config.dayIndex in LoginGiftConfigDict:
			print "GE_EXC,repeat dayIndex(%s) in LoginGiftConfigDict in PassionLoginGiftConfig" % config.dayIndex
		LoginGiftConfigDict[config.dayIndex] = config
		
		if config.theDate in DayIndexConfigDict:
			print "GE_EXC,repeat theDate(%s) in DayIndexConfigDict in PassionLoginGiftConfig" % config.theDate
		DayIndexConfigDict[config.theDate] = config.dayIndex


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLoginGiftConfig()
