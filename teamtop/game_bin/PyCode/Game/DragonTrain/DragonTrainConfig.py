#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonTrain.DragonTrainConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Property import PropertyEnum

DRAGON_TRAIN_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
DRAGON_TRAIN_FILE_FOLDER_PATH.AppendPath("DragonTrain")

if "_HasLoad" not in dir():
	DRAGON_TRAIN_BASE = {}
	DRAGON_COLLECT_SOUL = {}
	DRAGON_BALL_BASE = {}
	DRAGON_EQUIPMENT = {}
	DRAGON_VEIN_BASE = {}
	DRAGON_VEIN_GRADE = {}
	DRAGON_VEIN_LEVEL = {}
	DRAGON_VEIN_BUF = {}
	DragonEquipUpgradeDict = {}
	DRAGON_SALE_DICT = {}
	
class DragonTrainBase(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	驯龙基础配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonTrainBase.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.dragonId = int
		self.grade = int
		self.gradeName = str
		self.dragonName = str
		self.oddsBase = int
		self.maxEvolveLucky = int
		self.perLuckyAddOdds = int
		self.successNeedMinLucky = int
		self.failAddLuckyRange = self.GetEvalByString
		self.evolveNeedItem = self.GetEvalByString
		
class DragonCollectSoul(TabFile.TabLine):
	'''
	聚灵配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonCollectSoul.txt")
	def __init__(self):
		self.cnt = int
		self.needRMB = int
		self.rewardSoul = int
		self.critOdds = int
		self.critTimes = int
		
class DragonBallBase(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	龙珠基础配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonBallBase.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.dragonId = int
		self.position = int
		self.grade = int
		self.needDragonSoul = int
		self.needPreBallData = self.GetEvalByString
		
class DragonEquipment(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	驯龙装备配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonEquipment.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.coding = int
		self.dragonId = int
		self.needLevel = int
		self.grade = int
		self.posType = int
		self.canActivate = int
		
class DragonEquipUpgrade(TabFile.TabLine):
	'''
	龙骸进阶配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonEquipmentUpgrade.txt")
	def __init__(self):
		self.srcType = int
		self.desType = int
		self.needLevel = int
		self.itemType1 = int
		self.cnt1 = int
		self.itemType2 = int
		self.cnt2 = int	
		self.itemType3 = int
		self.cnt3 = int

class DragonVeinBaseConfig(TabFile.TabLine):
	'''
	龙脉基础配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonVeinBase.txt")
	def __init__(self):
		self.idx = int
		self.maxLevel = int
		self.maxGrade = int
		self.veinName = str
		self.activateNeedItem = self.GetEvalByString
		self.activateNeedRoleLevel = int
		self.activateNeedPreVein = int
		
class DragonVeinGrade(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	龙脉阶级配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonVeinGrade.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.idx = int
		self.grade = int
		self.oddsBase = int
		self.maxEvolveLucky = int
		self.perLuckyAddOdds = int
		self.successNeedMinLucky = int
		self.failAddLuckyRange = self.GetEvalByString
		self.evolveNeedItem = self.GetEvalByString
		
class DragonVeinLevel(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	龙脉等级配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonVeinLevel.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.idx = int
		self.level = int
		self.oddsBase = int
		self.maxEvolveLucky = int
		self.perLuckyAddOdds = int
		self.successNeedMinLucky = int
		self.failAddLuckyRange = self.GetEvalByString
		self.evolveNeedItem = self.GetEvalByString
		
class DragonVeinBuf(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	龙脉buf(其实也就是被动技能)配置表
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonVeinBuff.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.idx = int
		self.level = int
		self.activateNeedVeinLevelSum = int
		self.activateNeedVeinGrade = int
		self.activateNeedVeinCount = int
		
class DragonEquipmentSale(TabFile.TabLine):
	'''
	部件售卖
	'''
	FilePath = DRAGON_TRAIN_FILE_FOLDER_PATH.FilePath("DragonEquipmentSale.txt")
	def __init__(self):
		self.coding = int
		self.price = int
		
def LoadDragonEquipmentSale():
	global DRAGON_SALE_DICT
	for cfg in DragonEquipmentSale.ToClassType():
		if cfg.coding in DRAGON_SALE_DICT:
			print "GE_EXC, repeat coding(%s) in LoadDragonEquipmentSale" % cfg.coding
		DRAGON_SALE_DICT[cfg.coding] = cfg
		
def LoadDragonTrainBase():
	global DRAGON_TRAIN_BASE
	for config in DragonTrainBase.ToClassType():
		config.InitProperty()
		DRAGON_TRAIN_BASE[(config.dragonId, config.grade)] = config
		
def LoadDragonCollectSoul():
	global DRAGON_COLLECT_SOUL
	for config in DragonCollectSoul.ToClassType():
		DRAGON_COLLECT_SOUL[config.cnt] = config
		
def LoadDragonBallBase():
	global DRAGON_BALL_BASE
	for config in DragonBallBase.ToClassType():
		config.InitProperty()
		DRAGON_BALL_BASE[(config.dragonId, config.position, config.grade)] = config
		
def LoadDragonEquipment():
	global DRAGON_EQUIPMENT
	for config in DragonEquipment.ToClassType():
		config.InitProperty()
		DRAGON_EQUIPMENT[config.coding] = config

def LoadDragonEquipUpgrade():
	global DragonEquipUpgradeDict
	for config in DragonEquipUpgrade.ToClassType():
		if config.srcType in DragonEquipUpgradeDict:
			print "GE_EXC, repeat config.srcType(%s) in DragonEquipUpgradeDict"
		DragonEquipUpgradeDict[config.srcType] = config

def LoadDragonVeinBase():
	global DRAGON_VEIN_BASE
	for config in DragonVeinBaseConfig.ToClassType():
		DRAGON_VEIN_BASE[config.idx] = config
		
def LoadDragonVeinGrade():
	global DRAGON_VEIN_GRADE
	for config in DragonVeinGrade.ToClassType():
		config.InitProperty()
		DRAGON_VEIN_GRADE[(config.idx, config.grade)] = config
		
def LoadDragonVeinLevel():
	global DRAGON_VEIN_LEVEL
	for config in DragonVeinLevel.ToClassType():
		config.InitProperty()
		DRAGON_VEIN_LEVEL[(config.idx, config.level)] = config
		
def LoadDragonVeinBuf():
	global DRAGON_VEIN_BUF
	for config in DragonVeinBuf.ToClassType():
		config.InitProperty()
		DRAGON_VEIN_BUF[config.idx] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadDragonTrainBase()
		LoadDragonCollectSoul()
		LoadDragonBallBase()
		LoadDragonEquipment()
		LoadDragonVeinBase()
		LoadDragonVeinGrade()
		LoadDragonVeinLevel()
		LoadDragonVeinBuf()
		LoadDragonEquipUpgrade()
		LoadDragonEquipmentSale()
