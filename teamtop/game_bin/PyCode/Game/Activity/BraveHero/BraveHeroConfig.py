#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.BraveHero.BraveHeroConfig")
#===============================================================================
# 勇者英雄坛配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	WP_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	WP_FILE_FOLDER_PATH.AppendPath("BraveHero")
	
	#boss
	BraveHeroBoss_Dict = {}
	#购买次数
	BraveHeroBuy_Dict = {}
	#排行榜奖励
	BraveHeroRank_Dict = {}
	BraveHeroRankToIndex_Dict = {}
	#个人积分奖励
	BraveHeroScore_Dict = {}
	#个人积分等级列表(已序)
	BraveHeroScoreLevel_List = []
	#根据开服时间确定的服务器类型
	BraveHeroServerType_Dict = {}
	#英雄徽章商店
	BraveHeroShop_Dict = {}
	
class BraveHeroBuyConfig(TabFile.TabLine):
	FilePath = WP_FILE_FOLDER_PATH.FilePath("BraveHeroBuy.txt")
	def __init__(self):
		self.cnt = int					#购买次数
		self.needRMB = int				#需要的神石
	
class BraveHeroBossConfig(TabFile.TabLine):
	FilePath = WP_FILE_FOLDER_PATH.FilePath("BraveHeroBoss.txt")
	def __init__(self):
		self.index = int					#boss索引
		self.fightID = int					#boss战斗ID
		self.maxHp = int					#boss最大血量
		self.winScore = eval				#挑战获得积分[一回合, 两回合, 三回合, 四回合, 大于四回合]
		
class BraveHeroRankConfig(TabFile.TabLine):
	FilePath = WP_FILE_FOLDER_PATH.FilePath("BraveHeroRank.txt")
	def __init__(self):
		self.index = int					#排名奖励索引
		self.rankInterval = eval			#排名区间
		self.serverType = int				#服务器类型
		self.reward = eval					#奖励
	
class BraveHeroScoreConfig(TabFile.TabLine):
	FilePath = WP_FILE_FOLDER_PATH.FilePath("BraveHeroScore.txt")
	def __init__(self):
		self.index = int					#积分奖励索引
		self.level = int					#等级
		self.needScore = int				#需要的积分
		self.reward = eval					#奖励
		self.money = int					#金币奖励
	
class BraveHeroServerTypeConfig(TabFile.TabLine):
	FilePath = WP_FILE_FOLDER_PATH.FilePath("BraveHeroServerType.txt")
	def __init__(self):
		self.serverType = int						#服务器类型
		self.kaifuDay = eval						#开服天数区间
	
class BraveHeroShopConfig(TabFile.TabLine):
	FilePath = WP_FILE_FOLDER_PATH.FilePath("BraveHeroShop.txt")
	def __init__(self):
		self.coding = int							#物品coding
		self.needCoding = int						#需要物品coding
		self.needLevel = int						#兑换需要的角色等级
		self.needWorldLevel = int					#兑换需要的世界等级
		self.limitCnt = int							#限购个数(0-不限购)
		self.needItemCnt = int						#兑换需要的物品个数
		
def LoadBraveHeroBossConfig():
	global BraveHeroBoss_Dict
	
	for BHB in BraveHeroBossConfig.ToClassType():
		if BHB.index in BraveHeroBoss_Dict:
			print "GE_EXC, repeat index (%s) in BraveHeroBoss_Dict" % BHB.index
			continue
		BraveHeroBoss_Dict[BHB.index] = BHB
	
def LoadBraveHeroBuyConfig():
	global BraveHeroBuy_Dict
	
	for BHB in BraveHeroBuyConfig.ToClassType():
		if BHB.cnt in BraveHeroBuy_Dict:
			print "GE_EXC, repeat cnt (%s) in BraveHeroBuy_Dict" % BHB.cnt
			continue
		BraveHeroBuy_Dict[BHB.cnt] = BHB
	
def LoadBraveHeroRankConfig():
	global BraveHeroRank_Dict
	global BraveHeroRankToIndex_Dict
	
	for BHR in BraveHeroRankConfig.ToClassType():
		if (BHR.index, BHR.serverType) in BraveHeroRank_Dict:
			print "GE_EXC, repeat (index : %s, serverType : %s) in BraveHeroRank_Dict" % (BHR.index, BHR.serverType)
			continue
		#排名区间 -- > 排名索引
		if BHR.rankInterval not in BraveHeroRankToIndex_Dict:
			BraveHeroRankToIndex_Dict[BHR.rankInterval] = BHR.index
		BraveHeroRank_Dict[(BHR.index, BHR.serverType)] = BHR
	
def LoadBraveHeroScoreConfig():
	global BraveHeroScore_Dict
	global BraveHeroScoreLevel_List
	
	for BHS in BraveHeroScoreConfig.ToClassType():
		if (BHS.index, BHS.level) in BraveHeroScore_Dict:
			print "GE_EXC, repeat (index : %s, level : %s) in BraveHeroScore_Dict" % (BHS.index, BHS.level)
			continue
		if BHS.level not in BraveHeroScoreLevel_List:
			BraveHeroScoreLevel_List.append(BHS.level)
		BraveHeroScore_Dict[(BHS.index, BHS.level)] = BHS
	BraveHeroScoreLevel_List.sort()
	
def LoadBraveHeroSTConfig():
	global BraveHeroServerType_Dict
	
	for BHT in BraveHeroServerTypeConfig.ToClassType():
		if BHT.serverType in BraveHeroServerType_Dict:
			print "GE_EXC, repeat serverType (%s) in BraveHeroServerType_Dict" % BHT.serverType
			continue
		BraveHeroServerType_Dict[BHT.serverType] = BHT
	
def LoadBraveHeroShopConfig():
	global BraveHeroShop_Dict
	
	for BHS in BraveHeroShopConfig.ToClassType():
		if BHS.coding in BraveHeroShop_Dict:
			print "GE_EXC, repeat coding (%s) in BraveHeroShop_Dict" % BHS.coding
			continue
		BraveHeroShop_Dict[BHS.coding] = BHS
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadBraveHeroBossConfig()
		LoadBraveHeroBuyConfig()
		LoadBraveHeroRankConfig()
		LoadBraveHeroScoreConfig()
		LoadBraveHeroSTConfig()
		LoadBraveHeroShopConfig()
		
		
		