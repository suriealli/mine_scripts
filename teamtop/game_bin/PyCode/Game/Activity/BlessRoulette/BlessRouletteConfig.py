#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.BlessRoulette.BlessRouletteConfig")
#===============================================================================
# 祝福轮盘配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile
from Common.Other import EnumGameConfig

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("BlessRoulette")
	
	BLESS_CARD_REWARD_DICT = {}		#祝福轮盘奖励 {index:{cfg},}

class BlessRouletteReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("BlessRouletteReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.levelRange = self.GetEvalByString
		self.rateItems = self.GetEvalByString	#[(coding,cnt,rate,isRecord,itemIndex,_)]
	
	def pre_process(self):
		self.randomer = Random.RandomRate()
		for coding, cnt, rate, isRecord, itemIndex,_ in self.rateItems:
			self.randomer.AddRandomItem(rate, (coding,cnt,isRecord, itemIndex))
		
def GetRewardCfgByLevel(level = 1):
	'''
	根据等级 获取对应所属等级区段的奖励cfg 
	保证等级 超过最大配置等级区段情况下 取配置最大等级区段对应配置
	@param level:角色等级
	'''
	rewardCfg = None
	for _, cfg in BLESS_CARD_REWARD_DICT.iteritems():
		rewardCfg = cfg
		levelDown, levelUp = cfg.levelRange
		if level >= levelDown and level <= levelUp:
			break
		
	return rewardCfg
		
def GetSingleRandomReward(role,roleLevel = 1):
	'''
	获取单次随机奖励物品
	@param role: 
	@return: (coding,cnt，isRecord,itemIndex)
	'''
	cfg = GetRewardCfgByLevel(roleLevel)
	if not cfg:
		print "GE_EXC,BlessRouletteConfig::GetRandomReward: can not get reward config with level(%s)" % roleLevel
		return None
	
	return cfg.randomer.RandomOne()	

def GetBatchRandomReward(role):
	'''
	祝福轮盘批量随机奖励
	@return rewardList:[(coding,cnt,isRecord),...]
	'''
	rewardList = []
	roleLevel = role.GetLevel()
	for _ in xrange(EnumGameConfig.BlessRoulette_BatchDrawNum):
		coding, cnt, isRecord, itemIndex = GetSingleRandomReward(role, roleLevel)
		rewardList.append((coding, cnt, isRecord, itemIndex))
	
	return rewardList
		
def LoadBlessRouletteReward():
	global BLESS_CARD_REWARD_DICT
	for cfg in BlessRouletteReward.ToClassType():
		if cfg.rewardIndex in BLESS_CARD_REWARD_DICT:
			print "GE_EXC,repeat rewardindex(%s) in LoadBlessRouletteReward" % cfg.rewardIndex
		BLESS_CARD_REWARD_DICT[cfg.rewardIndex] = cfg
		cfg.pre_process()

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadBlessRouletteReward()