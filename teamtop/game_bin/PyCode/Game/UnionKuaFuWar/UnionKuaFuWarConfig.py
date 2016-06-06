#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.UnionKuaFuWar.UnionKuaFuWarConfig")
#===============================================================================
# 公会圣域争霸配置
#===============================================================================
import cDateTime
import DynamicPath
import Environment
from Util import Time
from Util.File import TabFile

UNION_KUAFU_WAR_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
UNION_KUAFU_WAR_FILE_FOLDER_PATH.AppendPath("UnionKuaFuWar")

if "_HasLoad" not in dir():
	TOTAL_UNION_RANK_CNT = 100				#公会总榜排行数量
	UNION_ROLE_RANK_CNT = 10				#公会个人榜排行数量
	TOTAL_ROLE_RANK_CNT = 20				#个人总榜排行数量
	
	UNION_KUAFU_WAR_ZONE = {}				#区域
	UNION_KUAFU_WAR_GATE = {}				#城门
	UNION_KUAFU_WAR_UNION_RANK = {}			#公会排行榜
	UNION_KUAFU_WAR_UNION_ROLE_RANK = {}	#公会个人排行榜
	UNION_KUAFU_WAR_TOTAL_ROLE_RANK = {}	#个人排行总榜
	UNION_KUAFU_WAR_BUFF_ZDL = {}			#buff需要的战斗力
	UNION_KUAFU_WAR_BUFF_BASE = {}			#buff基础信息
	UNION_KUAFU_WAR_GODDESS_BUFF = {}		#女神庇护buff
	
	UNION_KUAFU_WAR_ZDL_SCORE_LIST = []		#进入战场根据战斗力获得积分

def GetWeekDay():
	return Time.GetWeekDay(cDateTime.Now())

class UnionKuaFuWarZone(TabFile.TabLine):
	'''
	公会圣域争霸区域
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarZone.txt")
	def __init__(self):
		self.zoneId = int
		self.sceneId = int
		self.kaifuDay = self.GetEvalByString
		
class UnionKuaFuWarGate(TabFile.TabLine):
	'''
	公会圣域争霸城门
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarGate.txt")
	def __init__(self):
		self.gateId = int
		self.gateName = str
		self.winScore = int
		self.lostScore = int
		self.guardMCID = int
		self.gateHp = int
		self.winStreakFactor = int
		
class UnionKuaFuWarUnionRank(TabFile.TabLine):
	'''
	公会圣域争霸公会榜
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarUnionRank.txt")
	def __init__(self):
		self.zoneId = int
		self.levelRange = self.GetEvalByString
		self.rankRange = self.GetEvalByString
		self.rewardItem = self.GetEvalByString

class UnionKuaFuWarUnionRoleRank(TabFile.TabLine):
	'''
	公会圣域争霸公会个人榜
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarUnionRoleRank.txt")
	def __init__(self):
		self.zoneId = int
		self.rank = int
		self.levelRange = self.GetEvalByString
		self.needScore = int
		self.rewardMoney = int
		self.rewardItem = self.GetEvalByString
		
class UnionKuaFuWarTotalRank(TabFile.TabLine):
	'''
	公会圣域争霸个人总榜
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarTotalRank.txt")
	def __init__(self):
		self.zoneId = int
		self.rank = int
		self.levelRange = self.GetEvalByString
		self.needScore = int
		self.rewardItem = self.GetEvalByString
		self.rewardReputation = int
		self.rewardMoney = int
		
class UnionKuaFuWarZDLScore(TabFile.TabLine):
	'''
	进入战场根据战斗力获得积分
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarZDLScore.txt")
	def __init__(self):
		self.minZDL = int
		self.maxZDL = int
		self.score = int
		
class UnionKuaFuWarBuffZDL(TabFile.TabLine):
	'''
	公会圣域争霸开启Buff需要战斗力配置表
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarBuffZDL.txt")
	def __init__(self):
		self.buffId = int
		self.buffName = str
		self.buffType = int
		self.needZDL = int
		
class UnionKuaFuWarBuffBase(TabFile.TabLine):
	'''
	公会圣域争霸开启Buff基础信息配置表
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarBuffBase.txt")
	def __init__(self):
		self.buffType = int
		self.buffLevel = int
		self.maxLevel = int
		self.buffName = str
		self.pctValue = int
		self.absValue = int
		
class UnionKuaFuWarGoddessBuff(TabFile.TabLine):
	'''
	公会圣域争霸女神庇护Buff配置表
	'''
	FilePath = UNION_KUAFU_WAR_FILE_FOLDER_PATH.FilePath("UnionKuaFuWarGoddessBuff.txt")
	def __init__(self):
		self.buffLevel = int
		self.maxLevel = int
		self.buffName = str
		self.damageUpgradeRate = int
		self.damageReduceRate = int

#===============================================================================
# 读取配置表
#===============================================================================
def LoadUnionKuaFuWarZone():
	global UNION_KUAFU_WAR_ZONE
	for config in UnionKuaFuWarZone.ToClassType():
		UNION_KUAFU_WAR_ZONE[config.zoneId] = config
		
def LoadUnionKuaFuWarGate():
	global UNION_KUAFU_WAR_GATE
	for config in UnionKuaFuWarGate.ToClassType():
		UNION_KUAFU_WAR_GATE[config.gateId] = config
		
def LoadUnionKuaFuWarUnionRank():
	global UNION_KUAFU_WAR_UNION_RANK
	for config in UnionKuaFuWarUnionRank.ToClassType():
		for rank in xrange(config.rankRange[0], config.rankRange[1] + 1):
			#大于排行榜最大数量直接截断
			if rank > TOTAL_UNION_RANK_CNT + 1:
				break
			d = UNION_KUAFU_WAR_UNION_RANK.setdefault((config.zoneId, rank), {})
			for level in xrange(config.levelRange[0], config.levelRange[1] + 1):
				d[level] = config 
			
def LoadUnionKuaFuWarUnionRoleRank():
	global UNION_KUAFU_WAR_UNION_ROLE_RANK
	for config in UnionKuaFuWarUnionRoleRank.ToClassType():
		d = UNION_KUAFU_WAR_UNION_ROLE_RANK.setdefault((config.zoneId, config.rank), {})
		for level in xrange(config.levelRange[0], config.levelRange[1] + 1):
			d[level] = config 
			
def LoadUnionKuaFuWarTotalRank():
	global UNION_KUAFU_WAR_TOTAL_ROLE_RANK
	for config in UnionKuaFuWarTotalRank.ToClassType():
		d = UNION_KUAFU_WAR_TOTAL_ROLE_RANK.setdefault((config.zoneId, config.rank), {})
		for level in xrange(config.levelRange[0], config.levelRange[1] + 1):
			d[level] = config
			
def LoadUnionKuaFuWarZDLScore():
	global UNION_KUAFU_WAR_ZDL_SCORE_LIST
	for config in UnionKuaFuWarZDLScore.ToClassType():
		UNION_KUAFU_WAR_ZDL_SCORE_LIST.append(config)
		
def LoadUnionKuaFuWarBuffZDL():
	global UNION_KUAFU_WAR_BUFF_ZDL
	for config in UnionKuaFuWarBuffZDL.ToClassType():
		UNION_KUAFU_WAR_BUFF_ZDL[config.buffId] = config
		
def LoadUnionKuaFuWarBuffBase():
	global UNION_KUAFU_WAR_BUFF_BASE
	for config in UnionKuaFuWarBuffBase.ToClassType():
		UNION_KUAFU_WAR_BUFF_BASE[(config.buffType, config.buffLevel)] = config
		
def LoadUnionKuaFuWarGoddessBuff():
	global UNION_KUAFU_WAR_GODDESS_BUFF
	for config in UnionKuaFuWarGoddessBuff.ToClassType():
		UNION_KUAFU_WAR_GODDESS_BUFF[config.buffLevel] = config

#===============================================================================
# 接口
#===============================================================================
def IsTodayHasWar():
	if GetWeekDay() not in (2, 5):
		return False
	return True
		
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadUnionKuaFuWarZone()
		LoadUnionKuaFuWarGate()
		LoadUnionKuaFuWarUnionRank()
		LoadUnionKuaFuWarUnionRoleRank()
		LoadUnionKuaFuWarTotalRank()
		LoadUnionKuaFuWarZDLScore()
		LoadUnionKuaFuWarBuffZDL()
		LoadUnionKuaFuWarBuffBase()
		LoadUnionKuaFuWarGoddessBuff()
