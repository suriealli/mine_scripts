#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DailyDo.DailyDoConfig")
#===============================================================================
# 每日必做配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	DailyDo_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DailyDo_FILE_FOLDER_PATH.AppendPath("DailyDo")
	
	DailyDo_Dict = {}
	DailyDo_Reward_Dict = {}
	DailyDo_Reward_List = []
	
class DailyDoConfig(TabFile.TabLine):
	FilePath = DailyDo_FILE_FOLDER_PATH.FilePath("DailyDoConfig.txt")
	def __init__(self):
		self.index = int
		self.score = int
		self.max_cnt = int
		self.level_limit = int
		
class DailyDoRewardConfig(TabFile.TabLine):
	FilePath = DailyDo_FILE_FOLDER_PATH.FilePath("DailyDoRewardConfig.txt")
	def __init__(self):
		self.index = int
		self.minLevel = int
		self.need_score = int
		self.tili = int
		self.items = self.GetEvalByString
		self.bindRMB = self.GetIntByString
		self.money = self.GetIntByString
		self.union_exp = self.GetIntByString
		self.union_contribution = self.GetIntByString
		self.jlb = self.GetIntByString
		self.feastWheelNomalTimes = self.GetIntByString
		self.christmasStockings = self.GetIntByString
		self.holidayWishCnt = self.GetIntByString
		self.newYearFreeTimes = self.GetIntByString
		self.huoYueDaLiSteps = self.GetIntByString
		
		self.tili_fcm = self.GetIntByString              #体力
		self.items_fcm = self.GetEvalByString            #物品
		self.bindRMB_fcm = self.GetIntByString           #魔晶
		self.money_fcm = self.GetIntByString             #银币
		self.union_exp_fcm = self.GetIntByString         #公会经验
		self.union_contribution_fcm = self.GetIntByString#公会贡献
		
	def getReward(self, flag):
		if flag == 1:
			return (self.tili_fcm, self.items_fcm, self.bindRMB_fcm, self.money_fcm, self.union_exp_fcm, self.union_contribution_fcm)
		elif flag == 0:
			return (self.tili, self.items, self.bindRMB, self.money, self.union_exp, self.union_contribution)
		else:
			return 0, (), 0, 0, 0, 0
	
def LoadDailyDoConfig():
	global DailyDo_Dict
	for DD in DailyDoConfig.ToClassType():
		if DD.index in DailyDo_Dict:
			print "GE_EXC, repeat index (%s) in DailyDo_Dict" % DD.index
		DailyDo_Dict[DD.index] = DD
	
def LoadDailyDoRewardConfig():
	global DailyDo_Reward_Dict, DailyDo_Reward_List
	for DDR in DailyDoRewardConfig.ToClassType():
		if (DDR.index, DDR.minLevel) in DailyDo_Reward_Dict:
			print "GE_EXC, repeat index %s, minLevel %s in DailyDo_Reward_Dict" % (DDR.index, DDR.minLevel)
		DailyDo_Reward_Dict[(DDR.index, DDR.minLevel)] = DDR
		DailyDo_Reward_List.append(DDR.minLevel)
	
	DailyDo_Reward_List = list(set(DailyDo_Reward_List))
	DailyDo_Reward_List.sort(key = lambda x:x, reverse = False)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadDailyDoConfig()
		LoadDailyDoRewardConfig()
	
	
