#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Slave.SlaveConfig")
#===============================================================================
# 抓奴隶
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile



if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Slave")
	
	SlaveBuyCatchTimes_Dict = {}
	SlaveBuySaveTimes_Dict = {}
	SlaveBuyBattleTimes_Dict = {}
	SlavePlayReward_Dict = {}
	SlaveExp_Dict = {}
	SlaveMaxExp_Dict = {}


#购买抓捕次数
class SlaveBuyCatchTimes(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SlaveBuyCatch.txt")
	def __init__(self):
		self.times = int
		self.needRMB = int

#购买解救次数
class SlaveBuySaveTimes(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SlaveBuySave.txt")
	def __init__(self):
		self.times = int
		self.needRMB = int

#购买反抗(公会求救次数)
class SlaveBuyBattleTimes(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SlaveBuyBattle.txt")
	def __init__(self):
		self.times = int
		self.needRMB = int


class SlavePlayReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SlavePlayReward.txt")
	def __init__(self):
		self.level = int
		self.rewardItem = self.GetEvalByString
		self.rewardItem_fcm = self.GetEvalByString	#奖励物品

class SlaveExp(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SlaveExp.txt")
	def __init__(self):
		self.level = int
		self.exp = int

class SlaveMaxExp(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SlaveMaxExp.txt")
	def __init__(self):
		self.level = int
		self.exp = int
		
def LoadSlaveBuyCatchTimes():
	global SlaveBuyCatchTimes_Dict
	for SC in SlaveBuyCatchTimes.ToClassType():
		SlaveBuyCatchTimes_Dict[SC.times] = SC.needRMB

def LoadSlaveBuySaveTimes():
	global SlaveBuySaveTimes_Dict
	for SS in SlaveBuySaveTimes.ToClassType():
		SlaveBuySaveTimes_Dict[SS.times] = SS.needRMB

def LoadSlaveBuyBattleTimes():
	global SlaveBuyBattleTimes_Dict
	for SS in SlaveBuyBattleTimes.ToClassType():
		SlaveBuyBattleTimes_Dict[SS.times] = SS.needRMB


def LoadSlavePlayReward():
	global SlavePlayReward_Dict
	for SP in SlavePlayReward.ToClassType():
		SlavePlayReward_Dict[SP.level] = (SP.rewardItem, SP.rewardItem_fcm)

def LoadSlaveExp():
	global SlaveExp_Dict
	for SE in SlaveExp.ToClassType():
		SlaveExp_Dict[SE.level] = SE.exp

def LoadSlaveMaxExp():
	global SlaveMaxExp_Dict
	for SE in SlaveMaxExp.ToClassType():
		SlaveMaxExp_Dict[SE.level] = SE.exp
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		LoadSlaveBuyCatchTimes()
		LoadSlaveBuySaveTimes()
		LoadSlaveBuyBattleTimes()
		LoadSlavePlayReward()
		LoadSlaveExp()
		LoadSlaveMaxExp()
