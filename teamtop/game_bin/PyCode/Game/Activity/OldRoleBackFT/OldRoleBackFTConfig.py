#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OldRoleBackFT.OldRoleBackFTConfig")
#===============================================================================
# 繁体版老玩家回流配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("OldRoleBakcFT")
	
	SignUpConfigDict = {}
	SignUpRemedyPriceDict = {}


class SignUpConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("SignUpAward.txt")
	def __init__(self):
		self.Day = int
		self.items = eval
		self.money = int
		self.bindRMB = int
		self.unbindRMB = int


class SignUpRemedyConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("SignUpRemedyPrice.txt")
	def __init__(self):
		self.cnt = int
		self.price = int
		

def LoadSignUpConfig():
	global SignUpConfigDict
	for config in SignUpConfig.ToClassType():
		if config.Day in SignUpConfigDict:
			print "GE_EXC,repeat Day(%s) in  SignUpConfigDict in OldRoleBackFTConfig" % config.Day
		SignUpConfigDict[config.Day] = config


def LoadSignUpRemedyConfig():
	global SignUpRemedyPriceDict
	for config in SignUpRemedyConfig.ToClassType():
		if config.cnt in SignUpRemedyPriceDict:
			print "GE_EXC,repeat cnt(%s) in  SignUpConfigDict in OldRoleBackFTConfig" % config.cnt
		SignUpRemedyPriceDict[config.cnt] = config.price


if "_HasLoad" not in dir():
	#这个活动仅仅繁体版才有的
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsFT() or Environment.IsDevelop):
		LoadSignUpConfig()
		LoadSignUpRemedyConfig()
		
