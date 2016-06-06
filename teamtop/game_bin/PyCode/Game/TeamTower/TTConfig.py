#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.TeamTower.TTConfig")
#===============================================================================
# 组队爬塔配置
#===============================================================================
import random
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Other import GlobalPrompt

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("TeamTower")

	TeamTowerConfig_Dict = {}
	TeamTowerLayerConfig_Dict = {}

	TeamTowerRewardConfig_Dict = {}

class TeamTowerBaseConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("TeamTower.txt")
	def __init__(self):
		self.index = int
		self.name = str
		self.maxLayer = int
		
		self.maxPeople = int
		
		self.needMountIDs = self.GetEvalByString
		
		self.score = self.GetEvalByString
		
		#通关星级奖励
		self.finishReward1 = self.GetEvalByString# 金币 龙灵 物品
		self.finishReward2 = self.GetEvalByString
		self.finishReward3 = self.GetEvalByString
		self.finishReward4 = self.GetEvalByString
		self.finishReward5 = self.GetEvalByString
		self.finishReward6 = self.GetEvalByString
		self.finishReward7 = self.GetEvalByString
		
		self.finishReward1_fcm = self.GetEvalByString #通关奖励SSS
		self.finishReward2_fcm = self.GetEvalByString #通关奖励SS
		self.finishReward3_fcm = self.GetEvalByString #通关奖励S
		self.finishReward4_fcm = self.GetEvalByString #通关奖励A
		self.finishReward5_fcm = self.GetEvalByString #通关奖励B
		self.finishReward6_fcm = self.GetEvalByString #通关奖励C
		self.finishReward7_fcm = self.GetEvalByString #通关奖励D
	
	def Preprocess(self):
		self.rewardDict = {1 : self.finishReward1, 2 : self.finishReward2,
							3 : self.finishReward3, 4 : self.finishReward4,
							5 : self.finishReward5, 6 : self.finishReward6,
							7 : self.finishReward7
						 }
		
	def LinkFirst(self):
		self.ttLayerFirstCfg = TeamTowerLayerConfig_Dict.get(self.index).get(1)

	def GetReward(self, role, s):
		if role == None:
			return self.rewardDict.get(s)
		
		#根据评分获取奖励
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			return {1 : self.finishReward1_fcm, 2 : self.finishReward2_fcm,
				3 : self.finishReward3_fcm, 4 : self.finishReward4_fcm,
				5 : self.finishReward5_fcm, 6 : self.finishReward6_fcm,
				7 : self.finishReward7_fcm}.get(s)
		elif yyAntiFlag == 0:
			return self.rewardDict.get(s)
		else:
			return ()
	
	def GetReward_fcm(self, s):
		#根据评分获取奖励,防沉迷
		return {1 : self.finishReward1_fcm, 2 : self.finishReward2_fcm,
				3 : self.finishReward3_fcm, 4 : self.finishReward4_fcm,
				5 : self.finishReward5_fcm, 6 : self.finishReward6_fcm,
				7 : self.finishReward7_fcm}.get(s)
	
class TeamTowerLayer(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("TeamTowerLayer.txt")
	def __init__(self):
		self.index = int
		self.layer = int
		self.name = str
		self.scenePos = self.GetEvalByString
		self.jumpRound = self.GetEvalByString
		
		self.hasFirst = int
		self.firstItems = self.GetEvalByString
		self.firstMoney = self.GetEvalByString
		self.firstRMB = self.GetEvalByString
		
		self.m1 = self.GetEvalByString
		self.m2 = self.GetEvalByString
		self.boss = self.GetEvalByString
		self.door = self.GetEvalByString
		
		self.firstItems_fcm = self.GetEvalByString    #首次通关奖励物品
		self.firstRMB_fcm = self.GetEvalByString      #首次通关奖励魔晶
	
	def Preprocess(self):
		self.rewardCfgs = []
		if self.m1:
			npcType, x, y, direction, mcid, fightType, rewardId = self.m1
			rewardcfg = TeamTowerRewardConfig_Dict.get(rewardId)
			if not rewardcfg:
				print "GE_EXC, TeamTowerLayer m1 Preprocess error not this rewardcfg(%s)" % rewardId
			self.m1 = (npcType, x, y, direction, mcid, fightType, rewardcfg)
			self.rewardCfgs.append(rewardcfg)
		if self.m2:
			npcType, x, y, direction, mcid, fightType, rewardId = self.m2
			rewardcfg = TeamTowerRewardConfig_Dict.get(rewardId)
			if not rewardcfg:
				print "GE_EXC, TeamTowerLayer m2 Preprocess error not this rewardcfg(%s)" % rewardId
			self.m2 = (npcType, x, y, direction, mcid, fightType, rewardcfg)
			self.rewardCfgs.append(rewardcfg)
			
		if self.boss:
			npcType, x, y, direction, mcid, fightType, rewardId = self.boss
			rewardcfg = TeamTowerRewardConfig_Dict.get(rewardId)
			if not rewardcfg:
				print "GE_EXC, TeamTowerLayer boss Preprocess error not this rewardcfg(%s)" % rewardId
			self.boss = (npcType, x, y, direction, mcid, fightType, rewardcfg)
			self.rewardCfgs.append(rewardcfg)
			
	def LinkNext(self, layerdict):
		self.ttLayerNextCfg = layerdict.get(self.layer + 1)
	
	def LinkRewards(self):
		#链接奖励ID和配置
		pass

class TeamTowerReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("TeamTowerReward.txt")
	def __init__(self):
		self.rewardID = int
		self.money = int
		self.soul = int
		self.items = self.GetEvalByString
		self.money_fcm = int                          #奖励金币
		self.soul_fcm = int                           #奖励龙灵
		self.items_fcm = self.GetEvalByString         #奖励物品

	def RewardRole(self, role):
		#奖励
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			_money = self.money_fcm
			_soul = self.soul_fcm
			_items = self.items_fcm
		elif yyAntiFlag == 0:
			_money = self.money
			_soul = self.soul
			_items = self.items
		else:
			_soul = _money = 0
			_items = ()
			
		if _money:
			role.IncMoney(_money)
		if _soul:
			role.IncDragonSoul(_soul)
		items = []
		if _items:
			for itemCoding, itemCnt, rate in _items:
				if rate > random.randint(0, 10000):
					role.AddItem(itemCoding, itemCnt)
					items.append((itemCoding, itemCnt))
		return (_money, _soul, items)
	
	def GetReward(self, role):
		#只获取奖励，不真正发到身上
		itemList = []
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			_money = self.money_fcm
			_soul = self.soul_fcm
			_items = self.items_fcm
		elif yyAntiFlag == 0:
			_money = self.money
			_soul = self.soul
			_items = self.items
		else:
			_money = 0
			_soul = 0
			_items = None
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		if _items:
			for itemCoding, itemCnt, rate in _items:
				if rate > random.randint(0, 10000):
					itemList.append((itemCoding, itemCnt))
		return (_money, _soul, itemList)
	
	
def LoadTeamTowerBaseConfig():
	global TeamTowerConfig_Dict
	for ttb in TeamTowerBaseConfig.ToClassType():
		TeamTowerConfig_Dict[ttb.index] = ttb
		ttb.Preprocess()

def LoadTeamTowerLayerConfig():
	global TeamTowerLayerConfig_Dict
	for ttl in TeamTowerLayer.ToClassType():
		if ttl.index not in TeamTowerLayerConfig_Dict:
			TeamTowerLayerConfig_Dict[ttl.index] = {}
		TeamTowerLayerConfig_Dict[ttl.index][ttl.layer] = ttl
		ttl.Preprocess()
		
	#连接下一层
	for layerdict in TeamTowerLayerConfig_Dict.itervalues():
		for layercfg in layerdict.itervalues():
			layercfg.LinkNext(layerdict)
			layercfg.LinkRewards()
	#链接第一层
	global TeamTowerConfig_Dict
	for baseCfg in TeamTowerConfig_Dict.itervalues():
		baseCfg.LinkFirst()


def LoadTeamTowerReward():
	global TeamTowerRewardConfig_Dict
	for ttr in TeamTowerReward.ToClassType():
		TeamTowerRewardConfig_Dict[ttr.rewardID] = ttr



if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTeamTowerReward()
		LoadTeamTowerBaseConfig()
		LoadTeamTowerLayerConfig()


