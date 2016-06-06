#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.BallFame.BallFameConfig")
#===============================================================================
# 一球成名配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	BALLFAME_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	BALLFAME_FILE_FOLDER_PATH.AppendPath("BallFame")
	
	#进球
	BF_GoalsDict = {}
	#公会喝彩
	BF_UCDict = {}
	#全服喝彩
	BF_ASCDict = {}
	#奖励宝箱字典
	BF_BoxDict = {}
	
class BFGoalsConfig(TabFile.TabLine):
	FilePath = BALLFAME_FILE_FOLDER_PATH.FilePath("BFGoalsConfig.txt")
	def __init__(self):
		self.goalsCnt = int			#进球个数
		self.needItemCnt = int		#需要道具个数
		
class BFUnionCheersConfig(TabFile.TabLine):
	FilePath = BALLFAME_FILE_FOLDER_PATH.FilePath("BFUnionCheersConfig.txt")
	def __init__(self):
		self.cheersCnt = int		#公会喝彩次数
		self.needGoalsCnt = int		#需要公会进球个数
		
class BFASCheersConfig(TabFile.TabLine):
	FilePath = BALLFAME_FILE_FOLDER_PATH.FilePath("BFASCheersConfig.txt")
	def __init__(self):
		self.cheersCnt = int		#全服喝彩次数
		self.needGoalsCnt = int		#需要全服进球个数
		
class BFBoxConfig(TabFile.TabLine):
	FilePath = BALLFAME_FILE_FOLDER_PATH.FilePath("BFRewardBox.txt")
	def __init__(self):
		self.activeId = int				#活动编号
		self.goalsBoxCoding = int		#进球宝箱coding
		self.cheersBoxCoding = int		#喝彩宝箱coding
		
def LoadBFBoxConfig():
	global BF_BoxDict
	for BD in BFBoxConfig.ToClassType():
		if BD.activeId in BF_BoxDict:
			print "GE_EXC, repeat activeId %s in BF_BoxDict" % BD.activeId
			continue
		BF_BoxDict[BD.activeId] = BD
	
def LoadBFGoalsConfig():
	global BF_GoalsDict
	for GC in BFGoalsConfig.ToClassType():
		if GC.goalsCnt in BF_GoalsDict:
			print "GE_EXC, repeat goalsCnt %s in BF_GoalsDict" % GC.goalsCnt
			continue
		BF_GoalsDict[GC.goalsCnt] = GC
	
def LoadBFUnionCheersConfig():
	global BF_UCDict
	for UC in BFUnionCheersConfig.ToClassType():
		if UC.cheersCnt in BF_UCDict:
			print "GE_EXC, repeat cheersCnt %s in BF_UCDict" % UC.cheersCnt
			continue
		BF_UCDict[UC.cheersCnt] = UC
	
def LoadBFASCheersConfig():
	global BF_ASCDict
	for ASCC in BFASCheersConfig.ToClassType():
		if ASCC.cheersCnt in BF_ASCDict:
			print "GE_EXC, repeat cheersCnt %s in BF_ASCDict" % ASCC.cheersCnt
			continue
		BF_ASCDict[ASCC.cheersCnt] = ASCC
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadBFGoalsConfig()
		LoadBFUnionCheersConfig()
		LoadBFASCheersConfig()
		LoadBFBoxConfig()
		
		