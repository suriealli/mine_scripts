#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Shenshumijing.ShenshumijingConfig")
#===============================================================================
# 神树密境配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FILE_FOLDER_PATH.AppendPath("Shenshu")
	
	ShenshuLevel_Dict = {}
	ShenshuRMBInc_Dict = {}
	ShenshuIncExp_Dict = {}
	ShenshuIncExp_Dict = {}
	
	ShenshuCaijiNpc_Dict = {}
	ShenshuCaijiNpc_Set = set()
	ShenshuCaijiPos_Set = set()
	
	ShenshuGuardNpc_Dict = {}
	ShenshuGuardNpc_Set = set()
	ShenshuGuardPos_Set = set()
	ShenshuGuardNpcRandom_Dict = {}
	
	ShenshuGuardNpcCnt_Dict = {}
	ShenshuGuardNpcCnt_List = []
	
	ShenshuUnionReward_Dict = {}
	ShenshuUnionMaxCnt = 0
	
class ShenshuLevel(TabFile.TabLine):
	FilePath = FILE_FILE_FOLDER_PATH.FilePath("ShenshuLevel.txt")
	def __init__(self):
		self.level = int
		self.needExp = int
		self.nextLevel = int
		self.lastLevel = int
	
def LoadShenshuLevel():
	global ShenshuLevel_Dict
	
	for cfg in ShenshuLevel.ToClassType():
		if cfg.level in ShenshuLevel_Dict:
			print 'GE_EXC, repeat level %s in ShenshuLevel_Dict' % cfg.level
		ShenshuLevel_Dict[cfg.level] = cfg
	
class ShenshuRMBInc(TabFile.TabLine):
	FilePath = FILE_FILE_FOLDER_PATH.FilePath("ShenshuRMBInc.txt")
	def __init__(self):
		self.incGrade = int
		self.coef = int
		self.nextGrade = int
		self.needRMB = int
	
def LoadShenshuRMBInc():
	global ShenshuRMBInc_Dict
	for cfg in ShenshuRMBInc.ToClassType():
		if cfg.incGrade in ShenshuRMBInc_Dict:
			print 'GE_EXC, repeat incGrade %s in ShenshuRMBInc_Dict' % cfg.incGrade
		ShenshuRMBInc_Dict[cfg.incGrade] = cfg
	
class ShenshuIncExp(TabFile.TabLine):
	FilePath = FILE_FILE_FOLDER_PATH.FilePath("ShenshuIncExp.txt")
	def __init__(self):
		self.roleLevel = int
		self.shenshulv_1 = int
		self.shenshulv_2 = int
		self.shenshulv_3 = int
		self.shenshulv_4 = int
		self.shenshulv_5 = int
		self.shenshulv_6 = int
		self.shenshulv_7 = int
		self.shenshulv_8 = int
		self.shenshulv_9 = int
		self.shenshulv_10 = int
		
		self.shenshulv_1_fcm = int
		self.shenshulv_2_fcm = int
		self.shenshulv_3_fcm = int
		self.shenshulv_4_fcm = int
		self.shenshulv_5_fcm = int
		self.shenshulv_6_fcm = int
		self.shenshulv_7_fcm = int
		self.shenshulv_8_fcm = int
		self.shenshulv_9_fcm = int
		self.shenshulv_10_fcm = int
		
	def ProIncExp(self):
		self.incExp = {}
		self.incExp[1] = self.shenshulv_1
		self.incExp[2] = self.shenshulv_2
		self.incExp[3] = self.shenshulv_3
		self.incExp[4] = self.shenshulv_4
		self.incExp[5] = self.shenshulv_5
		self.incExp[6] = self.shenshulv_6
		self.incExp[7] = self.shenshulv_7
		self.incExp[8] = self.shenshulv_8
		self.incExp[9] = self.shenshulv_9
		self.incExp[10] = self.shenshulv_10
		
		
		self.incExp_fcm = {}
		self.incExp_fcm[1] = self.shenshulv_1_fcm
		self.incExp_fcm[2] = self.shenshulv_2_fcm
		self.incExp_fcm[3] = self.shenshulv_3_fcm
		self.incExp_fcm[4] = self.shenshulv_4_fcm
		self.incExp_fcm[5] = self.shenshulv_5_fcm
		self.incExp_fcm[6] = self.shenshulv_6_fcm
		self.incExp_fcm[7] = self.shenshulv_7_fcm
		self.incExp_fcm[8] = self.shenshulv_8_fcm
		self.incExp_fcm[9] = self.shenshulv_9_fcm
		self.incExp_fcm[10] = self.shenshulv_10_fcm
	
def LoadShenshuIncExp():
	global ShenshuIncExp_Dict
	for cfg in ShenshuIncExp.ToClassType():
		if cfg.roleLevel in ShenshuIncExp_Dict:
			print 'GE_EXC, repeat roleLevel %s in ShenshuIncExp_Dict' % cfg.roleLevel
		cfg.ProIncExp()
		ShenshuIncExp_Dict[cfg.roleLevel] = cfg
	
class ShenshuCaijiNpc(TabFile.TabLine):
	FilePath = FILE_FILE_FOLDER_PATH.FilePath("ShenshuCaijiNpc.txt")
	def __init__(self):
		self.posIndex = int
		self.pos = eval
		self.npcType = int
		self.caijiCnt = int
		self.items = eval
		self.isRumor = int
		self.items_fcm = self.GetEvalByString         #获得物品（物品coding， 物品数量）
	
def LoadShenshuCaijiNpc():
	global ShenshuCaijiNpc_Dict, ShenshuCaijiNpc_Set
	for cfg in ShenshuCaijiNpc.ToClassType():
		if cfg.posIndex in ShenshuCaijiNpc_Dict:
			print 'GE_EXC, repeat posIndex %s in ShenshuCaijiNpc_Dict' % cfg.posIndex
		ShenshuCaijiNpc_Dict[cfg.posIndex] = cfg
		ShenshuCaijiNpc_Set.add(cfg.npcType)
		ShenshuCaijiPos_Set.add(cfg.posIndex)
	
class ShenshuGuardNpc(TabFile.TabLine):
	FilePath = FILE_FILE_FOLDER_PATH.FilePath("ShenshuGuardNpc.txt")
	def __init__(self):
		self.posIndex = int
		self.pos = eval
		self.npcType = int
		self.mcid = int
		self.exp = int
		self.items = eval
	
	def PreRandom(self):
		global ShenshuGuardNpcRandom_Dict
		if self.posIndex not in ShenshuGuardNpcRandom_Dict:
			ShenshuGuardNpcRandom_Dict[self.posIndex] = Random.RandomRate()
		
		zeroRate = 10000
		for item in self.items:
			ShenshuGuardNpcRandom_Dict[self.posIndex].AddRandomItem(item[1], item[0])
			zeroRate -= item[1]
		
		if zeroRate < 0:
			print 'GE_EXC, Shenshumijing guard npc reward rate error by posIndex %s' % self.posIndex
			return
		ShenshuGuardNpcRandom_Dict[self.posIndex].AddRandomItem(zeroRate, ())
	
def LoadShenshuGuardNpc():
	global ShenshuGuardNpc_Dict, ShenshuGuardNpc_Set, ShenshuGuardPos_Set
	for cfg in ShenshuGuardNpc.ToClassType():
		if cfg.posIndex in ShenshuGuardNpc_Dict:
			print 'GE_EXC, repeat posIndex %s in ShenshuGuardNpc_Dict' % cfg.posIndex
		cfg.PreRandom()
		ShenshuGuardNpc_Dict[cfg.posIndex] = cfg
		ShenshuGuardNpc_Set.add(cfg.npcType)
		ShenshuGuardPos_Set.add(cfg.posIndex)
	
class ShenshuGuardNpcCnt(TabFile.TabLine):
	FilePath = FILE_FILE_FOLDER_PATH.FilePath("ShenshuGuardNpcCnt.txt")
	def __init__(self):
		self.peiyangCnt = int
		self.guardCnt = int
	
def LoadShenshuGuardNpcCnt():
	global ShenshuGuardNpcCnt_Dict, ShenshuGuardNpcCnt_List
	for cfg in ShenshuGuardNpcCnt.ToClassType():
		if cfg.peiyangCnt in ShenshuGuardNpcCnt_Dict:
			print 'GE_EXC, repeat peiyangCnt %s in ShenshuGuardNpcCnt_Dict' % cfg.peiyangCnt
		ShenshuGuardNpcCnt_Dict[cfg.peiyangCnt] = cfg.guardCnt
	
	ShenshuGuardNpcCnt_List = list(set(ShenshuGuardNpcCnt_Dict.keys()))
	ShenshuGuardNpcCnt_List.sort()
	
class ShenshuUnionReward(TabFile.TabLine):
	FilePath = FILE_FILE_FOLDER_PATH.FilePath("ShenshuUnionReward.txt")
	def __init__(self):
		self.rank = int
		self.rewardItems = eval
	
def LoadShenshuUnionReward():
	global ShenshuUnionReward_Dict, ShenshuUnionMaxCnt
	
	for cfg in ShenshuUnionReward.ToClassType():
		if cfg.rank in ShenshuUnionReward_Dict:
			print 'GE_EXC, repeat rank %s in ShenshuUnionReward_Dict' % cfg.rank
		ShenshuUnionReward_Dict[cfg.rank] = cfg
	
	ShenshuUnionMaxCnt = len(ShenshuUnionReward_Dict.keys())
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadShenshuLevel()
		LoadShenshuRMBInc()
		LoadShenshuIncExp()
		LoadShenshuCaijiNpc()
		LoadShenshuGuardNpc()
		LoadShenshuGuardNpcCnt()
		LoadShenshuUnionReward()
