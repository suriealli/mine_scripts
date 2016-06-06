#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GloryWar.GloryWarConfig")
#===============================================================================
# 荣耀之战配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	GW_NPC_Dict = {}						#npc配置
	GW_NPC_Set = set()						#npc类型集合
	GW_ZdlToScore_Dict = {}					#战斗力对应分数
	GW_ZdlToScore_Key_List = []				#排序个的GW_ZdlToScore_Dict.keys()
	GW_WLList = []							#已序世界等级列表
	GW_SSList = []							#已序积分奖励积分列表
	GW_SRList = []							#已序积分奖励等级列表
	GW_RRList = []							#已序排名奖励等级列表
	GW_URList = []							#已序公会奖励等级列表
	GW_CRList = []							#已序阵营奖励等级列表
	GW_ScoreReward_Dict = {}				#积分奖励
	GW_RankReward_Dict = {}					#排名奖励
	GW_UnionReward_Dict = {}				#公会奖励
	GW_CampReward_Dict = {}					#阵营奖励
	
	GW_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	GW_FILE_FOLDER_PATH.AppendPath("GloryWar")

class GloryWarNpcConfig(TabFile.TabLine):
	FilePath = GW_FILE_FOLDER_PATH.FilePath("GloryWarNpc.txt")
	def __init__(self):
		self.world_level = int
		self.npc_number = int
		self.npc_name = str
		self.npc_type = int
		self.next_npc_type = int
		self.mcid = int
		self.score = int
		self.reward_items = eval
		self.reward_items_fcm = self.GetEvalByString  #奖励物品防沉迷
		
class GloryWarZdlConfig(TabFile.TabLine):
	FilePath = GW_FILE_FOLDER_PATH.FilePath("GloryWarZdlToScore.txt")
	def __init__(self):
		self.zdl = int
		self.base_score = int
	
class GloryWarScoreConfig(TabFile.TabLine):
	FilePath = GW_FILE_FOLDER_PATH.FilePath("GloryWarScoreReward.txt")
	def __init__(self):
		self.score = int
		self.level = int
		self.reward_money = int
		self.reward_reputation = int
		self.reward_items = eval
	
class GloryWarRankRewardConfig(TabFile.TabLine):
	FilePath = GW_FILE_FOLDER_PATH.FilePath("GloryWarRankReward.txt")
	def __init__(self):
		self.rank = int
		self.level = int
		self.reward_items = eval
		self.reward_money = int
	
class GloryWarUnionRewardConfig(TabFile.TabLine):
	FilePath = GW_FILE_FOLDER_PATH.FilePath("GloryWarUnionReward.txt")
	def __init__(self):
		self.rank = int
		self.level = int
		self.reward_items = eval
	
class GloryWarCampRewardConfig(TabFile.TabLine):
	FilePath = GW_FILE_FOLDER_PATH.FilePath("GloryWarCampReward.txt")
	def __init__(self):
		self.is_win = int
		self.level = int
		self.reward_reputation = int
		self.reward_money = int
	
def LoadGWNC():
	global GW_NPC_Dict
	global GW_WLList
	for NC in GloryWarNpcConfig.ToClassType():
		if (NC.world_level, NC.npc_number) in GW_NPC_Dict:
			print "GE_EXC, repeat world_level (%s), npc_number (%s) in GW_NPC_Dict" % (NC.world_level, NC.npc_number)
			continue
		GW_NPC_Dict[(NC.world_level, NC.npc_number)] = NC
		GW_NPC_Set.add(NC.npc_type)
		if NC.world_level not in GW_WLList:
			GW_WLList.append(NC.world_level)
	GW_WLList.sort()
		
def LoadGWZC():
	global GW_ZdlToScore_Dict
	global GW_ZdlToScore_Key_List
	
	for ZTS in GloryWarZdlConfig.ToClassType():
		if ZTS.zdl in GW_ZdlToScore_Dict:
			print "GE_EXC, repeat zdl (%s) in GW_ZdlToScore_Dict" % ZTS.zdl
			continue
		GW_ZdlToScore_Dict[ZTS.zdl] = ZTS.base_score
		GW_ZdlToScore_Key_List.append(ZTS.zdl)
	GW_ZdlToScore_Key_List.sort()
	
def LoadGWSC():
	global GW_ScoreReward_Dict
	global GW_SRList
	global GW_SSList
	for SR in GloryWarScoreConfig.ToClassType():
		if (SR.score, SR.level) in GW_ScoreReward_Dict:
			print "GE_EXC, repeat score (%s), level (%s) in GW_ScoreReward_Dict" % (SR.score, SR.level)
			continue
		GW_ScoreReward_Dict[(SR.score, SR.level)] = SR
		if SR.level not in GW_SRList:
			GW_SRList.append(SR.level)
		if SR.score not in GW_SSList:
			GW_SSList.append(SR.score)
	GW_SRList.sort()
	GW_SSList.sort()
	
def LoadGWRRC():
	global GW_RankReward_Dict
	global GW_RRList
	for RR in GloryWarRankRewardConfig.ToClassType():
		if (RR.rank, RR.level) in GW_RankReward_Dict:
			print "GE_EXC, repeat rank (%s), level (%s) in GW_RankReward_Dict" % (RR.rank, RR.level)
			continue
		GW_RankReward_Dict[(RR.rank, RR.level)] = RR
		if RR.level not in GW_RRList:
			GW_RRList.append(RR.level)
	GW_RRList.sort()
	
def LoadGWURC():
	global GW_UnionReward_Dict
	global GW_URList
	for UR in GloryWarUnionRewardConfig.ToClassType():
		if (UR.rank, UR.level) in GW_UnionReward_Dict:
			print "GE_EXC, repeat rank (%s), level (%s) in GW_UnionReward_Dict" % (UR.rank, UR.level)
			continue
		GW_UnionReward_Dict[(UR.rank, UR.level)] = UR
		if UR.level not in GW_URList:
			GW_URList.append(UR.level)
	GW_URList.sort()
	
def LoadGWCRC():
	global GW_CampReward_Dict
	global GW_CRList
	for CR in GloryWarCampRewardConfig.ToClassType():
		if (CR.is_win, CR.level) in GW_CampReward_Dict:
			print "GE_EXC, repeat is_win (%s), level (%s) in GW_CampReward_Dict" % (CR.is_win, CR.level)
			continue
		GW_CampReward_Dict[(CR.is_win, CR.level)] = CR
		if CR.level not in GW_CRList:
			GW_CRList.append(CR.level)
	GW_CRList.sort()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGWNC()
		LoadGWZC()
		LoadGWSC()
		LoadGWRRC()
		LoadGWURC()
		LoadGWCRC()
