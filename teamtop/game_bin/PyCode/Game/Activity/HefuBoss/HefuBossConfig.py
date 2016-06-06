#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HefuBoss.HefuBossConfig")
#===============================================================================
# 合服boss配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	HefuBoss_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	HefuBoss_FILE_FOLDER_PATH.AppendPath("HefuBoss")
	
	HefuBossMonsterDict = {}
	HefuBossStatueDict = {}
	HefuBossStatuePosDict = {}

class HefuBossMonsterConfig(TabFile.TabLine):
	'''
	合服 boss怪物配置表
	'''
	FilePath = HefuBoss_FILE_FOLDER_PATH.FilePath("HefuBossMonster.txt")
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

class HefuBossStatueConfig(TabFile.TabLine):
	'''
	合服boss雕像配置
	'''
	FilePath = HefuBoss_FILE_FOLDER_PATH.FilePath("HefuBossStatue.txt")
	def __init__(self):
		self.career = int
		self.sex = int
		self.npctype = int
		
class HefuBossStatuePosConfig(TabFile.TabLine):
	'''
	合服boss雕像位置配置
	'''
	FilePath = HefuBoss_FILE_FOLDER_PATH.FilePath("HefuBossStatuePos.txt")
	def __init__(self):
		self.statueId = int
		self.pos = self.GetEvalByString
		self.sceneId = int

def LoadHefuBossMonsterConfig():
	global HefuBossMonsterDict
	for config in HefuBossMonsterConfig.ToClassType():
		if config.BossId in HefuBossMonsterDict:
			print "GE_EXC, repeat config.BossId(%s) in HefuBossMonsterDict" % config.BossId
		HefuBossMonsterDict[config.BossId] = config
		
def LoadHefuBossStatueConfig():
	global HefuBossStatueDict
	for config in HefuBossStatueConfig.ToClassType():
		if (config.career, config.sex) in HefuBossStatueDict:
			print "GE_EXC, repeat (config.career, config.sex)(%s,%s) in HefuBossMonsterDict" % (config.career, config.sex)
		HefuBossStatueDict[config.career, config.sex] = config.npctype

def LoadHefuBossStatuePosConfig():
	global HefuBossStatuePosDict
	for congfig in HefuBossStatuePosConfig.ToClassType():
		if congfig.statueId in HefuBossStatuePosDict:
			print "GE_EXC, repeat (congfig.statueId(%s) in HefuBossMonsterDict" % congfig.statueId
		HefuBossStatuePosDict[congfig.statueId] = congfig


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadHefuBossMonsterConfig()
		LoadHefuBossStatueConfig()
		LoadHefuBossStatuePosConfig()
