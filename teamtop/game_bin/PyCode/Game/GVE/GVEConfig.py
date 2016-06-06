#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.GVE.GVEConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile
from Game.Item import ItemConfig

GVE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
GVE_FILE_FOLDER_PATH.AppendPath("GVE")

if "_HasLoad" not in dir():
	GVE_FB = {}
	GVE_FB_REWARD = {}
	
class GVEFB(TabFile.TabLine):
	'''
	GVE副本
	'''
	FilePath = GVE_FILE_FOLDER_PATH.FilePath("GVEFB.txt")
	def __init__(self):
		self.fbId = int
		self.fbName = str
		self.sceneId = int
		self.posX = int
		self.posY = int
		self.needLevel = int
		
		self.rewardId = int 			#通关翻牌奖励(按照星级决定抽奖次数)
	
		self.mc1 = self.GetEvalByString	#(怪物npc类型,坐标x,坐标y,朝向,奖励ID,战斗数据索引, 战斗类型)
		self.mc2 = self.GetEvalByString
		self.mc3 = self.GetEvalByString
		
class GVEFBReward(TabFile.TabLine):
	'''
	GVE副本奖励
	'''
	FilePath = GVE_FILE_FOLDER_PATH.FilePath("GVEFBReward.txt")
	def __init__(self):
		self.rewardId = int
		self.money = int
		
		self.rate1 = int
		self.itemCoding1 = int
		self.cnt1 = int
		
		self.rate2 = int
		self.itemCoding2 = int
		self.cnt2 = int
		
		self.rate3 = int
		self.itemCoding3 = int
		self.cnt3 = int
		
		self.rate4 = int
		self.itemCoding4 = int
		self.cnt4 = int
		
		self.rate5 = int
		self.itemCoding5 = int
		self.cnt5 = int
		
	def PreprocessReward(self):
		#读取配置时候预处理，检测
		self.rewardItems = []
		
		self.randomObj = Random.RandomRate()
		if self.rate1:
			self.randomObj.AddRandomItem(self.rate1, (self.itemCoding1, self.cnt1))
			if not ItemConfig.CheckItemCoding(self.itemCoding1):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemCoding1, self.rewardId)
		if self.rate2:
			self.randomObj.AddRandomItem(self.rate2, (self.itemCoding2, self.cnt2))
			if not ItemConfig.CheckItemCoding(self.itemCoding2):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemCoding2, self.rewardId)
		if self.rate3:
			self.randomObj.AddRandomItem(self.rate3, (self.itemCoding3, self.cnt3))
			if not ItemConfig.CheckItemCoding(self.itemCoding3):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemCoding3, self.rewardId)
		if self.rate4:
			self.randomObj.AddRandomItem(self.rate4, (self.itemCoding4, self.cnt4))
			if not ItemConfig.CheckItemCoding(self.itemCoding4):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemCoding4, self.rewardId)
		if self.rate5:
			self.randomObj.AddRandomItem(self.rate5, (self.itemCoding5, self.cnt5))
			if not ItemConfig.CheckItemCoding(self.itemCoding5):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemCoding5, self.rewardId)
			
		self.rewardItems.append((self.itemCoding1, self.cnt1))
		self.rewardItems.append((self.itemCoding2, self.cnt2))
		self.rewardItems.append((self.itemCoding3, self.cnt3))
		self.rewardItems.append((self.itemCoding4, self.cnt4))
		self.rewardItems.append((self.itemCoding5, self.cnt5))

def LoadGVEFB():
	global GVE_FB
	for config in GVEFB.ToClassType():
		GVE_FB[config.fbId] = config
		
def LoadGVEFBReward():
	global GVE_FB_REWARD
	for config in GVEFBReward.ToClassType():
		GVE_FB_REWARD[config.rewardId] = config 
		#预处理
		config.PreprocessReward()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsNA() or Environment.IsDevelop):
		LoadGVEFB()
		LoadGVEFBReward()
		