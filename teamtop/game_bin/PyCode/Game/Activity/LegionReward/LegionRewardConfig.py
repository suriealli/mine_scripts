#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LegionReward.LegionRewardConfig")
#===============================================================================
# 登录奖励相关配置表
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile
from Game.Role.Data import EnumObj

if '_HasLoad' not in dir():
	LEGION_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	LEGION_FILE_FOLDER_PATH.AppendPath("LegionReward")
	
	LEGION_SEVEN_REWARD = {}#七日礼包配置
	LEGION_REWARD = {} #登录奖励配置
	
class LegionSevenReward(TabFile.TabLine):
	'''
	七日登录奖励配置
	'''
	FilePath = LEGION_FILE_FOLDER_PATH.FilePath("LegionSevenReward.txt")
	def __init__(self):
		self.totalNum      = int
		self.rewards       = self.GetEvalByString
		self.addTarot      = int
		self.addHero       = int
		self.bindRMB       = int
		self.cardRewards   = self.GetEvalByString
		self.cardMoney     = int
		
class LegionReward(TabFile.TabLine):
	'''
	登录奖励
	'''
	FilePath = LEGION_FILE_FOLDER_PATH.FilePath("LegionReward.txt")
	def __init__(self):
		self.rewardId 	= int
		self.rate 		= int
		self.itemconfig = int
		self.cnt 		= int
		self.bindRMB   	= int
		
def LoadLegionSevenReward():
	global LEGION_SEVEN_REWARD
	for config in LegionSevenReward.ToClassType():
		if config.totalNum in LEGION_SEVEN_REWARD:
			print 'GE_EXC, repeat totalNum in LegionSevenReward(%s)' % config.totalNum
		LEGION_SEVEN_REWARD[config.totalNum] = config
		
def LoadLegionReward():
	global LEGION_REWARD	
	for sc in LegionReward.ToClassType():
		if sc.rewardId in LEGION_REWARD:
			print 'GE_EXC, repeat stageid= (%s) in stagescoreReward' % sc.rewardId
		LEGION_REWARD[sc.rewardId] = sc

def GetRandomOne(role):
	'''
	除去已获取的奖励，重新计算剩余物品的
	概率
	@param role:
	'''
	global LEGION_REWARD
	#获取玩家已获得列表
	dragonTreasure_obj = role.GetObj(EnumObj.LEGION_REWARD)
	getted_item = dragonTreasure_obj.get(2)	
	NEW_RANDOM = Random.RandomRate()
	for rewardId, cfg in LEGION_REWARD.iteritems():
		if rewardId not in getted_item:
			NEW_RANDOM.AddRandomItem(cfg.rate, cfg.rewardId)
	return NEW_RANDOM.RandomOne()
	
if '_HasLoad' not in dir():
	if Environment.HasLogic:
		LoadLegionSevenReward()
		LoadLegionReward()
