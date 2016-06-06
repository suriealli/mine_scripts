#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoldMirror.GoldMirrorConfig")
#===============================================================================
# 金币副本配置
#===============================================================================

import DynamicPath
import Environment
from Util.File import TabFile

GOLD_TYPE  = 1#金币npc
FIGHT_TYPE = 2#怪物
TP_TYPE    = 3#传送门
if "_HasLoad" not in dir():
	GOLDSTAGE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	GOLDSTAGE_FOLDER_PATH.AppendPath("GoldMirror")
	
	GOLD_STAGE_DICT = {}
	GOLD_STAGENPC_DICT = {}
	LEVEL_MAP_GOLD = {}
	GOLD_DROP_LIMIT = {}
	GoldPickLimit_Dict = {}			#拾取的金币的最大值
	
class GoldPickLimit(TabFile.TabLine):
	FilePath = GOLDSTAGE_FOLDER_PATH.FilePath("GoldPickLimit.txt")
	def __init__(self):
		self.level = int		#玩家等级
		self.maxMoney = int		#拾取的最大金币值
		self.useRMB = int		#领取需要使用的神石
		
def LoadGoldPickLimit():
	global GoldPickLimit_Dict
	
	for GPL in GoldPickLimit.ToClassType():
		if GPL.level in GoldPickLimit_Dict:
			print 'GE_EXC, repeat level %s in GoldPickLimit_Dict' % GPL.level
			continue
		GoldPickLimit_Dict[GPL.level] = GPL
	
class GoldMirror(TabFile.TabLine):
	'''
	金币副本配置表 -- 进入配置表
	'''
	FilePath = GOLDSTAGE_FOLDER_PATH.FilePath("GoldMirror.txt")
	def __init__(self):
		self.stageID    = int		#层数
		self.sceneID    = int		#场景ID
		self.posX       = int		#x坐标
		self.posY       = int		#y坐标

class GoldMirrorNpc(TabFile.TabLine):
	'''
	金币副本npc配置 -- 金币副本内的npc配置
	'''
	FilePath = GOLDSTAGE_FOLDER_PATH.FilePath("GoldMirrorNpc.txt")
	def __init__(self):
		self.npcId     = int		#npcid
		self.npctype   = int		#npc类型
		self.x         = int		#坐标
		self.y         = int
		self.direction = int
		self.rewardId  = int		#
		self.camp      = int
		self.fightType = int
		self.layerId   = int
		self.type      = int
		self.goldtype  = int
		self.click     = int
		
class LevelMapGold(TabFile.TabLine):
	'''
	玩家获取金币配置表
	'''
	FilePath = GOLDSTAGE_FOLDER_PATH.FilePath("LevelMapGold.txt")
	def __init__(self):
		self.Level  = int
		self.index1 = int
		self.gold1  = int
		self.index2 = int
		self.gold2  = int
		self.index3 = int
		self.gold3  = int
		
class GoldDropLimit(TabFile.TabLine):
	'''
	掉落金币限制
	'''
	FilePath = GOLDSTAGE_FOLDER_PATH.FilePath("GoldDropLimit.txt")
	def __init__(self):
		self.level  = int
		self.maxMoney = int
		self.coinMoney = int
		self.maxCnt = int
		self.doubleNeedRMB = int
		
		
def LoadGoldMirror():
	global GOLD_STAGE_DICT
	for config in GoldMirror.ToClassType():
		if config.stageID in GOLD_STAGE_DICT:
			print "GE_EXC, repeat stageId=(%s) in GoldMirror" % config.stageID
		GOLD_STAGE_DICT[config.stageID] = config

def LoadGoldMirrorNpc():
	global GOLD_STAGENPC_DICT
	for config in GoldMirrorNpc.ToClassType():
		if config.layerId not in GOLD_STAGENPC_DICT:
			GOLD_STAGENPC_DICT[config.layerId] = {config.npcId:config}
			#计算最大的金币数
			
		else:
			GOLD_STAGENPC_DICT[config.layerId][config.npcId] = config
		

def LoadLevelMapGold():
	global LEVEL_MAP_GOLD
	for config in LevelMapGold.ToClassType():
		if config.Level in LEVEL_MAP_GOLD:
			print "GE_EXC,repeat level=(%s) in LevelMapGold" % config.Level
		LEVEL_MAP_GOLD[config.Level] = {config.index1:config.gold1, config.index2:config.gold2, config.index3:config.gold3}

def LoadGoldDropLimit():
	global GOLD_DROP_LIMIT
	for config in GoldDropLimit.ToClassType():
		if config.level in GOLD_DROP_LIMIT:
			print "GE_EXC,repeat level=(%s) in LoadGoldDropLimit" % config.Level
		GOLD_DROP_LIMIT[config.level] = config

def GetGoldNpc(stageId):
	'''
	根据层数获取各种类型NPC配置列表
	@param stageId:
	'''
	global GOLD_STAGENPC_DICT
	npcdict = GOLD_STAGENPC_DICT.get(stageId)
	if not npcdict:
		print "GE_EXC,can not find GoldMirror by layerId=(%s)" % stageId
		return
	gold_list = []#金币
	fight_list = []#怪
	tp_list = [] #传送门
	for _, cfg in npcdict.iteritems():
		if cfg.type == GOLD_TYPE:#是金币
			gold_list.append(cfg)
		elif cfg.type == FIGHT_TYPE:#是怪
			fight_list.append(cfg)
		elif cfg.type == TP_TYPE:#是传送门
			tp_list.append(cfg)
	return gold_list, fight_list, tp_list 

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGoldMirror()
		LoadGoldMirrorNpc()
		LoadLevelMapGold()
		LoadGoldDropLimit()
		LoadGoldPickLimit()
		
