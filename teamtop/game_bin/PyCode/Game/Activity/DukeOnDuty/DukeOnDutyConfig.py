#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DukeOnDuty.DukeOnDutyConfig")
#===============================================================================
# 城主轮值配置
#===============================================================================

import Environment
import DynamicPath
from Util.File import TabFile
from Game.Property import PropertyEnum

if "_HasLoad" not in dir():
	DUKE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DUKE_FILE_FOLDER_PATH.AppendPath("DukeOnDuty")

	BUFF_INFO_DICT = {}			#城主buff配置（攻守都有）
	ATTACK_BUFF_INFO_DICT = {}	#连守buff
	ZDL_POINT_DICT = {}			#PVP积分配置
	CD_COST_DICT = {}			#秒CD消耗配置表
	UNION_RANK_REWARD_DICT = {}	#公会排名奖励配置
	PERSON_RANK_REWARD_DICT = {}#个人排名奖励配置
	EARNING_BUFF_DICT = {}		#收益buff配置
	BOSS_HP_DICT = {}			#boss最大血量、积分配置
	QUICK_CD_DICT = {}
	
class BuffInfo(TabFile.TabLine):
	'''
	轮值buff
	'''
	FilePath = DUKE_FILE_FOLDER_PATH.FilePath("BuffInfo.txt")
	def __init__(self):
		self.key = int
		self.pt1 = str
		self.value1 = int
		self.pt2 = str
		self.value2 = int
		self.needZDL = int

class AttackBuffInfo(TabFile.TabLine):
	'''
	连破buff
	'''
	FilePath = DUKE_FILE_FOLDER_PATH.FilePath("AttackBuffInfo.txt")
	def __init__(self):
		self.round = int
		self.pt1 = str
		self.value1 = int
		self.pt2 = str
		self.value2 = int
		self.reduced = int

class ZDLPoint(TabFile.TabLine):
	'''
	战斗力对应积分
	'''
	FilePath = DUKE_FILE_FOLDER_PATH.FilePath("ZDLPoint.txt")	
	def __init__(self):
		self.max_ZDL = int
		self.min_ZDL = int
		self.point = int

class CDCost(TabFile.TabLine):
	'''
	加速消耗
	'''
	FilePath = DUKE_FILE_FOLDER_PATH.FilePath("CDCost.txt")
	def __init__(self):
		self.times = int
		self.cost = int

class UnionRankReward(TabFile.TabLine):
	'''
	工会排名奖励
	'''
	FilePath = DUKE_FILE_FOLDER_PATH.FilePath("UnionRankReward.txt")
	def __init__(self):
		self.rewardId = int
		self.order = int
		self.awardEnum = int
		self.Minlevel = int
		self.Maxlevel = int
		self.itemId1 = int
		self.cnt1 = int
		self.itemId2 = int
		self.cnt2 = int
		self.itemId3 = int
		self.cnt3 = int
		self.itemId4 = int
		self.cnt4 = int
		self.money = int

class PersonRankReward(TabFile.TabLine):
	'''
	工会个人排行奖励
	'''
	FilePath = DUKE_FILE_FOLDER_PATH.FilePath("PersonRankReward.txt")
	def __init__(self):
		self.rewardId = int
		self.awardEnum = int
		self.level1 = self.GetEvalByString
		self.money1 = int
		self.level2 = self.GetEvalByString
		self.money2 = int
		self.level3 = self.GetEvalByString
		self.money3 = int
		self.level4 = self.GetEvalByString
		self.money4 = int
		self.level5 = self.GetEvalByString
		self.money5 = int
		self.level6 = self.GetEvalByString
		self.money6 = int
		self.level7 = self.GetEvalByString
		self.money7 = int
		self.level8 = self.GetEvalByString
		self.money8 = int
		
	def GetRewardByLevel(self, level):
		if self.level1[0] <= level <= self.level1[1]:
			return self.money1, self.awardEnum
		elif self.level2[0] <= level <= self.level2[1]:
			return self.money2, self.awardEnum
		elif self.level3[0] <= level <= self.level3[1]:
			return self.money3, self.awardEnum
		elif self.level4[0] <= level <= self.level4[1]:
			return self.money4, self.awardEnum
		elif self.level5[0] <= level <= self.level5[1]:
			return self.money5, self.awardEnum
		elif self.level6[0] <= level <= self.level6[1]:
			return self.money6, self.awardEnum
		elif self.level7[0] <= level <= self.level7[1]:
			return self.money7, self.awardEnum
		elif self.level8[0] <= level <= self.level8[1]:
			return self.money8, self.awardEnum
		return None, None
			
class EarningBuff(TabFile.TabLine):
	'''
	收益buff
	'''
	FilePath = DUKE_FILE_FOLDER_PATH.FilePath("EarningBuff.txt")
	def __init__(self):
		self.keepdays = int
		self.expbonus = int
		self.goldbonus = int
			
class BossHp(TabFile.TabLine):
	'''
	boss血量配置表
	'''
	FilePath = DUKE_FILE_FOLDER_PATH.FilePath("BossHp.txt")
	def __init__(self):
		self.kfDays = self.GetEvalByString
		self.bossHp1	= int
		self.bossHp2	= int
		self.bossHp3	= int
		self.divisor	= int
		self.minpoint	= int
		self.maxpoint	= int
		
def LoadBuffInfo():
	global BUFF_INFO_DICT
	for cfg in BuffInfo.ToClassType():
		if cfg.key in BUFF_INFO_DICT:
			print "GE_EXC,repeate key=(%s) in BuffInfo" % cfg.key
		pt1 = getattr(PropertyEnum, cfg.pt1)
		if not pt1:
			print "GE_EXC, Not find property index(%s) in BuffInfo" % cfg.pt1
		pt2 = getattr(PropertyEnum, cfg.pt2)
		if not pt2:
			print "GE_EXC, Not find property index(%s) in BuffInfo" % cfg.pt2
			
		BUFF_INFO_DICT[cfg.key] = [[pt1, cfg.value1], [pt2, cfg.value2], cfg.needZDL]

def LoadAttackBuffInfo():
	global ATTACK_BUFF_INFO_DICT
	global QUICK_CD_DICT
	for cfg in AttackBuffInfo.ToClassType():
		if cfg.round in ATTACK_BUFF_INFO_DICT:
			print "GE_EXC,repeate round(%s) in AttackBuffInfo" % cfg.round
		pt1 = getattr(PropertyEnum, cfg.pt1)
		if not pt1:
			print "GE_EXC, Not find property index(%s) in AttackBuffInfo" % cfg.pt1
		pt2 = getattr(PropertyEnum, cfg.pt2)
		if not pt2:
			print "GE_EXC, Not find property index(%s) in AttackBuffInfo" % cfg.pt2				
		ATTACK_BUFF_INFO_DICT[cfg.round] = [[pt1, cfg.value1], [pt2, cfg.value2]]
		QUICK_CD_DICT[cfg.round] = cfg

def LoadZDLPoint():
	global ZDL_POINT_DICT
	for cfg in ZDLPoint.ToClassType():
		key = (cfg.max_ZDL, cfg.min_ZDL)
		if key in ZDL_POINT_DICT:
			print "GE_EXC, repeate key(%s) in ZDLPoint" % key
		ZDL_POINT_DICT[key] = cfg

def LoadCDCost():
	global CD_COST_DICT
	for cfg in CDCost.ToClassType():
		if cfg.times in CD_COST_DICT:
			print "GE_EXC, repeate times(%s) in CDCost" % cfg.times
		CD_COST_DICT[cfg.times] = cfg

def LoadUnionRankReward():
	global UNION_RANK_REWARD_DICT
	for cfg in UnionRankReward.ToClassType():
		if cfg.order in UNION_RANK_REWARD_DICT:
			UNION_RANK_REWARD_DICT[cfg.order].append(cfg)
		else:
			UNION_RANK_REWARD_DICT[cfg.order] = [cfg]

def LoadPersonRankReward():
	global PERSON_RANK_REWARD_DICT
	for cfg in PersonRankReward.ToClassType():
		if cfg.rewardId in PERSON_RANK_REWARD_DICT:
			print "GE_EXC,repeat rewardId(%s) in PersonRankReward" % cfg.rewardId
		PERSON_RANK_REWARD_DICT[cfg.rewardId] = cfg

def LoadEarningBuff():
	global EARNING_BUFF_DICT
	for cfg in EarningBuff.ToClassType():
		if cfg.keepdays in EARNING_BUFF_DICT:
			print "GE_EXC,repeat keepdays=(%s) in EarningBuff" % cfg.keepdays
		EARNING_BUFF_DICT[cfg.keepdays] = cfg
	
def LoadBossHp():
	global BOSS_HP_DICT
	
	#保证开服天数区间连续
	cur_end = -1
	for cfg in BossHp.ToClassType():
		if cfg.kfDays[0] > cfg.kfDays[1]:
			print"GE_EXC,kfDays range conflict range(begin(%s) end(%s)) in BOSS_HP_DICT"%(cfg.kfDays[0],cfg.kfDays[1])
		if cfg.kfDays[0] - cur_end != 1:
			print "GE_EXC, kfDays range(begin(%s) end(%s)) not continuation with last item in BOSS_HP_DICT"%(cfg.kfDays[0],cfg.kfDays[1])
		cur_end = cfg.kfDays[1]
		BOSS_HP_DICT[(cfg.kfDays[0],cfg.kfDays[1])] = cfg

def GetBossHpConfig(kfday):
	global BOSS_HP_DICT
	for kfDays,config in BOSS_HP_DICT.iteritems():
		if kfday >= kfDays[0] and kfday <= kfDays[1]:
			return config

	return None

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadBuffInfo()
		LoadAttackBuffInfo()
		LoadZDLPoint()
		LoadCDCost()
		LoadUnionRankReward()
		LoadPersonRankReward()
		LoadEarningBuff()
		LoadBossHp()
	