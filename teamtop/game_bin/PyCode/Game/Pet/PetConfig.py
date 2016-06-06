#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Pet.PetConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile
from Game.Property import PropertyEnum

PET_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
PET_FILE_FOLDER_PATH.AppendPath("Pet")

if "_HasLoad" not in dir():
	PET_BASE = {}				#宠物基础配置
	PET_INIT_PROPERTY = {}		#宠物初始属性配置
	PET_TRAIN_PROPERTY = {}		#宠物训练属性配置
	PET_MAX_PROPERTY = {}		#宠物最大属性配置
	PET_SOUL_BASE = {}			#宠物之灵基础配置
	PET_LUCKY_DRAW = {}			#宠物转转乐配置
	
	PET_SOUL_SALE_RETURN = {}		#宠物之灵需要出售返还的物品字典
	
	PET_EVOLUTION_DICT = {}		#宠物进化配置表
	PET_ITEM_LUCK_DICT = {}		#宠物进化幸运果实

	LUCKY_DRAW_RANDOM = Random.RandomRate()	#宠物转转乐随机对象
	
	#1：攻击(有两种，需要特殊判断)  2：生命  3：暴击 4：免暴 5：破档 6：格挡
	PET_SOUL_POS_TO_PROPERTY_ENUM = {2: PropertyEnum.maxhp, 3: PropertyEnum.crit, 
									4: PropertyEnum.critpress, 5: PropertyEnum.puncture, 
									6: PropertyEnum.parry}
	
class PetBase(TabFile.TabLine):
	'''
	宠物基础配置
	'''
	FilePath = PET_FILE_FOLDER_PATH.FilePath("PetBase.txt")
	def __init__(self):
		self.petType = int
		self.starLevel = int
		self.maxStarLevel = int
		self.initLucky = int
		self.addLucky = int
		self.trainNeedRMB = int
		self.trainNeedItemCoding = int
		
class PetInitProperty(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	宠物初始属性配置
	'''
	FilePath = PET_FILE_FOLDER_PATH.FilePath("PetInitProperty.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.petType = int
		self.name	 = str
		
class PetTrainProperty(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	宠物训练属性配置
	'''
	FilePath = PET_FILE_FOLDER_PATH.FilePath("PetTrainProperty.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.petType = int
		
class PetMaxProperty(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	宠物最大属性配置
	'''
	FilePath = PET_FILE_FOLDER_PATH.FilePath("PetMaxProperty.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.petType = int
		self.starLevel = int
		
class PetSoulBase(TabFile.TabLine):
	'''
	宠物之灵基础配置
	'''
	FilePath = PET_FILE_FOLDER_PATH.FilePath("PetSoulBase.txt")
	def __init__(self):
		self.petSoulCoding = int
		self.position = int
		self.propertyPercentage = int
		self.nextLevelCoding = int
		self.upgradeNeedItemList = self.GetEvalByString
		self.saleReturn = self.GetEvalByString
		
class PetLuckyDraw(TabFile.TabLine):
	'''
	宠物转转乐配置
	'''
	FilePath = PET_FILE_FOLDER_PATH.FilePath("PetLuckyDraw.txt")
	def __init__(self):
		self.rewardId = int
		self.rate = int
		self.itemCoding = int
		self.cnt = int

class PetEvolution(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	宠物进化配置表
	'''
	FilePath = PET_FILE_FOLDER_PATH.FilePath("PetEvolution.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.petType	= int
		self.evoId		= int
		self.shapeId	= int
		self.nextshapeId= int
		self.petStar	= int
		self.nextEvoId	= int
		self.sucRate	= int
		self.addRate	= int
		self.maxRate	= int
		self.addExp		= int
		self.maxExp		= int
		self.unBindRMB	= int

class PetItemLuck(TabFile.TabLine):
	'''
	宠物幸运过
	'''
	FilePath = PET_FILE_FOLDER_PATH.FilePath("PetItemLuck.txt")
	def __init__(self):
		self.coding   = int
		self.itemRate = int
	
def LoadPetBase():
	global PET_BASE
	for config in PetBase.ToClassType():
		PET_BASE[(config.petType, config.starLevel)] = config
		
def LoadPetInitProperty():
	global PET_INIT_PROPERTY
	for config in PetInitProperty.ToClassType():
		config.InitProperty()
		PET_INIT_PROPERTY[config.petType] = config
		
def LoadPetTrainProperty():
	global PET_TRAIN_PROPERTY
	for config in PetTrainProperty.ToClassType():
		config.InitProperty()
		PET_TRAIN_PROPERTY[config.petType] = config
		
def LoadPetMaxProperty():
	global PET_MAX_PROPERTY
	for config in PetMaxProperty.ToClassType():
		config.InitProperty()
		PET_MAX_PROPERTY[(config.petType, config.starLevel)] = config
		
def LoadPetSoulBase():
	global PET_SOUL_BASE
	global PET_SOUL_SALE_RETURN
	for config in PetSoulBase.ToClassType():
		PET_SOUL_BASE[config.petSoulCoding] = config
		
		if config.saleReturn:
			PET_SOUL_SALE_RETURN[config.petSoulCoding] = config.saleReturn
		
def LoadPetLuckyDraw():
	global PET_LUCKY_DRAW
	global LUCKY_DRAW_RANDOM
	for config in PetLuckyDraw.ToClassType():
		PET_LUCKY_DRAW[config.rewardId] = config
		LUCKY_DRAW_RANDOM.AddRandomItem(config.rate, config.rewardId)

def LoadPetEvolution():
	global PET_EVOLUTION_DICT
	for config in PetEvolution.ToClassType():
		if config.shapeId and config.shapeId < 100:
			print "GE_EXC,petType(%s) and evoId(%s) 's shapeID must > 100" % (config.petType, config.evoId)
		key = (config.petType, config.evoId)
		if key in PET_EVOLUTION_DICT:
			print "GE_EXC,repeat petType=(%s) and evoId=(%s) in LoadPetEvolution" % (config.petType, config.evoId)
		config.InitProperty()
		PET_EVOLUTION_DICT[key] = config

def LoadPetItemLuck():
	global PET_ITEM_LUCK_DICT
	for config in PetItemLuck.ToClassType():
		if config.coding in PET_ITEM_LUCK_DICT:
			print "GE_EXC,repeat coding(%s) in PET_ITEM_LUCK_DICT" % config.coding
		PET_ITEM_LUCK_DICT[config.coding] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPetBase()
		LoadPetInitProperty()
		LoadPetTrainProperty()
		LoadPetMaxProperty()
		LoadPetSoulBase()
		LoadPetLuckyDraw()
		LoadPetEvolution()
		LoadPetItemLuck()
