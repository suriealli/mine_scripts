#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FB.FBReward")
#===============================================================================
# 副本奖励表(只能用于副本)
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random, Trace
from Common.Other import EnumGameConfig
from Game.Role.Data import EnumCD
from Game.Activity import ExtendReward


if "_HasLoad" not in dir():
	#副本奖励掉落表
	FB_Reward_Dict = {}

def RewardRole(role, rewardId, param = None):
	#按照奖励ID给角色发奖励
	global FB_Reward_Dict
	sR = FB_Reward_Dict.get(rewardId)
	if not sR:
		print "GE_EXC, RewardRole error in rewardId (%s)" % rewardId
		Trace.StackWarn("RewardRole")
		return None, None
	return sR.RewardRole(role, param)

def RewardRoleByStar(role, rewardId, cnt):
	#按照星级发奖励
	global FB_Reward_Dict
	sR = FB_Reward_Dict.get(rewardId)
	if not sR:
		print "GE_EXC, RewardRoleByStar error in rewardId (%s)" % rewardId
		Trace.StackWarn("RewardRole")
		return None
	return sR.RewardRoleByStar(role, cnt)

def FlipCardReward(role, rewardId, cnt = 1):
	global FB_Reward_Dict
	sR = FB_Reward_Dict.get(rewardId)
	if not sR:
		print "GE_EXC, GetReward error in rewardId (%s)" % rewardId
		return []
	return sR.FlipCardReward(cnt)

def GetAllRewardItems(rewardId):
	global FB_Reward_Dict
	sR = FB_Reward_Dict.get(rewardId)
	if not sR:
		print "GE_EXC, GetReward error in rewardId (%s)" % rewardId
		return []
	return sR.GetAllRewardItems()


#副本奖励表
class FBReward(TabFile.TabLine):
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("FBAndEvilHoleConfig").FilePath("FBReward.txt")
	def __init__(self):
		self.reward_Id = int
		self.money = int
		
		self.rate1 = int
		self.itemcoding1 = int
		self.cnt1 = int
		self.rate2 = int
		self.itemcoding2 = int
		self.cnt2 = int
		self.rate3 = int
		self.itemcoding3 = int
		self.cnt3 = int
		self.rate4 = int
		self.itemcoding4 = int
		self.cnt4 = int
		self.rate5 = int
		self.itemcoding5 = int
		self.cnt5 = int
		self.itemcoding6 = int
		self.cnt6 = int
		self.rate6 = int
		
	def PreReward(self):
		from Game.Item import ItemConfig
		#读取配置时候预处理，检测
		self.rewardItems = []
		
		self.randomItems = Random.RandomRate()
		if self.rate1:
			self.randomItems.AddRandomItem(self.rate1, (self.itemcoding1, self.cnt1))
			if not ItemConfig.CheckItemCoding(self.itemcoding1):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemcoding1, self.reward_Id)
		if self.rate2:
			self.randomItems.AddRandomItem(self.rate2, (self.itemcoding2, self.cnt2))
			if not ItemConfig.CheckItemCoding(self.itemcoding2):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemcoding2, self.reward_Id)
		if self.rate3:
			self.randomItems.AddRandomItem(self.rate3, (self.itemcoding3, self.cnt3))
			if not ItemConfig.CheckItemCoding(self.itemcoding3):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemcoding3, self.reward_Id)
		if self.rate4:
			self.randomItems.AddRandomItem(self.rate4, (self.itemcoding4, self.cnt4))
			if not ItemConfig.CheckItemCoding(self.itemcoding4):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemcoding4, self.reward_Id)
		if self.rate5:
			self.randomItems.AddRandomItem(self.rate5, (self.itemcoding5, self.cnt5))
			if not ItemConfig.CheckItemCoding(self.itemcoding5):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemcoding5, self.reward_Id)
		if self.rate6:
			self.randomItems.AddRandomItem(self.rate6, (self.itemcoding6, self.cnt6))
			if not ItemConfig.CheckItemCoding(self.itemcoding6):
				print "GE_EXC, not this item (%s) in FBRewardID = (%s)" % (self.itemcoding6, self.reward_Id)
		
		self.rewardItems.append((self.itemcoding1, self.cnt1))
		self.rewardItems.append((self.itemcoding2, self.cnt2))
		self.rewardItems.append((self.itemcoding3, self.cnt3))
		self.rewardItems.append((self.itemcoding4, self.cnt4))
		self.rewardItems.append((self.itemcoding5, self.cnt5))
		self.rewardItems.append((self.itemcoding6, self.cnt6))
		
	def RewardRole(self, role, param = None):
		#副本杀怪奖励
		realMoney = self.money
		if realMoney:
			goldBuff = role.GetEarningGoldBuff()
			
			#各版本判断
			if Environment.EnvIsNA():
				#北美版
				if role.GetCD(EnumCD.Card_Year):
					goldBuff += EnumGameConfig.Card_YearGold
			else:
				#其他版本
				if role.GetCD(EnumCD.Card_HalfYear):
					goldBuff += EnumGameConfig.Card_HalfYearGold
					
			realMoney = int(self.money * (1 + goldBuff / 100.0))
			role.IncMoney(realMoney)
			
		itemcoding, cnt = self.randomItems.RandomOne()
		#额外奖励(可能是默写活动的奖励)
		rewardDict = ExtendReward.GetExtendReward(role, (1, param + 1))
		rewardDict[itemcoding] = rewardDict.get(itemcoding, 0) + cnt
		
		rewardList = rewardDict.items()
		for itemCoding, itemCnt in rewardList:
			role.AddItem(itemCoding, itemCnt)
		return (realMoney, rewardList)
	
	def RewardRoleByStar(self, role, star):
		#星级奖励(只有物品没有金币)
		#按照星级随机多个物品(多少星级随机多少次)
		tempList = []
		for item, cnt in self.randomItems.RandomMany(star):
			role.AddItem(item, cnt)
			tempList.append((item, cnt))
		return (0, tempList)
	
	def FlipCardReward(self, randomTimes):
		#星级奖励(只有物品没有金币)
		return self.randomItems.RandomMany(randomTimes)
	
	def GetAllRewardItems(self):
		#获取翻牌的所有可能的奖励物品
		return self.rewardItems

def LoadFBRewardConfig():
	#读取副本配置
	global FB_Reward_Dict
	for SR in FBReward.ToClassType():
		if SR.reward_Id in FB_Reward_Dict:
			print "GE_EXC, repeat id in LoadFBRewardConfig (%s)" % SR.reward_Id
			
		FB_Reward_Dict[SR.reward_Id] = SR
		#检测配置表,预处理
		SR.PreReward()

		
if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		LoadFBRewardConfig()

