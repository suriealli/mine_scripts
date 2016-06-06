#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OpenYear.OpenYearConfig")
#===============================================================================
# 开年活动配置表
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
if "_HasLoad" not in dir():
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("OpenYear")
	
	TotalLoginConfigDict = {}
	ContinueLoginConfigDict = {}
	ConsumeConfigDict = {}


class TotalLoginConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("TotalLogin.txt")
	def __init__(self):
		self.Index = int						#活动id
		self.Days = int							#需要累计登录的天数
		self.Items = eval						#奖励道具
		self.BindRMB = int						#奖励魔晶
		self.Money = int						#奖励金币


class ContinueLoginConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ContinueLogin.txt")
	def __init__(self):
		self.Index = int						#活动id
		self.Days = int							#需要连续登录的天数
		self.Items = eval						#奖励道具
		self.BindRMB = int						#奖励魔晶
		self.Money = int						#奖励金币


class ConsumeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("Consum.txt")
	def __init__(self):
		self.Index = int						#活动id
		self.Consume = int						#需要当天消费的充值神石数
		self.Items = eval						#奖励道具
		self.BindRMB = int						#奖励魔晶
		self.Money = int						#奖励金币


def LoadTotalLoginConfig():
	global TotalLoginConfigDict
	for config in TotalLoginConfig.ToClassType():
		if config.Index in TotalLoginConfigDict:
			print "GE_EXC,repeat Index(%s) in TotalLoginConfigDict" % config.Index
		TotalLoginConfigDict[config.Index] = config

def LoadContinueLoginConfig():
	global ContinueLoginConfigDict
	for config in ContinueLoginConfig.ToClassType():
		if config.Index in ContinueLoginConfigDict:
			print "GE_EXC,repeat Index(%s) in ContinueLoginConfigDict" % config.Index
		ContinueLoginConfigDict[config.Index] = config


def LoadConsumeConfig():
	global ConsumeConfigDict
	for config in ConsumeConfig.ToClassType():
		if config.Index in ConsumeConfigDict:
			print "GE_EXC,repeat Index(%s) in ConsumeConfigDict" % config.Index
		ConsumeConfigDict[config.Index] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTotalLoginConfig()
		LoadContinueLoginConfig()
		LoadConsumeConfig()
