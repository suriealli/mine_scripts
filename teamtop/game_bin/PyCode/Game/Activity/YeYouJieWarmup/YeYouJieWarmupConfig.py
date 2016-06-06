#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.YeYouJieWarmup.YeYouJieWarmupConfig")
#===============================================================================
# 页游节预热配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile



if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("YeYouJieWarmUp")
	
	RechargeRewardsConfigDict = {}
	LoginRewardsConfigDict = {}


class TimeControlConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ShiJianKongZhi.txt")
	def __init__(self):
		self.beginTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString


class RechargeRewardsConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("RechargeRewards.txt")
	def __init__(self):
		self.Level = int
		self.Money = int
		self.Items = eval


class LoginRewardsConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LoginRewards.txt")
	def __init__(self):
		self.Index = int
		self.Days = int
		self.Items = eval


def LoadRechargeRewardsConfig():
	global RechargeRewardsConfigDict
	for config in RechargeRewardsConfig.ToClassType():
		if config.Level in RechargeRewardsConfigDict:
			print "GE_EXC,repeat config.Level(%s) in RechargeRewardsConfigDict in YeYouJieWarmupConfig" % config.Level
		RechargeRewardsConfigDict[config.Level] = config


def LoadLoginRewardsConfig():
	global LoginRewardsConfigDict
	for config in LoginRewardsConfig.ToClassType():
		if config.Index in LoginRewardsConfigDict:
			print "GE_EXC,repeat config.Index(%s) in LoginRewardsConfigDict in YeYouJieWarmupConfig" % config.Index
		LoginRewardsConfigDict[config.Index] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRechargeRewardsConfig()
		LoadLoginRewardsConfig()
