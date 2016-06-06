#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WishPool.WishPoolConfig")
#===============================================================================
# 许愿池配置
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	WP_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	WP_FILE_FOLDER_PATH.AppendPath("WishPool")
	
	WishPool_Dict = {}
	ScoreShop_Dict = {}
	
	WPRumorsSet = set()
	
class WishPoolConfig(TabFile.TabLine):
	FilePath = WP_FILE_FOLDER_PATH.FilePath("WishPoolConfig.txt")
	def __init__(self):
		self.index = int					#许愿池索引
		self.needLevel = int				#许愿需要等级
		self.needItemCoding = int			#许愿需要物品coding
		self.needCnt = int					#单次需要物品数量
		self.needUnbindRMB = int			#单次需要神石数量
		self.score = int					#单次获得积分
		self.maxCnt = int					#每日最大许愿次数(0-没有次数限制)
#		self.addGoldMirrorCnt = int			#累计次数增加金币副本次数
		
		self.reward = eval					#随机奖励(里面什么都有)
		self.extraReward = eval				#100次许愿额外奖励
		
	def InitReward(self):
		self.randomReward = Random.RandomRate()
		for (tp, coding, cnt, rate, isRumors) in self.reward:
			self.randomReward.AddRandomItem(rate, (tp, coding, cnt))
			if not isRumors:
				continue
			#加入需要传闻集合
			WPRumorsSet.add(coding)
	
class ScoreShopConfig(TabFile.TabLine):
	FilePath = WP_FILE_FOLDER_PATH.FilePath("ScoreShopConfig.txt")
	def __init__(self):
		self.coding = int								#物品coding
		self.needScore = self.GetIntByString			#兑换需要积分
		self.needUnbindRMB = self.GetIntByString		#兑换需要的神石
		self.needLevel = int							#兑换需要的等级
		self.limitCnt = int								#每日限购次数(0-不限购)
		
def LoadScoreShopConfig():
	global ScoreShop_Dict
	for SS in ScoreShopConfig.ToClassType():
		if SS.coding in ScoreShop_Dict:
			print "GE_EXC, repeat coding (%s) in ScoreShop_Dict" % SS.coding
		ScoreShop_Dict[SS.coding] = SS
	
def LoadWishPoolConfig():
	global WishPool_Dict
	for WP in WishPoolConfig.ToClassType():
		if WP.index in WishPool_Dict:
			print "GE_EXC, repeat index (%s) in WishPool_Dict" % WP.index
		WP.InitReward()
		WishPool_Dict[WP.index] = WP
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadWishPoolConfig()
		LoadScoreShopConfig()
		
	