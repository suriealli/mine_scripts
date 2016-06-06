#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WildBoss.WildBossConfig")
#===============================================================================
# 野外寻宝配置
#===============================================================================
import Environment
from Util.File import TabFile
import DynamicPath

if "_HasLoad" not in dir():
	WB_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	WB_FILE_FOLDER_PATH.AppendPath("WildBoss")
	
	WildBossDamage_Dict = {}
	CodingToNpctype_Dict = {}		#{coding-->npcType}
	WildBossRoleStatus_Dict = {}	#{(haveBox, killCnt):roleStatus}
	WildBossScore_Dict = {}			#{(score, region_index):items}
	WildBossScore_List = []
	WildBossScoreMax = 0
	
class WildBossScore(TabFile.TabLine):
	FilePath = WB_FILE_FOLDER_PATH.FilePath("WildBossScore.txt")
	def __init__(self):
		self.minScore = int
		self.regionIndex = int
		self.items = eval
	
def LoadWildBossScore():
	global WildBossScore_Dict, WildBossScore_List, WildBossScoreMax
	for WBS in WildBossScore.ToClassType():
		if (WBS.minScore, WBS.regionIndex) in WildBossScore_Dict:
			print 'GE_EXC, repeat minScore %s, regionIndex %s in WildBossRoleStatus_Dict' % (WBS.minScore, WBS.regionIndex)
		WildBossScore_Dict[(WBS.minScore, WBS.regionIndex)] = WBS
		WildBossScore_List.append(WBS.minScore)
	WildBossScore_List = list(set(WildBossScore_List))
	WildBossScore_List.sort()
	WildBossScoreMax = WildBossScore_List[:-1]
	
class WildBossRoleStatus(TabFile.TabLine):
	FilePath = WB_FILE_FOLDER_PATH.FilePath("WildBossStatus.txt")
	def __init__(self):
		self.haveBox = int
		self.killCnt = int
		self.roleStatus = int
	
def LoadWildBossRoleStatus():
	global WildBossRoleStatus_Dict
	for WBRS in WildBossRoleStatus.ToClassType():
		if (WBRS.haveBox, WBRS.killCnt) in WildBossRoleStatus_Dict:
			print 'GE_EXC, repeat haveBox %s, killCnt %s in WildBossRoleStatus_Dict' % (WBRS.haveBox, WBRS.killCnt)
		WildBossRoleStatus_Dict[(WBRS.haveBox, WBRS.killCnt)] = WBRS.roleStatus
	
class CodingToNpctype(TabFile.TabLine):
	FilePath = WB_FILE_FOLDER_PATH.FilePath("CodingToNpctype.txt")
	def __init__(self):
		self.coding = int
		self.npcType = int
	
def LoadCodingToNpctype():
	global CodingToNpctype_Dict
	for CTN in CodingToNpctype.ToClassType():
		if CTN.coding in CodingToNpctype_Dict:
			print 'GE_EXC, repeat coding %s in CodingToNpctype_Dict' % CTN.coding
		CodingToNpctype_Dict[CTN.coding] = CTN.npcType
	
class WildBossDamageConfig(TabFile.TabLine):
	FilePath = WB_FILE_FOLDER_PATH.FilePath("WildBossDamage.txt")
	def __init__(self):
		self.rank = int					#排名
		self.region = int				#战区
		self.boxDict = eval				#宝箱
		
def LoadWildBossDamage():
	global WildBossDamage_Dict
	for WBR in WildBossDamageConfig.ToClassType():
		if WBR.region not in WildBossDamage_Dict:
			WildBossDamage_Dict[WBR.region] = {}
		WildBossDamage_Dict[WBR.region][WBR.rank] = WBR


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadWildBossDamage()
		LoadCodingToNpctype()
		LoadWildBossRoleStatus()
		LoadWildBossScore()
		
	