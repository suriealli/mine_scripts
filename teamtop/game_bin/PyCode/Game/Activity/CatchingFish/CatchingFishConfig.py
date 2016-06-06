#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CatchingFish.CatchingFishConfig")
#===============================================================================
#捕鱼达人配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	TT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	TT_FILE_FOLDER_PATH.AppendPath("CatchingFish")
	
	CatchingFish_Dict = {}					#捕鱼的配置
	CatchingFishRandom_Dict = {}			#等级抽奖机{(level,grade):Random.RandomRate()}
	CatchingFishBox = {}					#积分奖励
	CatchingFishGrade = {}					#捕鱼的档次要求
class CatchingFishConfig(TabFile.TabLine):
	FilePath = TT_FILE_FOLDER_PATH.FilePath("CatchingFish.txt")
	def __init__(self):
		self.CatchFinshIndex = int
		self.minLevel = int
		self.grade = int
		self.rate = int
		self.rewardItems = eval
		self.rewardUnbindRMB_S_Percent = int
		self.isRumor = int
		self.isRare = int
		


def LoadCatchingFish():
	global CatchingFishRandom_Dict, CatchingFish_Dict
	maxgrade = 0
	#寻找最高的档次
	for df in CatchingFishConfig.ToClassType() :
		maxgrade = max(maxgrade, df.grade)
		CatchingFish_Dict[df.CatchFinshIndex] = df
	#按等级，档次设置相应的抽奖机
	for df in CatchingFishConfig.ToClassType() :
		index = df.grade
		while index <= maxgrade :
			if (df.minLevel, index) not in CatchingFishRandom_Dict :
				CatchingFishRandom_Dict[(df.minLevel, index)] = Random.RandomRate()
			CatchingFishRandom_Dict[(df.minLevel, index)].AddRandomItem(df.rate, df.CatchFinshIndex)
			index+=1
			


class CatchingFishGradeConfig(TabFile.TabLine):
	FilePath = TT_FILE_FOLDER_PATH.FilePath("CatchingFishGrade.txt")
	def __init__(self):
		self.needPoolValue = int
		self.needCnt = int
		self.grade = int
		

def LoadCatchingFishGradeConfig():
	global CatchingFishGrade
	for cf in CatchingFishGradeConfig.ToClassType() :
		if (cf.needPoolValue, cf.needCnt) in CatchingFishGrade :
			print "GE_EXC, repeat CatchingFishGrade %s  in CatchingFishGrade" % cf.needPoolValue
		CatchingFishGrade[(cf.needPoolValue, cf.needCnt)] = cf
		

class CatchingFishBoxConfig(TabFile.TabLine):
	FilePath = TT_FILE_FOLDER_PATH.FilePath("CatchingFishBox.txt")
	def __init__(self):
		self.boxIndex = int
		self.MinLevel = int
		self.MaxLevel = int
		self.needCnt = int
		self.rewardItems = self.GetEvalByString
		self.rewardMoney = int
		self.rewardBindRMB = int
		self.rewardUnbindRMB_S = int
		

def LoadCatchingFishBoxConfig():
	global CatchingFishBox
	for cf in CatchingFishBoxConfig.ToClassType() :
		if (cf.boxIndex, cf.MinLevel) in CatchingFishBox :
			print "GE_EXC, repeat boxIndex %s MinLevel % in CatchingFishBox" % (cf.boxIndex, cf.MinLevel)
		CatchingFishBox[(cf.boxIndex, cf.MinLevel)] = cf
		



if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadCatchingFish()
		LoadCatchingFishGradeConfig()
		LoadCatchingFishBoxConfig()