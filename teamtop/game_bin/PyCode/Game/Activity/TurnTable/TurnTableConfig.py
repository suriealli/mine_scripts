#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TurnTable.TurnTableConfig")
#===============================================================================
# 全名转转乐配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	TT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	TT_FILE_FOLDER_PATH.AppendPath("TurnTable")
	
	TurnTable_Dict = {}
	TurnTableLevel_List = []
	TurnTableRandom_Dict = {}
	TurnTableGrade_Dict = {}
	
	TurnTableCntGrade_Dict = {}
	TurnTableCntGrade_List = []
	TurnTablePoolGrade_Dict = {}
	TurnTablePoolGrade_List = []
	
	TurnTableBox_Dict = {}
	
	TurnTableEx_Dict = {}
	TurnTableRandomEx_Dict = {}		#这里的等级段和TurnTableRandom_Dict中的是一样的
	
class TurnTableConfig(TabFile.TabLine):
	FilePath = TT_FILE_FOLDER_PATH.FilePath("TurnTable.txt")
	def __init__(self):
		self.tableIndex = int						#转盘索引
		self.minLevel = int							#最小等级
		self.grade = int							#档次
		self.rate = int								#概率
		self.rewardItems = eval						#奖励物品
		self.rewardUnbindRMB_S_Percent = int		#奖励奖池神石百分百
		self.isRumor = int							#是否广播（广播的都记录）
		self.isRare = int							#是否稀有(0-不稀有, 1-稀有)
		
	def InitRandom(self):
		global TurnTableGrade_Dict, TurnTableRandom_Dict
		if self.grade not in TurnTableRandom_Dict:
			TurnTableRandom_Dict[self.grade] = {}
		if self.grade  not in TurnTableGrade_Dict:
			TurnTableGrade_Dict[self.grade] = {}
			
		if self.minLevel not in TurnTableRandom_Dict[self.grade]:
			TurnTableRandom_Dict[self.grade][self.minLevel] = Random.RandomRate()
		if self.minLevel not in TurnTableGrade_Dict[self.grade]:
			TurnTableGrade_Dict[self.grade][self.minLevel] = {}
		
		TurnTableGrade_Dict[self.grade][self.minLevel][self.tableIndex] = self
		TurnTableRandom_Dict[self.grade][self.minLevel].AddRandomItem(self.rate, self.tableIndex)
		
def LoadTurnTableConfig():
	global TurnTable_Dict, TurnTableLevel_List, TurnTableGrade_Dict
	
	gradeList = []
	for TT in TurnTableConfig.ToClassType():
		if (TT.tableIndex, TT.minLevel) in TurnTable_Dict:
			print "GE_EXC, repeat tableIndex %s minLevel %s in TurnTable_Dict" % (TT.tableIndex, TT.minLevel)
		#预处理随机
		TT.InitRandom()
		
		TurnTable_Dict[(TT.tableIndex, TT.minLevel)] = TT
		#档次列表
		gradeList.append(TT.grade)
		#等级列表
		TurnTableLevel_List.append(TT.minLevel)
	
	#去重
	gradeList = list(set(gradeList))
	gradeList.sort()
	
	TurnTableLevel_List = list(set(TurnTableLevel_List))
	TurnTableLevel_List.sort()
	
	#要把上一个档次的转盘索引加到后一个档次上去
	lastGrade = 0
	tmpGradeDict = {}
	for grade in gradeList:
		for lv in TurnTableLevel_List:
			if lastGrade not in TurnTableGrade_Dict or grade not in TurnTableGrade_Dict:
				continue
			if lv not in TurnTableGrade_Dict[lastGrade]:
				continue
			for tableIndex, cfg in TurnTableGrade_Dict[lastGrade][lv].iteritems():
				if tableIndex in TurnTableGrade_Dict[grade][lv]:
					continue
				tmpGradeDict[tableIndex] = cfg
			#合并
			TurnTableGrade_Dict[grade][lv].update(tmpGradeDict)
			#合并随机
			for cfg in tmpGradeDict.itervalues():
				TurnTableRandom_Dict[grade][lv].AddRandomItem(cfg.rate, cfg.tableIndex)
			tmpGradeDict = {}
			
		lastGrade = grade
	
class TurnTableExConfig(TabFile.TabLine):
	FilePath = TT_FILE_FOLDER_PATH.FilePath("TurnTableEx.txt")
	def __init__(self):
		self.tableIndex = int						#转盘索引
		self.minLevel = int							#最小等级
		self.rate = int								#概率
		self.rewardItems = eval						#奖励物品
		self.rewardUnbindRMB_S_Percent = int		#奖励奖池神石百分百
		self.isRumor = int							#是否广播（广播的都记录）
		self.isRare = int							#是否稀有(0-不稀有, 1-稀有)
		
	def InitRandom(self):
		global TurnTableRandomEx_Dict
		if self.minLevel not in TurnTableRandomEx_Dict:
			TurnTableRandomEx_Dict[self.minLevel] = Random.RandomRate()
		TurnTableRandomEx_Dict[self.minLevel].AddRandomItem(self.rate, self.tableIndex)
	
def LoadTurnTableExConfig():
	global TurnTableEx_Dict, TurnTableLevelEx_List
	
	for TT in TurnTableExConfig.ToClassType():
		if (TT.tableIndex, TT.minLevel) in TurnTableEx_Dict:
			print "GE_EXC, repeat tableIndex %s minLevel %s in TurnTableEx_Dict" % (TT.tableIndex, TT.minLevel)
		#预处理随机
		TT.InitRandom()
		
		TurnTableEx_Dict[(TT.tableIndex, TT.minLevel)] = TT
	
class TurnTableCntGradeConfig(TabFile.TabLine):
	FilePath = TT_FILE_FOLDER_PATH.FilePath("TurnTableCntGrade.txt")
	def __init__(self):
		self.needCnt = int				#抽奖次数
		self.grade = int				#档次
		
def LoadTurnTableCntGradeConfig():
	global TurnTableCntGrade_Dict, TurnTableCntGrade_List
	
	for TTC in TurnTableCntGradeConfig.ToClassType():
		if TTC.needCnt in TurnTableCntGrade_Dict:
			print "GE_EXC, repeat needCnt(%s) in TurnTableCnt_Dict" % TTC.needCnt
		TurnTableCntGrade_Dict[TTC.needCnt] = TTC.grade
		TurnTableCntGrade_List.append(TTC.needCnt)
	TurnTableCntGrade_List = list(set(TurnTableCntGrade_List))
	TurnTableCntGrade_List.sort()
	
class TurnTablePoolGradeConfig(TabFile.TabLine):
	FilePath = TT_FILE_FOLDER_PATH.FilePath("TurnTablePoolGrade.txt")
	def __init__(self):
		self.needPoolValue = int		#奖池神石数
		self.grade = int				#档次
		
def LoadTurnTablePoolGradeConfig():
	global TurnTablePoolGrade_Dict, TurnTablePoolGrade_List
	
	for TTP in TurnTablePoolGradeConfig.ToClassType():
		if TTP.needPoolValue in TurnTablePoolGrade_Dict:
			print "GE_EXC, repeat needPoolValue(%s) in TurnTablePoolGrade_Dict" % TTP.needPoolValue
		TurnTablePoolGrade_Dict[TTP.needPoolValue] = TTP.grade
		TurnTablePoolGrade_List.append(TTP.needPoolValue)
	TurnTablePoolGrade_List = list(set(TurnTablePoolGrade_List))
	TurnTablePoolGrade_List.sort()
	
class TurnTableBoxConfig(TabFile.TabLine):
	FilePath = TT_FILE_FOLDER_PATH.FilePath("TurnTableBox.txt")
	def __init__(self):
		self.boxIndex = int
		self.needCnt = int
		self.rewardItems = eval
		self.rewardMoney = int
		self.rewardBindRMB = int
		
def LoadTurnTableBoxConfig():
	global TurnTableBox_Dict
	
	for TTB in TurnTableBoxConfig.ToClassType():
		if TTB.boxIndex in TurnTableBox_Dict:
			print "GE_EXC, repeat boxIndex(%s) in TurnTableBox_Dict" % TTB.boxIndex
		TurnTableBox_Dict[TTB.boxIndex] = TTB
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTurnTableConfig()
		LoadTurnTableExConfig()
		LoadTurnTableCntGradeConfig()
		TurnTablePoolGradeConfig()
		LoadTurnTablePoolGradeConfig()
		LoadTurnTableBoxConfig()
