#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuBoss.KaifuBossConfig")
#===============================================================================
# 开服boss配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	KaifuBoss_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	KaifuBoss_FILE_FOLDER_PATH.AppendPath("KaifuBoss")
	
	KaifuBossMonsterDict = {}
	KaifuBossStatueDict = {}
	KaifuBossStatuePosDict = {}

class KaifuBossMonsterConfig(TabFile.TabLine):
	'''
	开服 boss怪物配置表
	'''
	FilePath = KaifuBoss_FILE_FOLDER_PATH.FilePath("KaifuBossMonster.txt")
	def __init__(self):
		self.BossId = int
		self.sceneId = int
		self.fightType = int
		self.monsterName = str
		self.monsterCampIdList = self.GetEvalByString
		self.singlereward = self.GetEvalByString
		self.timeLimit = int
		self.allreward = self.GetEvalByString
		self.allreward_vip = self.GetEvalByString

class KaifuBossStatueConfig(TabFile.TabLine):
	'''
	开服boss雕像配置
	'''
	FilePath = KaifuBoss_FILE_FOLDER_PATH.FilePath("KaifuBossStatue.txt")
	def __init__(self):
		self.career = int
		self.sex = int
		self.npctype = int
		
class KaifuBossStatuePosConfig(TabFile.TabLine):
	'''
	开服boss雕像位置配置
	'''
	FilePath = KaifuBoss_FILE_FOLDER_PATH.FilePath("KaifuBossStatuePos.txt")
	def __init__(self):
		self.statueId = int
		self.pos = self.GetEvalByString
		self.sceneId = int


def LoadKaifuBossMonsterConfig():
	global KaifuBossMonsterDict
	for config in KaifuBossMonsterConfig.ToClassType():
		if config.BossId in KaifuBossMonsterDict:
			print "GE_EXC, repeat config.BossId(%s) in KaifuBossMonsterDict" % config.BossId
		KaifuBossMonsterDict[config.BossId] = config
		
def LoadKaifuBossStatueConfig():
	global KaifuBossStatueDict
	for config in KaifuBossStatueConfig.ToClassType():
		if (config.career, config.sex) in KaifuBossStatueDict:
			print "GE_EXC, repeat (config.career, config.sex)(%s,%s) in KaifuBossMonsterDict" % (config.career, config.sex)
		KaifuBossStatueDict[config.career, config.sex] = config.npctype

def LoadKaifuBossStatuePosConfig():
	global KaifuBossStatuePosDict
	for congfig in KaifuBossStatuePosConfig.ToClassType():
		if congfig.statueId in KaifuBossStatuePosDict:
			print "GE_EXC, repeat (congfig.statueId(%s) in KaifuBossMonsterDict" % congfig.statueId
		KaifuBossStatuePosDict[congfig.statueId] = congfig


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadKaifuBossMonsterConfig()
		LoadKaifuBossStatueConfig()
		LoadKaifuBossStatuePosConfig()
