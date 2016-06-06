#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionChunJieActiveConfig")
#===============================================================================
# 春节活跃有礼配置表
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	PassionChunJieActiveConfigDict = {}
	
class PassionChunJieActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionChunJieActive.txt")
	def __init__(self):
		self.DayIndex = int
		self.MinDailyDoScore = int
		self.MinRechargeRMB = int
		self.LoginReward = self.GetEvalByString
		self.DailyDoReward = self.GetEvalByString
		self.RechargeReward = self.GetEvalByString

def LoadPassionChunJieActive():
	global PassionChunJieActiveConfigDict
	for cf in PassionChunJieActive.ToClassType() :
		if cf.DayIndex in PassionChunJieActiveConfigDict :
			print "GE_EXC, repeat DayIndex %s is in PassionChunJieActiveConfigDict" % cf.DayIndex
		PassionChunJieActiveConfigDict[cf.DayIndex] = cf
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassionChunJieActive()