#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ChaosDivinity.ChaosDivinityConfig")
#===============================================================================
# 混沌神域配置
#===============================================================================

import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	DES_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DES_FILE_FOLDER_PATH.AppendPath("ChaosDivinity")

	ChaosDivinity_BossListDict		= {}	#基础配置
	ChaosDivinity_BossInfoDict		= {}	#怪物信息
	ChaosDivinity_PassiveSkillList 	= []	#被动技能表
	ChaosDivinity_StarRewardDict	= {}	#星级奖励
	ChaosDivinity_RankRewardDict	= {}	#排行榜奖励

	PassiveSkillRandObj = Random.RandomRate()

#混沌神域Boss配置
class ChaosDivinityBossListConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("ChaosDivinityBossList.txt")

	def __init__(self):
		self.index				= int 					#章节索引
		self.bossList 			= self.GetEvalByString 	#关卡
		self.boosCnt			= int 					#选定boss数量
		self.fightType			= int 					#战斗类型
		self.rewardItem 		= self.GetEvalByString 	#道具奖励
		self.rewardExp 			= self.GetEvalByString 	#历练值奖励

	def pre_process(self):
		if len(self.rewardExp) != self.boosCnt:
			print "GE_EXC, len(rewardExp)(%s) != boosCnt(%s) where index(%s)" % (len(self.rewardExp),self.boosCnt,self.index)
		self.random_obj = Random.RandomRate()
		for boss_id,rate in self.bossList:
			self.random_obj.AddRandomItem(rate,boss_id)

	def random_boss_list(self):
		return self.random_obj.RandomMany(self.boosCnt)

#混沌神域BossInfo配置
class ChaosDivinityBossInfoConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("ChaosDivinityBoosInfo.txt")

	def __init__(self):
		self.boosId = int 	#怪物ID
		self.campId = int 	#怪物阵营ID

#混沌神域被动技能配置
class ChaosDivinityPassiveSkillConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("ChaosDivinityPassiveSkill.txt")

	def __init__(self):
		self.skillId			= int 					#被动技能ID

#混沌神域星级奖励配置
class ChaosDivinityStarRewardConfig(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("ChaosDivinityStarReward.txt")

	def __init__(self):
		self.index				= int 					#章节索引
		
		self.needRound 			= self.GetEvalByString 	#回合数1
		self.rewardExp			= self.GetEvalByString 	#历练值
		self.seal				= self.GetEvalByString 	#印章1

#混沌神域排行奖励配置
class ChaosDivinityRankReward(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("ChaosDivinityRank.txt")

	def __init__(self):
		self.rewardId 			= int
		self.rankRange 			= self.GetEvalByString
		self.rewardItem 		= self.GetEvalByString
		self.rewardExp 			= int


def GetReward(index,killed_boss):
	'''
	获取击杀奖励
	'''
	global ChaosDivinity_BossListDict
	cfg = ChaosDivinity_BossListDict.get(index,None)

	reward = {1:[],2:0,3:0}
	if not cfg or killed_boss <= 0:
		return reward

	for index in xrange(0,killed_boss):
		reward[1].extend(cfg.rewardItem)
		reward[2] += cfg.rewardExp[index]
	return reward

def GetStar(index,fight_round):
	global ChaosDivinity_StarRewardDict
	cfg = ChaosDivinity_StarRewardDict.get(index)

	if not cfg:
		return -1

	star = -1
	for i in xrange(0,3):
		if fight_round <= cfg.needRound[i]:
			star = max(star,i)

	return star

def RewardStar(index,star):
	'''
	'''
	global ChaosDivinity_StarRewardDict
	cfg = ChaosDivinity_StarRewardDict.get(index)

	reward = {1:[],2:0,3:0}
	if not cfg:
		return reward

	if star >= 0 and star < 3:
		reward[2] += cfg.rewardExp[star]
		reward[3] += cfg.seal[star]
	return reward

def GetStarReward(index,begin_star,end_star):
	'''
	获取星级奖励
	'''
	global ChaosDivinity_StarRewardDict
	cfg = ChaosDivinity_StarRewardDict.get(index)

	reward = {1:[],2:0,3:0}
	if not cfg:
		return reward

	for i in xrange(begin_star,end_star+1):
		temp_dict = RewardStar(index,i)
		reward[1].extend(temp_dict[1])
		reward[2] += temp_dict.get(2,0)
		reward[3] += temp_dict.get(3,0)

	return reward

def GetRandomSkill(cnt):
	global PassiveSkillRandObj
	return PassiveSkillRandObj.RandomMany(cnt)

def LoadBossList():
	'''
	加载Boss列表
	'''
	global ChaosDivinity_BossListDict

	for cfg in ChaosDivinityBossListConfig.ToClassType():
		if cfg.index in ChaosDivinity_BossListDict:
			print "GE_EXC, repeat index(%s) in ChaosDivinity_BossListDict" % cfg.index
		ChaosDivinity_BossListDict[cfg.index] = cfg
		cfg.pre_process()

def LoadBossInfo():
	'''
	加载boss info
	'''
	global ChaosDivinity_BossInfoDict

	for cfg in ChaosDivinityBossInfoConfig.ToClassType():
		if cfg.boosId in ChaosDivinity_BossInfoDict:
			print "GE_EXC, repeat boosId(%s) in ChaosDivinity_BossInfoDict" % cfg.boosId
		ChaosDivinity_BossInfoDict[cfg.boosId] = cfg.campId

def LoadPassiveSkill():
	'''
	加载被动技能
	'''
	global ChaosDivinity_PassiveSkillList

	for cfg in ChaosDivinityPassiveSkillConfig.ToClassType():
		if cfg.skillId in ChaosDivinity_PassiveSkillList:
			print "GE_EXC, repeat skillId(%s) in ChaosDivinity_PassiveSkillList" % cfg.skillId
		else:
			PassiveSkillRandObj.AddRandomItem(100,cfg.skillId)
		ChaosDivinity_PassiveSkillList.append(cfg.skillId)

def LoadStarReward():
	'''
	加载星级奖励
	'''
	global ChaosDivinity_StarRewardDict

	for cfg in ChaosDivinityStarRewardConfig.ToClassType():
		if cfg.index in ChaosDivinity_StarRewardDict:
			print  "GE_EXC, repeat index(%s) in ChaosDivinity_StarRewardDict" % cfg.index
		ChaosDivinity_StarRewardDict[cfg.index] = cfg

def LoadRankReward():
	'''
	加载排行榜奖励配置
	'''
	global ChaosDivinity_RankRewardDict

	for cfg in ChaosDivinityRankReward.ToClassType():
		if cfg.rewardId in ChaosDivinity_RankRewardDict:
			print "GE_EXC, repeat rewardId(%s) in ChaosDivinity_RankRewardDict"% cfg.rewardId
		ChaosDivinity_RankRewardDict[cfg.rewardId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadBossList()
		LoadBossInfo()
		LoadPassiveSkill()
		LoadStarReward()
		LoadRankReward()