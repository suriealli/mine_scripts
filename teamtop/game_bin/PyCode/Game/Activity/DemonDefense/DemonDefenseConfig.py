#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DemonDefense.DemonDefenseConfig")
#===============================================================================
# 魔兽入侵配置表
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

DD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
DD_FILE_FOLDER_PATH.AppendPath("DemonDefense")

if "_HasLoad" not in dir():
	DD_DEMON_BASE = {}			#魔兽入侵基础配置
	DD_KILL_REWARD = {}			#魔兽入侵击杀奖励配置
	DD_UNION_REWARD = {}		#魔兽入侵公会奖励配置
	DD_FIGHT_REWARD = {}		#魔兽入侵战斗奖励配置
	DD_LUCKY_DRAW_BASE = {}		#魔兽入侵抽奖基础配置
	DD_LUCKY_DRAW_ODDS = []		#魔兽入侵抽奖概率列表
	DD_LUCKY_DRAW_CNT = {}		#魔兽入侵抽奖次数配置
	
class DemonBase(TabFile.TabLine):
	'''
	魔兽基础配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("DemonBase.txt")
	def __init__(self):
		self.wave = int
		self.kfDays = self.GetEvalByString
		self.bossCampId = int
		self.monsterCampId = int
		self.bossHP = int
		self.monsterHP = int

def GetDemonConfig(wave,kfDay):
	'''
	根据开服天数获取怪物难度
	'''
	global DD_DEMON_BASE
	for index,config in DD_DEMON_BASE.iteritems():
		_wave,_begin,_end = index
		if wave == _wave and (kfDay >= _begin and kfDay <= _end):
			return config
	return None

class KillReward(TabFile.TabLine):
	'''
	击杀奖励配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("KillReward.txt")
	def __init__(self):
		self.killCnt = int
		self.minLevel = int
		self.maxLevel = int
		self.rewardMoney = int
		self.rewardExp = int
		
class UnionReward(TabFile.TabLine):
	'''
	公会奖励配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("UnionReward.txt")
	def __init__(self):
		self.rank = int
		self.level = int
		self.rewardItem = self.GetEvalByString
		
class FightReward(TabFile.TabLine):
	'''
	战斗奖励配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("FightReward.txt")
	def __init__(self):
		self.level = int
		self.minRewardMoney = int
		self.maxRewardMoney = int
		self.minRewardMoney_fcm = int                 #最小金币防沉迷
		self.maxRewardMoney_fcm = int                 #最大金币防沉迷
	
class LuckyDrawBase(TabFile.TabLine):
	'''
	抽奖基础配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("LuckyDrawBase.txt")
	def __init__(self):
		self.level = int
		self.moneyBase = int
		
class LuckyDrawOdds(TabFile.TabLine):
	'''
	抽奖概率配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("LuckyDrawOdds.txt")
	def __init__(self):
		self.multiple = int
		self.odds = int
		
class LuckyDrawCnt(TabFile.TabLine):
	'''
	抽奖次数配置
	'''
	FilePath = DD_FILE_FOLDER_PATH.FilePath("LuckyDrawCnt.txt")
	def __init__(self):
		self.rank = int
		self.cnt = int
		
def LoadDemonBase():
	global DD_DEMON_BASE

	#保证开服天数唯一、连续
	#cur_end = -1
	temp_dict = {}
	for config in DemonBase.ToClassType():
		cur_end = temp_dict.get(config.wave,-1)

		if config.kfDays[0] > config.kfDays[1]:
			print "GE_EXC,kfDays conflict begin_day(%s) end_day(%s) in DD_DEMON_BASE"%(config.kfDays[0],config.kfDays[1])
		if config.kfDays[0] - cur_end != 1:
			print "GE_EXC,kfDays repeated with last item begin_day(%s) end_day(%s) in DD_DEMON_BASE"%(config.kfDays[0],config.kfDays[1])
		temp_dict[config.wave] = config.kfDays[1]

		DD_DEMON_BASE[(config.wave,config.kfDays[0],config.kfDays[1])] = config

def LoadKillReward():
	global DD_KILL_REWARD
	for config in KillReward.ToClassType():
		if config.killCnt not in DD_KILL_REWARD:
			DD_KILL_REWARD[config.killCnt] = {}
			
		d = DD_KILL_REWARD[config.killCnt]
		for level in xrange(config.minLevel, config.maxLevel + 1):
			d[level] = config
			
def LoadUnionReward():
	global DD_UNION_REWARD
	for config in UnionReward.ToClassType():
		if config.rank in DD_UNION_REWARD:
			DD_UNION_REWARD[config.rank][config.level] = config
		else:
			DD_UNION_REWARD[config.rank] = {config.level: config}
			
def LoadFightReward():
	global DD_FIGHT_REWARD
	for config in FightReward.ToClassType():
		DD_FIGHT_REWARD[config.level] = config
			
def LoadLuckyDrawBase():
	global DD_LUCKY_DRAW_BASE
	for config in LuckyDrawBase.ToClassType():
		DD_LUCKY_DRAW_BASE[config.level] = config
		
def LoadLuckyDrawOdds():
	global DD_LUCKY_DRAW_ODDS
	for config in LuckyDrawOdds.ToClassType():
		DD_LUCKY_DRAW_ODDS.append((config.odds, config.multiple))
		
def LoadLuckyDrawCnt():
	global DD_LUCKY_DRAW_CNT
	for config in LuckyDrawCnt.ToClassType():
		DD_LUCKY_DRAW_CNT[config.rank] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadDemonBase()
		LoadKillReward()
		LoadUnionReward()
		LoadFightReward()
		LoadLuckyDrawBase()
		LoadLuckyDrawOdds()
		LoadLuckyDrawCnt()
		
		
