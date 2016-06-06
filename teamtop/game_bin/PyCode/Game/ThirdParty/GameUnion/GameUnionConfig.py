#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.GameUnion.GameUnionConfig")
#===============================================================================
# 游戏联盟登录奖励配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile



if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("GameUnionLogAward")
	GameUnionAiwanDict = {}
	GameUnionQQGJDict = {}
	GameUnionAiwanLogDict = {}
	GameUnionQQGJLogDict = {}
	
class GameUnionAiwanConfig(TabFile.TabLine):
	'''
	爱玩连续登陆奖励
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("GameUnionAiwan.txt")
	def __init__(self):
		self.days = int
		self.bindRMB = int
		self.rewardItemList = self.GetEvalByString

class GameUnionQQGJConfig(TabFile.TabLine):
	'''
	QQ管家连续登陆奖励
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("GameUnionQQGJ.txt")
	def __init__(self):
		self.days = int
		self.bindRMB = int
		self.rewardItemList = self.GetEvalByString
		
class GameUnionAiwanLogConfig(TabFile.TabLine):
	'''
	爱玩每日登陆奖励
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("GameUnionAiwanLog.txt")
	def __init__(self):
		self.level = int
		self.bindRMB = int
		self.rewardItemList = self.GetEvalByString


class GameUnionQQGJLogConfig(TabFile.TabLine):
	'''
	QQ管家每日登陆奖励
	'''
	FilePath = FILE_FOLDER_PATH.FilePath("GameUnionQQGJLog.txt")
	def __init__(self):
		self.level = int
		self.bindRMB = int
		self.rewardItemList = self.GetEvalByString
	
def LoadGameUnionAiwanConfig():
	global GameUnionAiwanDict
	for config in GameUnionAiwanConfig.ToClassType():
		if config.days in GameUnionAiwanDict:
			print "GE_EXC,repeat config.days(%s) in GameUnionAiwanConfig" % config.days
		GameUnionAiwanDict[config.days] = config 
	
def LoadGameUnionQQGJConfig():
	global GameUnionQQGJDict
	for config in GameUnionQQGJConfig.ToClassType():
		if config.days in GameUnionQQGJDict:
			print "GE_EXC,repeat config.days(%s) in GameUnionAiwanConfig" % config.days
		GameUnionQQGJDict[config.days] = config

def LoadGameUnionAiwanLogConfig():
	global GameUnionAiwanLogDict
	for config in GameUnionAiwanLogConfig.ToClassType():
		if config.level in GameUnionAiwanLogDict:
			print "GE_EXC,repeat config.level(%s) in GameUnionAiwanLogConfig" % config.level
		GameUnionAiwanLogDict[config.level] = config 

def LoadGameUnionQQGJLogConfig():
	global GameUnionQQGJLogDict
	for config in GameUnionQQGJLogConfig.ToClassType():
		if config.level in GameUnionQQGJLogDict:
			print "GE_EXC,repeat config.level(%s) in GameUnionQQGJLogConfig" % config.level
		GameUnionQQGJLogDict[config.level] = config 

if "_HasLoad" not in dir():
	if Environment.HasLogic  and (not Environment.IsCross):
		LoadGameUnionAiwanConfig()
		LoadGameUnionQQGJConfig()
		LoadGameUnionAiwanLogConfig()
		LoadGameUnionQQGJLogConfig()
		
		
