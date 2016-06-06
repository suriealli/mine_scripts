#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.StarGirl.StarGirlConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Game.Property import PropertyEnum
from Util import Random
from Util.File import TabFile

STAR_GIRL_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
STAR_GIRL_FILE_FOLDER_PATH.AppendPath("StarGirl")

if "_HasLoad" not in dir():
	STAR_GIRL_BASE = {}
	STAR_GIRL_LEVEL = {}
	STAR_LEVEL = {}
	STAR_LUCKY = {}
	SUPER_DIVINE = {}
	LEVEL_UP_CRIT = {}
	BUY_LOVE_CNT = {}
	POWER_PROPERTY = {}
	POWER_CONSUME = {}
	INHERIT_CONSUME = {}
	SEAL_BASE = {}
	SEAL_LEVEL = {}
	LEVEL_UP_CRIT_RANDOM_OBJ = None
	
	STARGIRL_SELL_ITEMDICT = {}
	
class StarGirlBase(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	星灵基础配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("StarGirlBase.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.girlId = int
		self.grade = int
		self.girlName = str
		self.unlockNeedStarLucky = int
		self.unlockNeedRoleLevel = int
		self.gradeMaxLevel = int
		self.unlockNeedItem = self.GetEvalByString
		self.evolveNeedItem = self.GetEvalByString
		self.activeSkill = self.GetEvalByString
		
class StarGirlLevel(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	星灵等级配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("StarGirlLevel.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.girlId = int
		self.level = int
		self.girlName = str
		self.inheritGrade = int
		self.maxLevel = int
		self.maxGrade = int
		self.levelUpMaxExp = int
		self.levelUpNeedItem = self.GetEvalByString
		
class StarLevel(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	星灵星级配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("StarLevel.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.girlId = int
		self.starLevel = int
		self.maxStarlevel = int
		self.girlName = str
		self.maxBlessValue = int
		self.successNeedMinBlessValue = int
		self.failAddBlessValue = int
		self.starLevelUpOdds = int
		self.starLevelUpNeedItem = self.GetEvalByString
		self.passiveSkill = self.GetEvalByString
		self.skill_rate = int
	
class StarLucky(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	星灵幸运升星配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("StarLuckyLevel.txt")
	def __init__(self):
		self.luckyCoding = int
		self.itemName = str
		self.addRange = self.GetEvalByString
		self.addTempBless = self.GetEvalByString
	@classmethod
	def isLucky(cls,itemId,starGirl):
		cfg = STAR_LUCKY.get(itemId)
		if cfg is None:
			return False
		if starGirl >= cfg.addRange[0] and starGirl <= cfg.addRange[1]:
			return True
		else:
			return False
	
class SuperDivine(TabFile.TabLine):
	'''
	虔诚占星配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("SuperDivine.txt")
	def __init__(self):
		self.cnt = int
		self.needRMB = int
		self.rewardStarLucky = int
		
class LevelUpCrit(TabFile.TabLine):
	'''
	升级暴击配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("LevelUpCrit.txt")
	def __init__(self):
		self.critId = int
		self.critExp = int
		self.levelUpCritOdds = int
		self.freeCntRewardItemOdds = int
		self.freeCntRewardItem = self.GetEvalByString
		
class PowerProperty(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	星灵之力属性配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("PowerProperty.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.girlId = int
		self.girlName = str
		
class PowerConsume(TabFile.TabLine):
	'''
	星灵之力属性配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("PowerConsume.txt")
	def __init__(self):
		self.powerType = int
		self.needLove = int
		self.powerTime = int
		
class BuyLoveCnt(TabFile.TabLine):
	'''
	购买爱心值次数配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("BuyLoveCnt.txt")
	def __init__(self):
		self.cnt = int
		self.needRMB = int
		
class InheritConsume(TabFile.TabLine):
	'''
	购买爱心值次数配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("InheritConsume.txt")
	def __init__(self):
		self.level = int
		self.needItem = self.GetEvalByString
		
class SealBase(TabFile.TabLine):
	'''
	刻印基础配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("SealBase.txt")
	def __init__(self):
		self.sealId = int
		self.sealName = str
		self.unlockNeedStarLevel = int
		self.unlockNeedItem = self.GetEvalByString
		
class SealLevel(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	刻印等级配置表
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("SealLevel.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.sealId = int
		self.sealLevel = int
		self.sealName = str
		self.maxLevel = int
		self.levelUpNeedExp = int
		self.levelUpNeedItem = self.GetEvalByString
		self.itemAddExp = int
		self.luckyCoding = int


class StarGirlItem(TabFile.TabLine):
	'''
	星灵解锁道具出售返回
	'''
	FilePath = STAR_GIRL_FILE_FOLDER_PATH.FilePath("StarGirlItem.txt")
	def __init__(self):
		self.coding		= int
		self.backItem	= self.GetEvalByString


def LoadStarGirlBase():
	global STAR_GIRL_BASE
	for config in StarGirlBase.ToClassType():
		config.InitProperty()
		STAR_GIRL_BASE[(config.girlId, config.grade)] = config 
		
def LoadStarGirlLevel():
	global STAR_GIRL_LEVEL
	for config in StarGirlLevel.ToClassType():
		config.InitProperty()
		STAR_GIRL_LEVEL[(config.girlId, config.level)] = config 
		
def LoadStarLevel():
	global STAR_LEVEL
	for config in StarLevel.ToClassType():
		config.InitProperty()
		STAR_LEVEL[(config.girlId, config.starLevel)] = config 
		
def LoadStarLucy():
	global STAR_LUCKY
	for config in StarLucky.ToClassType():
		STAR_LUCKY[config.luckyCoding] = config

def LoadSuperDivine():
	global SUPER_DIVINE
	for config in SuperDivine.ToClassType():
		SUPER_DIVINE[config.cnt] = config 
		
def LoadLevelUpCrit():
	global LEVEL_UP_CRIT
	global LEVEL_UP_CRIT_RANDOM_OBJ
	LEVEL_UP_CRIT_RANDOM_OBJ = Random.RandomRate()
	for config in LevelUpCrit.ToClassType():
		LEVEL_UP_CRIT[config.critId] = config 
		LEVEL_UP_CRIT_RANDOM_OBJ.AddRandomItem(config.levelUpCritOdds, config.critId)
		
def LoadBuyLoveCnt():
	global BUY_LOVE_CNT
	for config in BuyLoveCnt.ToClassType():
		BUY_LOVE_CNT[config.cnt] = config 
		
def LoadPowerProperty():
	global POWER_PROPERTY
	for config in PowerProperty.ToClassType():
		config.InitProperty()
		POWER_PROPERTY[config.girlId] = config 
		
def LoadPowerConsume():
	global POWER_CONSUME
	for config in PowerConsume.ToClassType():
		POWER_CONSUME[config.powerType] = config 
		
def LoadInheritConsume():
	global INHERIT_CONSUME
	for config in InheritConsume.ToClassType():
		INHERIT_CONSUME[config.level] = config 
		
def LoadSealBase():
	global SEAL_BASE
	for config in SealBase.ToClassType():
		SEAL_BASE[config.sealId] = config 
		
def LoadSealLevel():
	global SEAL_LEVEL
	for config in SealLevel.ToClassType():
		config.InitProperty()
		SEAL_LEVEL[(config.sealId, config.sealLevel)] = config 

def LoadStarGirlItem():
	global STARGIRL_SELL_ITEMDICT
	for config in StarGirlItem.ToClassType():
		STARGIRL_SELL_ITEMDICT[config.coding] = config.backItem


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadStarGirlBase()
		LoadStarGirlLevel()
		LoadStarLevel()
		LoadStarLucy()
		LoadSuperDivine()
		LoadLevelUpCrit()
		LoadBuyLoveCnt()
		LoadPowerProperty()
		LoadPowerConsume()
		LoadInheritConsume()
		LoadSealBase()
		LoadSealLevel()
		LoadStarGirlItem()
		
		