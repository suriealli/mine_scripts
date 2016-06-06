#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LiBaoCanChoose.LiBaoChooseConfig")
#===============================================================================
# 可选择的礼包配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("LiBaoCanChoose")
	
	LiBaoChooConfig_Dict = {}
	LiBaoForReward_Dict = {}
	
class LiBaoForChooConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LiBaoForChoose.txt")
	def __init__(self):
		self.itemCoding	= int
		self.index1 	= int
		self.rewardId1	= int
		self.index2 	= int
		self.rewardId2	= int
		self.index3 	= int
		self.rewardId3	= int
		self.index4 	= int
		self.rewardId4	= int
		self.index5 	= int
		self.rewardId5	= int
		self.index6 	= int
		self.rewardId6	= int
		self.index7 	= int
		self.rewardId7	= int
		self.index8 	= int
		self.rewardId8	= int
		
	def PreReward(self):
		self.IndexReward = {}
		self.IndexReward[self.index1] = self.rewardId1
		self.IndexReward[self.index2] = self.rewardId2
		self.IndexReward[self.index3] = self.rewardId3
		self.IndexReward[self.index4] = self.rewardId4
		self.IndexReward[self.index5] = self.rewardId5
		self.IndexReward[self.index6] = self.rewardId6
		self.IndexReward[self.index7] = self.rewardId7
		self.IndexReward[self.index8] = self.rewardId8
	
	def GetRewardId(self, index):
		if index not in self.IndexReward:
			return
		return self.IndexReward.get(index)

class LiBaoForReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LiBaoForReward.txt")
	def __init__(self):
		self.rewardId	= int
		self.money		= int
		self.bindrmb	= int
		self.items		= self.GetEvalByString
	
def LoadLiBaoForChooConfig():
	global LiBaoChooConfig_Dict
	for BC in LiBaoForChooConfig.ToClassType():
		if BC.itemCoding in LiBaoChooConfig_Dict:
			print "GE_EXC, repeat id in LiBaoForChooConfig (%s)" % BC.itemCoding
		LiBaoChooConfig_Dict[BC.itemCoding] = BC
		#检测配置表,预处理
		BC.PreReward()
		
def LoadLiBaoForReward():
	global LiBaoForReward_Dict
	for BR in LiBaoForReward.ToClassType():
		if BR.rewardId in LiBaoForReward_Dict:
			print "GE_EXC, repeat rewardId in LiBaoForReward (%s)" % BR.rewardId
		LiBaoForReward_Dict[BR.rewardId] = BR
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLiBaoForChooConfig()
		LoadLiBaoForReward()