#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FB.EvilHoleConfig")
#===============================================================================
# 恶魔深渊配置表
#===============================================================================
import math
import Environment
import DynamicPath
from Util.File import TabFile
from Common.Other import GlobalPrompt
from Game.Activity.RewardBuff import RewardBuff


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("FBAndEvilHoleConfig")
	
	#恶魔深渊配置表
	EvilHoleCfg_Dict = {}
	#恶魔深渊奖励配置表
	EvilHoleRewardDict = {}

class EvilHoleConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("EvilHole.txt")
	def __init__(self):
		self.evilIndex = int
		self.needLevel = int
		
		self.needStar = int
		self.needColorCode = int
		
		self.needPassIndex = int
		self.sceneID = int
		self.posX = int
		self.posY = int
		
		self.bossData = self.GetEvalByString
	
	def LinkReward(self):
		self.rewardConfig = EvilHoleRewardDict.get(self.evilIndex)
	
	def RewardRole(self, role, star, cnt = 1):
		return self.rewardConfig.RewardRole(role, star, cnt)
	
	
	
#恶魔深渊星级奖励配置表
class EvilHoleRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("EvilHoleReward.txt")
	def __init__(self):
		self.evilIndex				= int
		
		self.star1RewardExp 		= int
		self.star1RewardItemList	= self.GetEvalByString
		
		self.star2RewardExp 		= int
		self.star2RewardItemList	= self.GetEvalByString
		
		self.star3RewardExp 		= int
		self.star3RewardItemList	= self.GetEvalByString
		
		self.bxReward				= self.GetEvalByString
		
		self.star1RewardExp_fcm = int                      #一星通关奖励经验
		self.star1RewardItemList_fcm = self.GetEvalByString#[(物品Coding, 物品数量),(x, x)]
		self.star2RewardExp_fcm = int                      #2星通关奖励经验
		self.star2RewardItemList_fcm = self.GetEvalByString#[(物品Coding, 物品数量),(x, x)]
		self.star3RewardExp_fcm = int                      #3星通关奖励经验
		self.star3RewardItemList_fcm = self.GetEvalByString#[(物品Coding, 物品数量),(x, x)]
		self.bxReward_fcm = self.GetEvalByString           #宝箱奖励
	
	def RewardRole(self, role, star, cnt = 1):
		totalExp = 0
		items = None
		#根据星级奖励玩家(暂时不判断背包)
		################################################
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:#收益减半
			if star == 1:
				totalExp = self.star1RewardExp_fcm * cnt
				items = self.star1RewardItemList_fcm
			elif star == 2:
				totalExp = self.star2RewardExp_fcm * cnt
				items = self.star2RewardItemList_fcm
			elif star == 3:
				totalExp = self.star3RewardExp_fcm * cnt
				items = self.star3RewardItemList_fcm
		elif yyAntiFlag == 0:#原有收益
			if star == 1:
				totalExp = self.star1RewardExp * cnt
				items = self.star1RewardItemList
			elif star == 2:
				totalExp = self.star2RewardExp * cnt
				items = self.star2RewardItemList
			elif star == 3:
				totalExp = self.star3RewardExp * cnt
				items = self.star3RewardItemList
		else:
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
			return
		################################################
		tips = GlobalPrompt.Reward_Tips
		RC = RewardBuff.CalNumber
		RG = RewardBuff.GetRewardBuffCoef
		RE = RewardBuff.enEvilHole
		#奖励加成buff加成的数值是向上取整的
		totalExp = int(totalExp * (1 + role.GetExpCoef() / 100.0) + math.ceil(totalExp * RG(RE)))
		role.IncExp(totalExp)
		tips += GlobalPrompt.Exp_Tips % totalExp
		for itemCoding, itemCnt in items:
			extralCnt = RC(RE, itemCnt * cnt)
			role.AddItem(itemCoding, extralCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, extralCnt)
		
		role.Msg(2, 0, tips)
		
	
	def BoxReward(self, role):
		
		################################################
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:#收益减半
			tmpBoxReward = self.bxReward_fcm
		elif yyAntiFlag == 0:#原有收益
			tmpBoxReward = self.bxReward
		else:
			tmpBoxReward = ()
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
			return
		################################################
		tips = GlobalPrompt.Reward_Tips
		for itemCoding, itemCnt in tmpBoxReward:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		role.Msg(2, 0, tips)

def LoadEvilHoleConfig():
	#读取恶魔深渊基本配置表
	global EvilHoleCfg_Dict
	for rowItems in EvilHoleConfig.ToClassType():
		if rowItems.evilIndex in EvilHoleCfg_Dict:
			print "GE_EXC, Repeat cfg value in EvilHoleCfg_Dict repeat evilIndex (%s)" % rowItems.evilIndex
		EvilHoleCfg_Dict[ rowItems.evilIndex ] = rowItems
		rowItems.LinkReward()
		

def LoadEvilHoleRewardConfig():
	global EvilHoleRewardDict
	for rowItems in EvilHoleRewardConfig.ToClassType():
		if rowItems.evilIndex in EvilHoleRewardDict:
			print "GE_EXC, Repeat cfg value in FBEvilHoleRewardConfig repeat rewardID (%s)" % rowItems.evilIndex
		EvilHoleRewardDict[ rowItems.evilIndex ] = rowItems

if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		LoadEvilHoleRewardConfig()
		LoadEvilHoleConfig()
