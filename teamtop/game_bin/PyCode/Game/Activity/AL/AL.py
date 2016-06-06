#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.AL.AL")
#===============================================================================
# 活动等级经验表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile


if "_HasLoad" not in dir():
	AL_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	AL_FILE_FOLDER_PATH.AppendPath("AL")
	
	ALE_Dict = {}
	ALMoney_Dict = {}

	

class ALE(TabFile.TabLine):
	FilePath = AL_FILE_FOLDER_PATH.FilePath("ALE.txt")
	UseCache = False
	def __init__(self):
		self.level = int
		self.rongyu = int
		self.pub = int
		self.DailyTask = int
		self.run = int
		
class ALMoney(TabFile.TabLine):
	FilePath = AL_FILE_FOLDER_PATH.FilePath("ALMoney.txt")
	def __init__(self):
		self.level = int

def LoadALE():
	#读取等级奖励经验配置
	global ALE_Dict
	for A in ALE.ToClassType():
		if A.level in ALE_Dict:
			print "GE_EXC, repeat level in LoadALE (%s)" % A.level
		ALE_Dict[A.level] = A
		
def LoadALMoney():
	#读取等级奖励金币配置
	global ALMoney_Dict
	for A in ALMoney.ToClassType():
		if A.level in ALMoney_Dict:
			print "GE_EXC, repeat level in LoadALMoney (%s)" % A.level
		ALMoney_Dict[A.level] = A


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadALE()
		LoadALMoney()


