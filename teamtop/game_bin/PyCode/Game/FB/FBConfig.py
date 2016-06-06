#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FB.FBConfig")
#===============================================================================
# 副本配置
#===============================================================================
import Environment
import DynamicPath
from Common.Other import GlobalPrompt
from Util.File import TabFile
from Game.FB import FBReward
from Game.Role.Data import EnumCD


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("FBAndEvilHoleConfig")
	
	#副本配置
	FB_Config_Dict 		= {}
	#副本购买增加次数
	FB_BuyAddTimeDict	= {}
	#副本章节宝箱奖励
	FBZJRewardConfig_Dict = {}
	
	#每一个章节对应的副本Id列表
	FBZJ_Config_Dict = {}
	#每一个章节最后一个副本id
	FBZJ_MaxFBId = {}
	

#===============================================================================
#普通副本配置
class FBConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("FB.txt")
	def __init__(self):
		self.FBID = int
		self.zjID = int
		self.fbName = str
		self.sceneID = int
		self.posX = int
		self.posY = int
		self.needLevel = int
		
		self.rewardId = int 			#通关翻牌奖励(按照星级决定抽奖次数)
		self.mc1 = self.GetEvalByString #(怪物npc类型,坐标x,坐标y,朝向,奖励ID,战斗数据索引, 战斗类型)
		self.mc2 = self.GetEvalByString
		self.mc3 = self.GetEvalByString

	def PreCodingFBData(self):
		#根据平配置表数据预处理生成副本数据
		#扫荡奖励配置
		self.rewardList = []
		self.monsterCfgs = []
		self.monsterCfgs.append(self.mc1)
		self.monsterCfgs.append(self.mc2)
		self.monsterCfgs.append(self.mc3)
		
		for m in self.monsterCfgs:
			rewardId = m[4]
			if rewardId:
				self.rewardList.append(rewardId)

	def GuaJiReward(self, role, star):
		#普通怪物奖励
		rewards = []
		for index, rid in enumerate(self.rewardList):
			rewards.append(FBReward.RewardRole(role, rid, index))
		#根据星级翻牌发奖
		rewards.append(FBReward.RewardRoleByStar(role, self.rewardId, star))
		
		totalMoney = 0
		itemdict = {}
		for reward in rewards:
			if not reward:
				continue
			money, items = reward

			totalMoney += money
			for itemCoding, cnt in items:
				itemdict[itemCoding] = itemdict.get(itemCoding, 0) + cnt
		
		tips = GlobalPrompt.Reward_Tips
		if totalMoney:
			tips += GlobalPrompt.Money_Tips % totalMoney
		
		for itemcoding, cnt in itemdict.iteritems():
			tips += GlobalPrompt.Item_Tips % (itemcoding, cnt)
		IsAdd = False
		if Environment.EnvIsNA():
			if role.GetCD(EnumCD.Card_Year):
				IsAdd = True
		else:
			if role.GetCD(EnumCD.Card_HalfYear):
				IsAdd = True
		if IsAdd:
			role.Msg(2, 0, tips + GlobalPrompt.Card_GoldBuff_Tips)
		else:
			role.Msg(2, 0, tips)
		
class FBZJRewardConfig(TabFile.TabLine):
	#副本章节宝箱奖励配置表
	FilePath = FILE_FOLDER_PATH.FilePath("FBZhangJie.txt")
	def __init__(self):
		self.zjID		= int
		self.reward1 	= self.GetEvalByString
		self.reward2 	= self.GetEvalByString
	
	def FinishReward(self, role):
		#整个章节通关奖励
		tips = GlobalPrompt.Reward_Tips
		for itemCoding, cnt in self.reward1:
			role.AddItem(itemCoding, cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, cnt)
		
		role.Msg(2, 0, tips)
	
	def ThreeStarReward(self, role):
		#3星奖励
		tips = GlobalPrompt.Reward_Tips
		for itemCoding, cnt in self.reward2:
			role.AddItem(itemCoding, cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, cnt)
		role.Msg(2, 0, tips)

#副本购买额外购买次数
class FBBuyTime(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("FBAddTimes.txt")
	def __init__(self):
		self.VIPLevel		= int	#贵族等级
		self.maxAddTimes	= int 	#最大增加次数


def LoadFBConfig():
	#读取副本配置
	global FB_Config_Dict, FBZJ_Config_Dict, FBZJ_MaxFBId
	for fbcfg in FBConfig.ToClassType():
		if fbcfg.FBID in FB_Config_Dict:
			print "GE_EXC, repeat stageId in LoadFBConfigm  (%s)" % fbcfg.FBID
		
		FB_Config_Dict[fbcfg.FBID] = fbcfg
		#预处理数据
		fbcfg.PreCodingFBData()
		
		#副本章节信息预处理
		if fbcfg.zjID in FBZJ_Config_Dict:
			FBZJ_Config_Dict[fbcfg.zjID].add(fbcfg.FBID)
		else:
			FBZJ_Config_Dict[fbcfg.zjID] = set([fbcfg.FBID])
		
		FBZJ_MaxFBId[fbcfg.zjID] = max(FBZJ_MaxFBId.get(fbcfg.zjID, 0), fbcfg.FBID)

def LoadFBBuyTime():
	#读取副本购买次数配置表
	global FB_BuyAddTimeDict
	for rowItems in FBBuyTime.ToClassType():
		if rowItems.VIPLevel in FB_BuyAddTimeDict:
			print "GE_EXC, Repeat cfg value in FBBuyTime repeat vip level  (%s)" % rowItems.VIPLevel
			
		FB_BuyAddTimeDict[ rowItems.VIPLevel ] = rowItems.maxAddTimes

def LoadFBZJRewardConfig():
	#读取普通副本章节奖励基本配置表
	global FBZJRewardConfig_Dict
	for rowItems in FBZJRewardConfig.ToClassType():
		if rowItems.zjID in FBZJRewardConfig_Dict:
			print "GE_EXC, Repeat cfg value in FB repeat zjID (%s)" % rowItems.zjID
		FBZJRewardConfig_Dict[ rowItems.zjID ] = rowItems

if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		LoadFBConfig()
		LoadFBBuyTime()
		LoadFBZJRewardConfig()

