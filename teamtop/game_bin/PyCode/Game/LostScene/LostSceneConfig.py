#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.LostScene.LostSceneConfig")
#===============================================================================
# 迷失之境配置
#===============================================================================
import DynamicPath
from Util.File import TabFile
from Util import Random
import Environment

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("LostScene")
	
	LostScenePosNpc_Dict = {}
	LostSceneNpcType_Set = set()
	LostScenePosRandom = Random.RandomRate()
	LostSceneSkillCombin_Dict = {}
	LostSceneCardsRewards_Dict = {}
	LostSceneCardsRewardsGrade_Dict = {}
	LostSceneTurnCardRMB_Dict = {}
	LostSceneSkillRoleStatus_Dict = {}
	LostSceneExchange_Dict = {}
	LostSceneChange_Dict = {}
	
class LostScenePosNpcConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LostScenePosNpc.txt")
	def __init__(self):
		self.posIndex = int
		self.pos = eval
		self.npcType = int
		
	def initRandom(self):
		global LostScenePosRandom
		#概率都是一样的
		LostScenePosRandom.AddRandomItem(1, self.posIndex)
		
def LoadLostScenePosNpcConfig():
	global LostScenePosNpc_Dict, LostSceneNpcType_Set
	for LPC in LostScenePosNpcConfig.ToClassType():
		if LPC.posIndex in LostScenePosNpc_Dict:
			print "GE_EXC,repeat posIndex(%s) in LostScenePosNpc_Dict" % LPC.posIndex
		LPC.initRandom()
		LostScenePosNpc_Dict[LPC.posIndex] = LPC
		LostSceneNpcType_Set.add(LPC.npcType)
	
class LostSceneSkillCombinConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LostSceneSkillCombin.txt")
	def __init__(self):
		self.skillCombin = int
		self.skillIdList = eval
		
def LoadLostSceneSkillCombinConfig():
	global LostSceneSkillCombin_Dict
	for LSC in LostSceneSkillCombinConfig.ToClassType():
		if LSC.skillCombin in LostSceneSkillCombin_Dict:
			print "GE_EXC,repeat skillCombin(%s) in LostSceneSkillCombin_Dict" % LSC.skillCombin
		LostSceneSkillCombin_Dict[LSC.skillCombin] = LSC.skillIdList
	
class LostSceneCardsRewardsConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LostSceneCardsRewards.txt")
	def __init__(self):
		self.rewardIndex = int
		self.rewardGrade = int
		self.rate = int
		self.rewardCoding = eval
		self.rewardSocre = int
		
def LoadLostSceneCardsRewardsConfig():
	global LostSceneCardsRewards_Dict, LostSceneCardsRewardsGrade_Dict
	
	for LSCR in LostSceneCardsRewardsConfig.ToClassType():
		if LSCR.rewardIndex in LostSceneCardsRewards_Dict:
			print "GE_EXC,repeat skillCombin(%s) in LostSceneCardsRewards_Dict" % LSCR.rewardIndex
		LostSceneCardsRewards_Dict[LSCR.rewardIndex] = LSCR
		
		if LSCR.rewardGrade not in LostSceneCardsRewardsGrade_Dict:
			LostSceneCardsRewardsGrade_Dict[LSCR.rewardGrade] = []
		LostSceneCardsRewardsGrade_Dict[LSCR.rewardGrade].append(LSCR.rewardIndex)
		
	
class LostSceneTurnCardRMBConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LostSceneTurnCardRMB.txt")
	def __init__(self):
		self.turnCnt = int
		self.needRMB = int
		
def LoadLostSceneTurnCardRMBConfig():
	global LostSceneTurnCardRMB_Dict
	
	for LSCR in LostSceneTurnCardRMBConfig.ToClassType():
		if LSCR.turnCnt in LostSceneTurnCardRMB_Dict:
			print "GE_EXC,repeat turnCnt(%s) in LostSceneTurnCardRMB_Dict" % LSCR.turnCnt
		LostSceneTurnCardRMB_Dict[LSCR.turnCnt] = LSCR
	
class LostSceneSkillConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LostSceneSkill.txt")
	def __init__(self):
		self.skillId = int
		self.roleStatus = int
	

def LoadLostSceneSkillConfig():
	global LostSceneSkillRoleStatus_Dict
	
	for LSSC in LostSceneSkillConfig.ToClassType():
		if LSSC.skillId in LostSceneSkillRoleStatus_Dict:
			print "GE_EXC,repeat skillId(%s) in LostSceneSkillRoleStatus_Dict" % LSSC.skillId
		LostSceneSkillRoleStatus_Dict[LSSC.skillId] = LSSC.roleStatus
	
class LostSceneChangeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LostSceneChange.txt")
	def __init__(self):
		self.roleStatus = int
		self.npcType = int
	
def LoadLostSceneChangeConfig():
	global LostSceneChange_Dict
	
	for LSSC in LostSceneChangeConfig.ToClassType():
		if LSSC.roleStatus in LostSceneChange_Dict:
			print "GE_EXC,repeat roleStatus(%s) in LostSceneChange_Dict" % LSSC.roleStatus
		LostSceneChange_Dict[LSSC.roleStatus] = LSSC.npcType
	
class LostSceneExchangeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LostSceneExchange.txt")
	def __init__(self):
		self.itemCoding = int
		self.needScore = int
		self.limitCnt = int
	
def LoadLostSceneExchangeConfig():
	global LostSceneExchange_Dict
	
	for LSED in LostSceneExchangeConfig.ToClassType():
		if LSED.itemCoding in LostSceneExchange_Dict:
			print "GE_EXC,repeat skillId(%s) in LostSceneExchange_Dict" % LSED.itemCoding
		LostSceneExchange_Dict[LSED.itemCoding] = LSED
	

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLostScenePosNpcConfig()
		LoadLostSceneSkillCombinConfig()
		LoadLostSceneCardsRewardsConfig()
		LoadLostSceneTurnCardRMBConfig()
		LoadLostSceneSkillConfig()
		LoadLostSceneExchangeConfig()
		LoadLostSceneChangeConfig()
