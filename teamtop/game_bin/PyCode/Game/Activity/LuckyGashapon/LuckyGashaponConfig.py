#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LuckyGashapon.LuckyGashaponConfig")
#===============================================================================
# 幸运扭蛋读配置 @author: Gaoshuai 2016-02-15
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("LuckyGashapon")
	
	FashionGashaponReward_Dict = {}
	FashionGashaponItem_Dict = {}
	
	MountGashapon_Dict = {}
	MountGashaponExchange_Dict = {}

class MountGashaponConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("MountGashapon.txt")
	def __init__(self):
		self.rewardType = int                         #奖励类型(1:普通奖励，2:高级奖励，3:珍惜奖励)
		self.items = self.GetEvalByString             #物品
		self.weight = int                             #抽奖权重
		self.show = int                               #是否展示物品(1:展示，0:不展示)
		self.isRumor = int                            #是否广播（广播的都记录）


def LoadMountGashaponConfig():
	global MountGashapon_Dict
	commonRewardRandom = Random.RandomRate()  # 普通奖励随机对象
	goodRewardRandom = Random.RandomRate()    # 高级奖励随机对象
	superRewardRandom = Random.RandomRate()   # 珍惜奖励随机对象
	
	for cfg in MountGashaponConfig.ToClassType():
		if cfg.rewardType == 1:    # 普通奖励
			commonRewardRandom.AddRandomItem(cfg.weight, cfg.items)
		elif cfg.rewardType == 2:  # 高级奖励
			goodRewardRandom.AddRandomItem(cfg.weight, (cfg.items, cfg.isRumor))
		elif cfg.rewardType == 3:  # 珍惜奖励
			superRewardRandom.AddRandomItem(cfg.weight, (cfg.items, cfg.isRumor))
		
		MountGashapon_Dict = {1:commonRewardRandom, 2:goodRewardRandom, 3:superRewardRandom}


class MountGashaponExchangeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("MountGashaponExchange.txt")
	def __init__(self):
		self.index = int                              #物品索引
		self.rewardItems = self.GetEvalByString       #奖励物品
		self.needItemCnt = int                        #兑换需要碎片数量
		self.needLevel = int                          #需要角色的最小等级


def LoadMountGashaponExchangeConfig():
	global MountGashaponExchange_Dict
	
	for cfg in MountGashaponExchangeConfig.ToClassType():
		if cfg.index in MountGashaponExchange_Dict:
			print "GE_EXC, Repeat index(%s) in the file MountGashaponExchange.txt" % cfg.index 
		MountGashaponExchange_Dict[cfg.index] = cfg


class FashionGashaponConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("FashionGashapon.txt")
	def __init__(self):
		self.rewardType = int              # 奖励类型(1:普通奖励，2:高级奖励，3:珍惜奖励)
		self.items = self.GetEvalByString  # 物品
		self.weight = int                  # 抽奖权重
		self.isRumor = int                 # 是否广播（广播的都记录）


def LoadFashionGashaponConfig():
	global FashionGashaponReward_Dict
	commonRewardRandom = Random.RandomRate()  # 普通奖励随机对象
	goodRewardRandom = Random.RandomRate()    # 高级奖励随机对象
	superRewardRandom = Random.RandomRate()   # 珍惜奖励随机对象
	
	for cfg in FashionGashaponConfig.ToClassType():
		if cfg.rewardType == 1:    # 普通奖励
			commonRewardRandom.AddRandomItem(cfg.weight, cfg.items)
		elif cfg.rewardType == 2:  # 高级奖励
			goodRewardRandom.AddRandomItem(cfg.weight, (cfg.items, cfg.isRumor))
		elif cfg.rewardType == 3:  # 珍惜奖励
			superRewardRandom.AddRandomItem(cfg.weight, cfg.items)
		
		FashionGashaponReward_Dict = {1:commonRewardRandom, 2:goodRewardRandom, 3:superRewardRandom}


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadFashionGashaponConfig()
		LoadMountGashaponConfig()
		LoadMountGashaponExchangeConfig()
