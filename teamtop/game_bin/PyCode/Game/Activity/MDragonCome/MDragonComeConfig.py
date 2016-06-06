#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.MDragonCome.MDragonComeConfig")
#===============================================================================
# 魔龙入侵配置表
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

DD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
DD_FILE_FOLDER_PATH.AppendPath("MDragonCome")

if "_HasLoad" not in dir():

	MD_BOSS_CONFIG = {}			#魔龙降临boss配置
	MD_UNION_REWARD = {}		#魔龙降临公会奖励配置
	MD_HURT_RANK = {}			#魔龙降临伤害排名奖励
	MD_HURT = {}				#魔龙降临伤害量奖励
	
class MDBoss(TabFile.TabLine):
	'''
	魔龙基础配 置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("MDBoss.txt")
	def __init__(self):
		self.index = int
		self.bossCampId = int
		
class UnionReward(TabFile.TabLine):
	'''
	公会奖励配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("UnionReward.txt")
	def __init__(self):
		self.rank = int
		self.minLevel = int
		self.maxLevel = int
		self.rewardMoney = int
		self.rewardBindRMB = int
		self.rewardExp = int
		self.rewardItem = self.GetEvalByString
		
	@classmethod
	def get_config(cls,rank,level):
		global MD_UNION_REWARD
		
		for k, cfg in MD_UNION_REWARD.iteritems():
			crank,(minLevel,MaxLevel) = k
			if crank != rank:
				continue 
			if minLevel <= level <= MaxLevel:
				return cfg
		return None
		
class HurtRankReward(TabFile.TabLine):
	'''
	伤害排名奖励配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("HurtRankReward.txt")
	def __init__(self):
		self.rank = self.GetEvalByString
		self.minLevel = int
		self.maxLevel = int
		self.rewardMoney = int
		self.rewardBindRMB = int
		self.rewardExp = int
		self.rewardItem = self.GetEvalByString
		
	@classmethod
	def get_config(cls,rank,level):
		global MD_HURT_RANK
		
		for k,cfg in MD_HURT_RANK.iteritems():
			crank,(minLevel,MaxLevel) = k
			if rank < crank[0] or rank > crank[1]:
				continue 
			if minLevel <= level <= MaxLevel:
				return cfg
		return None
		
class HurtReward(TabFile.TabLine):
	'''
	伤害量奖励配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("HurtReward.txt")
	def __init__(self):
		self.hurtRange = self.GetEvalByString
		self.minLevel = int
		self.maxLevel = int
		self.rewardMoney = int
		self.rewardBindRMB = int
		self.rewardExp = int
		self.rewardItem = self.GetEvalByString
		
	@classmethod
	def get_config(cls,hurt,level):
		global MD_HURT
		
		for k,cfg in MD_HURT.iteritems():
			churt,(minLevel,MaxLevel) = k
			
			if hurt < churt[0] or hurt > churt[1]:
				continue 
			if minLevel <= level <= MaxLevel:
				return cfg
		return None
		
def LoadBoss():
	global MD_BOSS_CONFIG
	for config in MDBoss.ToClassType():
		MD_BOSS_CONFIG[config.index] = config
			
def LoadUnionReward():
	global MD_UNION_REWARD
	for config in UnionReward.ToClassType():
		key = (config.rank, (config.minLevel, config.maxLevel))
		if key in MD_UNION_REWARD:
			print "GE_EXC,repeat rank(%s) , (minLevel(%s),maxLevel(%s)) in UnionReward" \
				%(config.rank,config.minLevel,config.maxLevel)
				
		MD_UNION_REWARD[key] = config
			
def LoadHurtRankReward():
	global MD_HURT_RANK
	
	for config in HurtRankReward.ToClassType():
		key = (config.rank, (config.minLevel, config.maxLevel))
		if key in MD_HURT_RANK:
			print "GE_EXC,repeat rank(%s) , (minLevel(%s),maxLevel(%s)) in MD_HURT_RANK" \
				%(config.rank,config.minLevel,config.maxLevel)
				
		MD_HURT_RANK[key] = config
			
def LoadHurt():
	global MD_HURT
	
	for config in HurtReward.ToClassType():
		key = (config.hurtRange, (config.minLevel, config.maxLevel))
		if key in MD_HURT:
			print "GE_EXC,repeat hurtRange(%s) , (minLevel(%s),maxLevel(%s)) in MD_HURT" \
				%(config.hurtRange,config.minLevel,config.maxLevel)
				
		MD_HURT[key] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadBoss()
		LoadUnionReward()
		LoadHurtRankReward()
		LoadHurt()
