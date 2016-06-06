#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Zuma.ZumaConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

ZUMA_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
ZUMA_FILE_FOLDER_PATH.AppendPath("Zuma")

if "_HasLoad" not in dir():
	ZUMA_BASE = {}
	ZUMA_BALL = {}
	ZUMA_SCORE = {}
	ZUMA_COLLECT = {}
	ZUMA_BALL_REWARD = {}
	ZUMA_SCORE_REWARD = {}
	ZUMA_COLLECT_ITEM = set()
	ZUMA_ROLE_RANK_REWARD = {}
	ZUMA_UNION_RANK_REWARD = {}
	
class ZumaBase(TabFile.TabLine):
	'''
	祖玛基础配置
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaBase.txt")
	def __init__(self):
		self.levelId = int
		self.ballChainLen = int
		self.shootBallCnt = int
		self.randomBallIdList = self.GetEvalByString
		self.createBallCntAndOdds = self.GetEvalByString
		self.limitTime = int
		self.needScore = int
		
	def init_random(self):
		self.randomObj = Random.RandomRate()
		for ballCnt, odds in self.createBallCntAndOdds:
			self.randomObj.AddRandomItem(odds, ballCnt)
		
class ZumaBall(TabFile.TabLine):
	'''
	祖玛球配置
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaBall.txt")
	def __init__(self):
		self.ballId = int
		self.rewardIdAndOdds = self.GetEvalByString
		
	def init_random(self):
		self.randomObj = Random.RandomRate()
		for rewardId, odds in self.rewardIdAndOdds:
			self.randomObj.AddRandomItem(odds, rewardId)
			
class ZumaScore(TabFile.TabLine):
	'''
	祖玛积分配置
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaScore.txt")
	def __init__(self):
		self.cnt = int
		self.explodeScorePerTime = int
		self.cobomScorePerTime = int
		self.totalExplodeCntScore = int
		self.totalCobomCntScore = int
		self.maxCobomScorePerExplode = int
		
class ZumaCollect(TabFile.TabLine):
	'''
	祖玛收集奖励
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaCollect.txt")
	def __init__(self):
		self.collectId = int
		self.condition = self.GetEvalByString
		self.rewardItem = self.GetEvalByString
		
class ZumaBallReward(TabFile.TabLine):
	'''
	祖玛球奖励配置
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaBallReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rewardItemAndOdds = self.GetEvalByString
		
	def init_random(self):
		self.randomObj = Random.RandomRate()
		for itemCoding, itemCnt, odds in self.rewardItemAndOdds:
			self.randomObj.AddRandomItem(odds, (itemCoding, itemCnt))
			
class ZumaScoreReward(TabFile.TabLine):
	'''
	祖玛积分奖励配置
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaScoreReward.txt")
	def __init__(self):
		self.rewardId = int
		self.score = int
		self.levelRange = self.GetEvalByString
		self.rewardItem = self.GetEvalByString
		self.bindRMB = int
		
class ZumaCollectItem(TabFile.TabLine):
	'''
	祖玛收集物品配置
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaCollectItem.txt")
	def __init__(self):
		self.collectItemCoding = int
		
class ZumaRoleRankReward(TabFile.TabLine):
	'''
	祖玛个人排行榜奖励
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaRoleRankReward.txt")
	def __init__(self):
		self.rank = int
		self.rewardItem = self.GetEvalByString
		
class ZumaUnionRankReward(TabFile.TabLine):
	'''
	祖玛公会排行榜奖励
	'''
	FilePath = ZUMA_FILE_FOLDER_PATH.FilePath("ZumaUnionRankReward.txt")
	def __init__(self):
		self.rank = int
		self.level = int
		self.rewardItem = self.GetEvalByString
		
def LoadZumaBase():
	global ZUMA_BASE
	for config in ZumaBase.ToClassType():
		config.init_random()
		ZUMA_BASE[config.levelId] = config 
		
def LoadZumaBall():
	global ZUMA_BALL
	for config in ZumaBall.ToClassType():
		config.init_random()
		ZUMA_BALL[config.ballId] = config 
		
def LoadZumaScore():
	global ZUMA_SCORE
	for config in ZumaScore.ToClassType():
		ZUMA_SCORE[config.cnt] = config 
		
def LoadZumaCollect():
	global ZUMA_COLLECT
	for config in ZumaCollect.ToClassType():
		ZUMA_COLLECT[config.collectId] = config 
		
def LoadZumaBallReward():
	global ZUMA_BALL_REWARD
	for config in ZumaBallReward.ToClassType():
		config.init_random()
		ZUMA_BALL_REWARD[config.rewardId] = config 
		
def LoadZumaScoreReward():
	global ZUMA_SCORE_REWARD
	for config in ZumaScoreReward.ToClassType():
		for level in xrange(config.levelRange[0], config.levelRange[1] + 1):
			if level not in ZUMA_SCORE_REWARD:
				ZUMA_SCORE_REWARD[level] = {}
			ZUMA_SCORE_REWARD[level][config.rewardId] = config
			
def LoadZumaCollectItem():
	global ZUMA_COLLECT_ITEM
	for config in ZumaCollectItem.ToClassType():
		ZUMA_COLLECT_ITEM.add(config.collectItemCoding)
		
def LoadZumaRoleRankReward():
	global ZUMA_ROLE_RANK_REWARD
	for config in ZumaRoleRankReward.ToClassType():
		ZUMA_ROLE_RANK_REWARD[config.rank] = config
		
def LoadZumaUnionRankReward():
	global ZUMA_UNION_RANK_REWARD
	for config in ZumaUnionRankReward.ToClassType():
		ZUMA_UNION_RANK_REWARD[(config.rank, config.level)] = config
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadZumaBase()
		LoadZumaBall()
		LoadZumaScore()
		LoadZumaCollect()
		LoadZumaBallReward()
		LoadZumaScoreReward()
		LoadZumaCollectItem()
		LoadZumaRoleRankReward()
		LoadZumaUnionRankReward()
		
		