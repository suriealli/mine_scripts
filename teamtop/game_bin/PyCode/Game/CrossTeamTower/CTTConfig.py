#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CrossTeamTower.CTTConfig")
#===============================================================================
# 虚空幻境配置
#===============================================================================
import random
import datetime
import time
import cDateTime
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Role.Data import EnumInt32, EnumInt16
from Util import Random
from Common.Other import EnumGameConfig

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("CrossTeamTower")
	
	CTeamTowerRewardConfig_Dict = {}	#奖励
	CTeamTowerLayerConfig_Dict = {}		#每层的配置
	SCENE_ID_SET = set()				#保存副本场景ID
	CTT_RANK_REWARD = {}				#排行榜奖励配置
	RANK_REWARD_KEYS = []
	CTT_STATUE_DATA = {}				#雕像
	CTT_EXCHANGE_DICT = {}				#兑换商店
	CTT_POINT_EXCHANGE = Random.RandomRate()	#幻境点兑换
	CTT_FRESH_DICT = {}					#刷新消耗
	MAX_FRESH_TIMES = 0					#记录最大的刷新次数
	ActiveTime = {}						#新春活动翻倍时间
	
	
class TeamTowerLayer(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CTeamTowerLayer.txt")
	def __init__(self):
		self.layer = int
		self.nextlayer = int
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
	
	def Preprocess(self):
		self.rewardCfgs = []
		if self.m1:
			npcType, x, y, direction, mcid, fightType, rewardId = self.m1
			rewardcfg = CTeamTowerRewardConfig_Dict.get(rewardId)
			if not rewardcfg:
				print "GE_EXC, TeamTowerLayer Preprocess error not this rewardcfg(%s)" % rewardId
			self.m1 = (npcType, x, y, direction, mcid, fightType, rewardcfg)
			self.rewardCfgs.append(rewardcfg)
		if self.m2:
			npcType, x, y, direction, mcid, fightType, rewardId = self.m2
			rewardcfg = CTeamTowerRewardConfig_Dict.get(rewardId)
			if not rewardcfg:
				print "GE_EXC, TeamTowerLayer Preprocess error not this rewardcfg(%s)" % rewardId
			self.m2 = (npcType, x, y, direction, mcid, fightType, rewardcfg)
			self.rewardCfgs.append(rewardcfg)
			
		if self.boss:
			npcType, x, y, direction, mcid, fightType, rewardId = self.boss
			rewardcfg = CTeamTowerRewardConfig_Dict.get(rewardId)
			if not rewardcfg:
				print "GE_EXC, TeamTowerLayer Preprocess error not this rewardcfg(%s)" % rewardId
			self.boss = (npcType, x, y, direction, mcid, fightType, rewardcfg)
			self.rewardCfgs.append(rewardcfg)

def LoadTeamTowerLayerConfig():
	global CTeamTowerLayerConfig_Dict
	for cfg in TeamTowerLayer.ToClassType():
		if cfg.layer in CTeamTowerLayerConfig_Dict:
			print "GE_EXC,repeat layer(%s) in LoadCrossTeamTowerLayerConfig" % cfg.layer
		CTeamTowerLayerConfig_Dict[cfg.layer] = cfg
		SCENE_ID_SET.add(cfg.scenePos[0])
		cfg.Preprocess()
		
		
class CTeamTowerReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CTeamTowerReward.txt")
	def __init__(self):
		self.rewardID = int
		self.money = self.GetEvalByString
		self.CTTpoint = self.GetEvalByString
		self.items = self.GetEvalByString
	
	def RewardCTTPoint(self, role):
		global ActiveTime
		startdate = int(time.mktime(datetime.datetime(*ActiveTime[1].beginTime).timetuple()))
		enddate = int(time.mktime(datetime.datetime(*ActiveTime[1].endTime).timetuple()))
		if startdate <= cDateTime.Seconds() <= enddate:
			maxpoint = EnumGameConfig.CTT_POINT_DAY_MAX * 2
		else :
			maxpoint = EnumGameConfig.CTT_POINT_DAY_MAX
		daypoint = role.GetI16(EnumInt16.CTTDayPoint)
		if daypoint >= maxpoint:
			return 0
		point = 0
		if self.CTTpoint:
			point = random.randint(self.CTTpoint[0], self.CTTpoint[1])
			if point:
				addpoint = min(maxpoint - daypoint, point)
				role.IncI32(EnumInt32.CTTPoint, addpoint)
				role.IncI16(EnumInt16.CTTDayPoint, addpoint)
		return point
		
	def RewardRole(self, role):
		#奖励
		if self.money:
			role.IncMoney(self.money)
		
		items = []
		if self.items:
			for itemCoding, itemCnt, rate in self.items:
				if rate > random.randint(0, 10000):
					role.AddItem(itemCoding, itemCnt)
					items.append((itemCoding, itemCnt))
		
		return (self.money, items)
	
	def GetReward(self):
		#只获取奖励，不真正发到身上
		items = []
		if self.items:
			for itemCoding, itemCnt, rate in self.items:
				if rate > random.randint(0, 10000):
					items.append((itemCoding, itemCnt))
		return (self.money, items)
	
def LoadCrossTeamTowerReward():
	global CTeamTowerRewardConfig_Dict
	for ttr in CTeamTowerReward.ToClassType():
		CTeamTowerRewardConfig_Dict[ttr.rewardID] = ttr
		
class CTTRankReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CTTRankReward.txt")
	def __init__(self):
		self.minIndex = int
		self.maxIndex = int
		self.itemReward = self.GetEvalByString
		self.titleId = int
		
class CTTStatue(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CTTStatue.txt")
	def __init__(self):
		self.career = int
		self.sex 	= int
		self.npctype= int
		
class CTTExchange(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CTTExchange.txt")
	def __init__(self):
		self.goodsId	= int
		self.needPoint	= int
		self.apperaPro	= int
		self.rewards	= self.GetEvalByString
		
class CTTFresh(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CTTFresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.costPoint = int
		
def LoadCTTFresh():
	global CTT_FRESH_DICT
	global MAX_FRESH_TIMES
	
	for cfg in CTTFresh.ToClassType():
		if cfg.refreshCnt in CTT_FRESH_DICT:
			print "GE_EXC,repeat refreshCnt(%s) in LoadCTTFresh" % cfg.refreshCnt
		CTT_FRESH_DICT[cfg.refreshCnt] = cfg.costPoint
		if MAX_FRESH_TIMES < cfg.refreshCnt:
			MAX_FRESH_TIMES = cfg.refreshCnt
		
def LoadCTTExchange():
	global CTT_POINT_EXCHANGE
	global CTT_EXCHANGE_DICT
	
	for cfg in CTTExchange.ToClassType():
		if cfg.goodsId in CTT_EXCHANGE_DICT:
			print "GE_EXC, repeat goodsId(%s) in LoadCTTExchange" % cfg.goodsId
		CTT_EXCHANGE_DICT[cfg.goodsId] = cfg
		CTT_POINT_EXCHANGE.AddRandomItem(cfg.apperaPro, cfg.goodsId)
	
def FreashGOODs():
	global CTT_POINT_EXCHANGE
	return CTT_POINT_EXCHANGE.RandomMany(9)

def LoadCTTStatue():
	global CTT_STATUE_DATA
	
	for cfg in CTTStatue.ToClassType():
		key = (cfg.career, cfg.sex)
		if key in CTT_STATUE_DATA:
			print "GE_EXC,repeat career(%s) and sex(%s) in LoadCTTStatue" % (cfg.career, cfg.sex)
		CTT_STATUE_DATA[key] = cfg
		
def LoadCTTRankReward():
	global CTT_RANK_REWARD
	global RANK_REWARD_KEYS
	for cfg in CTTRankReward.ToClassType():
		index = (cfg.minIndex, cfg.maxIndex)
		if index in CTT_RANK_REWARD:
			print "GE_EXC,repeat minIndex(%s) and maxIndex(%s) in LoadCTTRankReward" % (cfg.minIndex, cfg.maxIndex)
		CTT_RANK_REWARD[index] = cfg
		RANK_REWARD_KEYS.append(index)
		RANK_REWARD_KEYS.sort(key = lambda x:x[0], reverse = False)
			
def GetRightRankKey(index):
	global RANK_REWARD_KEYS
	for minindex, maxindex in RANK_REWARD_KEYS:
		if minindex > index or maxindex < index:
			continue
		return (minindex, maxindex)
	
	
class CTChunJieActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CTChunJieActive.txt")
	def __init__(self):
		self.activeID = int 
		self.beginTime = self.GetEvalByString
		self.endTime = self.GetEvalByString
		

def LoadCTChunJieActive():
	global ActiveTime
	for cf in CTChunJieActive.ToClassType():
		ActiveTime[cf.activeID] = cf
	

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadCrossTeamTowerReward()
		LoadTeamTowerLayerConfig()
		LoadCTTRankReward()
		LoadCTTStatue()
		LoadCTTExchange()
		LoadCTTFresh()
		LoadCTChunJieActive()