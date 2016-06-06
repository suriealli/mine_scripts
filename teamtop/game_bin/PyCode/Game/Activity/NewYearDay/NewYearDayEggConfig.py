#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NewYearDay.NewYearDayEggConfig")
#===============================================================================
# 2016元旦金蛋活动配置表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	NYD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	NYD_FILE_FOLDER_PATH.AppendPath("NewYearDay")
	
	NYD_Egg_Award = {}				#金蛋活动奖励
	NYD_Egg_Random_Dict = {}		#等级区间的抽奖机
	OnLineAward = {}				#在线奖励
	RMBAward = {}					#充值奖励


class NewYearDayEggAward(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("HappyNewYearEggAward.txt")
	def __init__(self):
		self.AwardID = int
		self.MinLevel = int
		self.MaxLevel = int
		self.RewardItems = self.GetEvalByString
		self.Rate = int


def LoadNewYearDayEggAward():
	global NYD_Egg_Award, NYD_Egg_Random_Dict
	#load抽奖机和奖励
	for cf in NewYearDayEggAward.ToClassType():
		if cf.AwardID in NYD_Egg_Award :
			print "GE_EXC, repeat AwardID %s  in NewYearDayEggAward" % cf.AwardID
		NYD_Egg_Award[cf.AwardID] = cf
		
		if (cf.MinLevel, cf.MaxLevel) not in NYD_Egg_Random_Dict:
			NYD_Egg_Random_Dict[(cf.MinLevel, cf.MaxLevel)] = Random.RandomRate()
		NYD_Egg_Random_Dict[(cf.MinLevel, cf.MaxLevel)].AddRandomItem(cf.Rate, cf.AwardID)

class HappyNewYearOnLineHammer(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("HappyNewYearOnLineHammer.txt")
	def __init__(self):
		self.OnLineIndex = int
		self.NeedTime = int
		self.HammersNumbers = int
		
def LoadHappyNewYearOnLineHammer():
	global OnLineAward
	for cf in HappyNewYearOnLineHammer.ToClassType():
		if cf.OnLineIndex in OnLineAward :
			print "GE_EXC, repeat OnLineIndex %s in LoadHappyNewYearOnLineHammer" % cf.OnLineIndex
		OnLineAward[cf.OnLineIndex] = cf

class HappyNewYearBuyHammer(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("HappyNewYearBuyHammer.txt")
	def __init__(self):
		self.BuyIndex = int
		self.NeedRMB = int
		self.Hammers =int

def LoadHappyNewYearBuyHammer():
	global RMBAward
	for cf in HappyNewYearBuyHammer.ToClassType():
		if cf.BuyIndex in RMBAward:
			print "GE_EXC, repeat BuyIndex %s in LoadHappyNewYearBuyHammer" % cf.BuyIndex
		RMBAward[cf.BuyIndex] = cf


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadNewYearDayEggAward()
		LoadHappyNewYearOnLineHammer()
		LoadHappyNewYearBuyHammer()