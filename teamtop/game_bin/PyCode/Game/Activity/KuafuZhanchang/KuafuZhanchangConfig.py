#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KuafuZhanchang.KuafuZhanchangConfig")
#===============================================================================
# 注释
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("KuafuZhanchang")
	
	KFZC_TIME_BUFF_DICT = {}				#守卫时间对于buff
	KFZC_BOSS_BUFF_DICT = {}				#领主buff
	KFZC_TIME_SCORE_DICT = {}				#守卫时间对于积分
	KFZC_PERSIONAL_SCORERANK_DICT = {}		#个人排行榜奖励
	KFZC_TABLE_DICT = {}					#转盘奖励
	
class KFZCTimeBuff(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("KFZCTimeBuff.txt")
	def __init__(self):
		self.minutes = int
		self.damageupgrade = int
		self.deephurt = int

def LoadKFZCTimeBuff():
	global KFZC_TIME_BUFF_DICT
	for cfg in KFZCTimeBuff.ToClassType():
		if cfg.minutes in KFZC_TIME_BUFF_DICT:
			print "GE_EXC,repeat minutes(%s) in KFZC_TIME_BUFF_DICT" % cfg.minutes
		KFZC_TIME_BUFF_DICT[cfg.minutes] = cfg

class KFZCBossBuff(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("KFZCBossBuff.txt")
	def __init__(self):
		self.judian_type = int
		self.damageupgrade = int
		self.deephurt = int

def LoadKFZCBossBuff():
	global KFZC_BOSS_BUFF_DICT
	for cfg in KFZCBossBuff.ToClassType():
		if cfg.judian_type in KFZC_BOSS_BUFF_DICT:
			print "GE_EXC,repeat judian_type(%s) in KFZC_BOSS_BUFF_DICT" % cfg.judian_type
		KFZC_BOSS_BUFF_DICT[cfg.judian_type] = cfg
	
class KFZCTimeScore(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("KFZCTimeScore.txt")
	def __init__(self):
		self.judianType = int
		self.minutes = int
		self.score = int

def LoadKFZCTimeScore():
	global KFZC_TIME_SCORE_DICT
	for cfg in KFZCTimeScore.ToClassType():
		if (cfg.judianType, cfg.minutes) in KFZC_TIME_SCORE_DICT:
			print "GE_EXC,repeat judianType (%s) minutes(%s) in KFZC_TIME_SCORE_DICT" % (cfg.judianType, cfg.minutes)
		KFZC_TIME_SCORE_DICT[(cfg.judianType, cfg.minutes)] = cfg
	
class KFZCPersonalScoreRank(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("KFZCPersonalScoreRank.txt")
	def __init__(self):
		self.iswin = int
		self.rank = eval
		self.turnCnt = int
		self.items = eval

def LoadKFZCPersonalScoreRank():
	global KFZC_PERSIONAL_SCORERANK_DICT
	for cfg in KFZCPersonalScoreRank.ToClassType():
		if cfg.iswin not in KFZC_PERSIONAL_SCORERANK_DICT:
			KFZC_PERSIONAL_SCORERANK_DICT[cfg.iswin] = {}
		
		if cfg.rank in KFZC_PERSIONAL_SCORERANK_DICT[cfg.iswin]:
			print "GE_EXC,repeat rank(%s) in KFZC_PERSIONAL_SCORERANK_DICT[%s]" % (cfg.rank, cfg.iswin)
		KFZC_PERSIONAL_SCORERANK_DICT[cfg.iswin][cfg.rank] = cfg
	
class KFZCTable(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("KFZCTable.txt")
	def __init__(self):
		self.index = int
		self.rate = int
		self.items = eval

def LoadKFZCtable():
	global KFZC_TABLE_DICT
	
	for cfg in KFZCTable.ToClassType():
		if cfg.index in KFZC_TABLE_DICT:
			print "GE_EXC,repeat rank(%s) in KFZC_TABLE_DICT" % cfg.index
		KFZC_TABLE_DICT[cfg.index] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadKFZCBossBuff()
		LoadKFZCTimeBuff()
		LoadKFZCTimeScore()
		LoadKFZCPersonalScoreRank()
		LoadKFZCtable()
	
