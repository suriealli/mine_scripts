#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JJC.JJCConfig")
#===============================================================================
# 竞技场配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

JJC_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
JJC_FILE_FOLDER_PATH.AppendPath("JJC")

if "_HasLoad" not in dir():
	JJC_BUY_CNT = {}			#竞技场购买次数
	JJC_EXCHANGE = {}			#竞技场兑换
	JJC_RANK_AWARD = {}			#竞技场排名奖励{level:{rank:award}}
	JJC_RANK_REPUTATION = {}	#竞技场排名声望
	JJC_CHALLENGE_AWARD = {}	#竞技场挑战奖励
	JJC_RANK_TO_GROUP = {}		#竞技场排名对应组信息
	
class JJCBuyCnt(TabFile.TabLine):
	'''
	竞技场购买次数
	'''
	FilePath = JJC_FILE_FOLDER_PATH.FilePath("JJCBuyCnt.txt")
	def __init__(self):
		self.cnt = int
		self.cost = int
		
class JJCExchange(TabFile.TabLine):
	'''
	竞技场购买次数
	'''
	FilePath = JJC_FILE_FOLDER_PATH.FilePath("JJCExchange.txt")
	def __init__(self):
		self.level = int
		self.exchangeId = int
		self.score = int
		self.reputation = int
		self.item = self.GetEvalByString
		
class JJCRankAward(TabFile.TabLine):
	'''
	竞技场排名奖励
	'''
	FilePath = JJC_FILE_FOLDER_PATH.FilePath("JJCRankAward.txt")
	def __init__(self):
		self.level = int
		self.minRank = int
		self.maxRank = int
		self.money = int
		self.itemList = self.GetEvalByString
		self.titleId = int
		
class JJCRankReputation(TabFile.TabLine):
	'''
	竞技场排名声望奖励
	'''
	FilePath = JJC_FILE_FOLDER_PATH.FilePath("JJCRankReputation.txt")
	def __init__(self):
		self.rank = int
		self.reputation = int
		
class JJCChallengeAward(TabFile.TabLine):
	'''
	竞技场挑战奖励
	'''
	FilePath = JJC_FILE_FOLDER_PATH.FilePath("JJCChallengeAward.txt")
	def __init__(self):
		self.level = int
		self.winMoney = int
		self.lostMoney = int
		self.winMoney_fcm = int                       #胜利金币
		self.lostMoney_fcm = int                      #失败金币
		
class JJCRankToGroup(TabFile.TabLine):
	'''
	竞技场排名对应组信息
	'''
	FilePath = JJC_FILE_FOLDER_PATH.FilePath("JJCRankToGroup.txt")
	def __init__(self):
		self.rank = int
		self.groupId = int
		self.groupName = str
		self.groupRank = int
		self.canBePromoted = int
		self.promotedCanSeeRankList = self.GetEvalByString
		self.groupCanSeeRankList = self.GetEvalByString
		
def LoadJJCBuyCnt():
	global JJC_BUY_CNT
	for config in JJCBuyCnt.ToClassType():
		JJC_BUY_CNT[config.cnt] = config
		
def LoadJJCExchange():
	global JJC_EXCHANGE
	for config in JJCExchange.ToClassType():
		JJC_EXCHANGE[(config.level, config.exchangeId)] = config
		
def LoadJJCRankAward():
	global JJC_RANK_AWARD
	for config in JJCRankAward.ToClassType():
		if config.level not in JJC_RANK_AWARD:
			JJC_RANK_AWARD[config.level] = d = {}
		for rank in xrange(config.minRank, config.maxRank + 1):
			d[rank] = config
		
def LoadJJCRankReputation():
	global JJC_RANK_REPUTATION
	for config in JJCRankReputation.ToClassType():
		JJC_RANK_REPUTATION[config.rank] = config
		
def LoadJJCChallengeAward():
	global JJC_CHALLENGE_AWARD
	for config in JJCChallengeAward.ToClassType():
		JJC_CHALLENGE_AWARD[config.level] = config
		
def LoadJJCRankToGroup():
	global JJC_RANK_TO_GROUP
	for config in JJCRankToGroup.ToClassType():
		JJC_RANK_TO_GROUP[config.rank] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadJJCBuyCnt()
		LoadJJCExchange()
		LoadJJCRankAward()
		LoadJJCRankReputation()
		LoadJJCChallengeAward()
		LoadJJCRankToGroup()
		
