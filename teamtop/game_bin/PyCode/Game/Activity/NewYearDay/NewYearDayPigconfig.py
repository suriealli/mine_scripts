#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NewYearDay.NewYearDayPigconfig")
#===============================================================================
# 元旦好福利（金猪兑换）配置表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	NYD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	NYD_FILE_FOLDER_PATH.AppendPath("NewYearDay")
	
	GetPigAmount = {}				#获得金猪方式
	PigShop = {}					#金猪兑换商城

class HappyNewYearPig(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("HappyNewYearPig.txt")
	def __init__(self):
		self.TaskIndex = int
		self.rewardNum = int

def LoadHappyNewYearPig():
	global GetPigAmount
	for cf in HappyNewYearPig.ToClassType():
		if cf.TaskIndex in GetPigAmount :
			print "GE_EXC, repeat TaskIndex %s  in LoadHappyNewYearPig" % cf.TaskIndex
		GetPigAmount[cf.TaskIndex] = cf.rewardNum

class HappyNewYearPigShop(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("HappyNewYearPigShop.txt")
	def __init__(self):
		self.boxIndex = int
		self.NeedCnt = int
		self.rewardItems = self.GetEvalByString
		self.LeftCounts = int
		self.NeedLevel = self.GetEvalByString

def LoadHappyNewYearPigShop():
	global PigShop
	for cf in HappyNewYearPigShop.ToClassType():
		if cf.boxIndex in PigShop :
			print "GE_EXC, repeat boxIndex %s  in LoadHappyNewYearPigShop" % cf.boxIndex
		PigShop[cf.boxIndex] = cf



if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadHappyNewYearPig()
		LoadHappyNewYearPigShop()
