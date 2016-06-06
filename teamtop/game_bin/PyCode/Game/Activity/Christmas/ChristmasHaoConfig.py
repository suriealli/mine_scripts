#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasHaoConfig")
#===============================================================================
# 圣诞嘉年华 -- 有钱就是任性配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	CHFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CHFILE_FOLDER_PATH.AppendPath("Christmas")
	
	ChristmasHaoExpReward_Dict = {}		#有钱就是任性积分奖励字典
	
	ChristmasShop_Dict = {}				#狂欢兑不停
	
class ChristmasHaoRewardConfig(TabFile.TabLine):
	FilePath = CHFILE_FOLDER_PATH.FilePath("ChristmasHaoReward.txt")
	def __init__(self):
		self.index = int
		self.rewardItems = eval
	
def LoadChristmasHaoRewardConfig():
	global ChristmasHaoExpReward_Dict
	
	for CHRC in ChristmasHaoRewardConfig.ToClassType():
		if CHRC.index in ChristmasHaoExpReward_Dict:
			print 'GE_EXC, repeat index : %s in ChristmasHaoExpReward_Dict' % CHRC.index
			continue
		ChristmasHaoExpReward_Dict[CHRC.index] = CHRC
	
class ChristmasShopConfig(TabFile.TabLine):
	FilePath = CHFILE_FOLDER_PATH.FilePath("ChristmasShop.txt")
	def __init__(self):
		self.coding = int							#物品coding
		self.needCoding = int						#需要物品coding
		self.needLevel = int						#兑换需要的角色等级
		self.needWorldLevel = int					#兑换需要的世界等级
		self.limitCnt = int							#限购个数(0-不限购)
		self.needItemCnt = int						#兑换需要的物品个数
	
def LoadChristmasShopConfig():
	global ChristmasShop_Dict
	
	for CS in ChristmasShopConfig.ToClassType():
		if CS.coding in ChristmasShop_Dict:
			print "GE_EXC, repeat coding (%s) in ChristmasShop_Dict" % CS.coding
			continue
		ChristmasShop_Dict[CS.coding] = CS
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadChristmasHaoRewardConfig()
		LoadChristmasShopConfig()
	