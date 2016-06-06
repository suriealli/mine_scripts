#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuTarget.KaifuTargetConfig")
#===============================================================================
# 7日目标配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("KaifuTarget")
	
	#目标{(type, index) --> ...}
	KaifuTargetConfig_Dict = {}
	#排名{(type, rank) --> ...}
	KaifuTargetRank_Dict = {}
	
	#目标{(type, index) --> ...}
	NewKaifuTargetConfig_Dict = {}
	#排名{(type, rank) --> ...}
	NewKaifuTargetRank_Dict = {}
	
class KaifuTargetConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("KaifuTarget.txt")
	def __init__(self):
		self.targetType = int
		self.targetIndex = int
		self.param = int
		self.tarot = eval
		self.item = eval
		self.bindRMB = int
		self.unbindRMB_S = int

	
class KaifuTargetRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("KaifuTargetRank.txt")
	def __init__(self):
		self.targetType = int
		self.rank = int
		self.money = int
		self.tarot = eval
		self.item = eval
		self.bindRMB = int
		self.money = int
	
def LoadKaifuTargetConfig():
	global KaifuTargetConfig_Dict
	
	for KTD in KaifuTargetConfig.ToClassType():
		if (KTD.targetType, KTD.targetIndex) in KaifuTargetConfig_Dict:
			print 'GE_EXC, repeat targetType %s, targetIndex %s in KaifuTargetConfig_Dict' % (KTD.targetType, KTD.targetIndex)
			continue
		KaifuTargetConfig_Dict[(KTD.targetType, KTD.targetIndex)] = KTD
	
def LoadKaifuTargetRankConfig():
	global KaifuTargetRank_Dict
	
	for KTR in KaifuTargetRankConfig.ToClassType():
		if (KTR.targetType, KTR.rank) in KaifuTargetRank_Dict:
			print 'GE_EXC, repeat targetType %s, rank %s in KaifuTargetRank_Dict' % (KTR.targetType, KTR.rank)
			continue
		KaifuTargetRank_Dict[(KTR.targetType, KTR.rank)] = KTR
	
class NewKaifuTargetConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("NewKaifuTarget.txt")
	def __init__(self):
		self.targetType = int
		self.targetIndex = int
		self.param = int
		self.tarot = eval
		self.item = eval
		self.bindRMB = int
		self.unbindRMB_S = int

	
class NewKaifuTargetRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("NewKaifuTargetRank.txt")
	def __init__(self):
		self.targetType = int
		self.rank = int
		self.money = int
		self.tarot = eval
		self.item = eval
		self.bindRMB = int
		self.money = int
	
def LoadNewKaifuTargetConfig():
	global NewKaifuTargetConfig_Dict
	
	for KTD in NewKaifuTargetConfig.ToClassType():
		if (KTD.targetType, KTD.targetIndex) in NewKaifuTargetConfig_Dict:
			print 'GE_EXC, repeat targetType %s, targetIndex %s in KaifuTargetConfig_Dict' % (KTD.targetType, KTD.targetIndex)
			continue
		NewKaifuTargetConfig_Dict[(KTD.targetType, KTD.targetIndex)] = KTD
	
def LoadNewKaifuTargetRankConfig():
	global NewKaifuTargetRank_Dict
	
	for KTR in NewKaifuTargetRankConfig.ToClassType():
		if (KTR.targetType, KTR.rank) in NewKaifuTargetRank_Dict:
			print 'GE_EXC, repeat targetType %s, rank %s in KaifuTargetRank_Dict' % (KTR.targetType, KTR.rank)
			continue
		NewKaifuTargetRank_Dict[(KTR.targetType, KTR.rank)] = KTR
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadKaifuTargetConfig()
		LoadKaifuTargetRankConfig()
		LoadNewKaifuTargetConfig()
		LoadNewKaifuTargetRankConfig()
		


