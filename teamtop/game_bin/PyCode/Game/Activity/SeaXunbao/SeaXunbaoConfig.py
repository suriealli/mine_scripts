#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SeaXunbao.SeaXunbaoConfig")
#===============================================================================
# 深海寻宝配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	SEAXUNBAO_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SEAXUNBAO_FILE_FOLDER_PATH.AppendPath("SeaXunbao")
	
	SeaXunbao_Dict = {}
	SeaXunbaoLevel_List = []
	SeaXunbaoRumor_Set = set()
	
	SeaXunbao_Map = {}
	
class SeaXunbaoConfig(TabFile.TabLine):
	FilePath = SEAXUNBAO_FILE_FOLDER_PATH.FilePath("SeaXunbao.txt")
	def __init__(self):
		self.xunbaoGrade = int			#寻宝等级(普通, 高级)
		self.normalReward = eval		#普通寻宝奖励
		self.advanceReward = eval		#高级寻宝奖励
		self.minLevel = int				#最小等级
		self.activeId = int				#活动ID
		
	def InitReward(self):
		global SeaXunbaoRumor_Set
		
		self.normalRewardRandom = Random.RandomRate()
		SNA = self.normalRewardRandom.AddRandomItem
		for (tp, coding, cnt, rate, isRumors) in self.normalReward:
			SNA(rate, (tp, coding, cnt))
			if not isRumors:
				continue
			#加入需要传闻集合
			SeaXunbaoRumor_Set.add(coding)
		
		self.advanceRewardRandom = Random.RandomRate()
		SAA = self.advanceRewardRandom.AddRandomItem
		for (tp, coding, cnt, rate, isRumors) in self.advanceReward:
			SAA(rate, (tp, coding, cnt))
			if not isRumors:
				continue
			#加入需要传闻集合
			SeaXunbaoRumor_Set.add(coding)
		
class SeaXunbaoMap(TabFile.TabLine):
	'''
	活动藏宝图掉落配置
	'''
	FilePath = SEAXUNBAO_FILE_FOLDER_PATH.FilePath("SeaXunbaoMap.txt")
	def __init__(self):
		self.activityType = int
		self.fightIdx = int
		self.mapOdds = int
		self.mapCoding = int
	
def LoadSeaXunbaoConfig():
	global SeaXunbao_Dict
	global SeaXunbaoLevel_List
	SeaXunbaoLevel_List = []
	for SX in SeaXunbaoConfig.ToClassType():
		if (SX.xunbaoGrade, SX.minLevel, SX.activeId) in SeaXunbao_Dict:
			print 'GE_EXC, LoadSeaXunbaoConfig repeat (SX.xunbaoGrade %s, SX.minLevel %s, , SX.activeId %s) in SeaXunbao_Dict' % (SX.xunbaoGrade, SX.minLevel, SX.activeId)
		SX.InitReward()
		SeaXunbao_Dict[(SX.xunbaoGrade, SX.minLevel, SX.activeId)] = SX
		if SX.minLevel not in SeaXunbaoLevel_List:
			SeaXunbaoLevel_List.append(SX.minLevel)
	SeaXunbaoLevel_List.sort()
	
def LoadActivityMap():
	global SeaXunbao_Map
	for config in SeaXunbaoMap.ToClassType():
		SeaXunbao_Map[(config.activityType, config.fightIdx)] = config
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSeaXunbaoConfig()
		LoadActivityMap()
		