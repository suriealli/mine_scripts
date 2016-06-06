#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Mount.MountConfig")
#===============================================================================
# 坐骑配置相关
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.Property import PropertyEnum

if "_HasLoad" not in dir():
	MOUNT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	MOUNT_FILE_FOLDER_PATH.AppendPath("Mount")
	_MOUNT_BASE = {}
	_MOUNT_EVOLVE = {}
	_MOUNT_FOOD = {}
	MOUNT_ITEM_DICT = {}
	MOUNT_EXCHANGE_DICT = {}
	
	MountApperanceGrade_Dict = {}
	
class MountIllusion(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	坐骑基础配置
	'''
	FilePath = MOUNT_FILE_FOLDER_PATH.FilePath("MountIllusion.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.mountId = int
		self.mountName = str
		self.moveSpeed = int
		self.moveSpeed = int
		self.isFly = int
		self.timeLimit = int
		
class MountEvolve(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	坐骑培养配置
	'''
	FilePath = MOUNT_FILE_FOLDER_PATH.FilePath("MountEvolve.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.evolveId = int
		self.level    = int
		self.starNum  = int
		self.totalExp = int
		self.needMoney = int
		self.addExp = int
		self.GoldCrit = int
		self.GoldTimes = int
		self.needRMB = int
		self.itemId = int
		self.RMBaddExp = int
		self.RMBCrit1 = int
		self.RMBTimes1 = int
		self.RMBCrit2 = int
		self.NextID = int

class MountFood(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	坐骑食物配置
	'''
	FilePath = MOUNT_FILE_FOLDER_PATH.FilePath("MountFood.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.foodId = int
		self.itemId    = int
		self.foodName  = str
		self.EatConditions = int
	
class MountItem(TabFile.TabLine):
	'''
	坐骑道具
	'''
	FilePath = MOUNT_FILE_FOLDER_PATH.FilePath("MountItem.txt")
	def __init__(self):
		self.coding		= int
		self.mountId	= int
		self.backItem	= self.GetEvalByString
	
class MountGrade(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	坐骑外形品质进化
	'''
	FilePath = MOUNT_FILE_FOLDER_PATH.FilePath("MountGrade.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.mountId = int
		self.mountGrade = int
		self.nextGrade = int
		self.needLevel	= int
		self.needevolveId = int
		self.needItemCoding = int
		self.needItemCnt = int

class MountExchange(TabFile.TabLine):
	'''
	坐骑兑换
	'''
	FilePath = MOUNT_FILE_FOLDER_PATH.FilePath("MountExchange.txt")
	def __init__(self):
		self.MountId = int
		self.needItemCoding = int
		self.needItemCnt = int
	
def LoadMountGrade():
	global MountApperanceGrade_Dict
	for MG in MountGrade.ToClassType():
		if (MG.mountId, MG.mountGrade) in MountApperanceGrade_Dict:
			print "GE_EXC, repeat mountId %s, mountGrade %s in MountApperanceGrade_Dict" % (MG.mountId, MG.mountGrade)
		MG.InitProperty()
		MountApperanceGrade_Dict[(MG.mountId, MG.mountGrade)] = MG
	
def LoadMountBase():
	global _MOUNT_BASE
	for MB in MountIllusion.ToClassType():
		if MB.mountId in _MOUNT_BASE:
			print "GE_EXC, repeat mountId in MountIllusion (%s)" % MB.mountId
		MB.InitProperty()
		_MOUNT_BASE[MB.mountId] = MB

def LoadMountEvolve():
	global _MOUNT_EVOLVE
	for ME in MountEvolve.ToClassType():
		if ME.evolveId in _MOUNT_EVOLVE:
			print "GE_EXC, repeat evolveId in MountEvolve (%s)" % ME.evolveId
		ME.InitProperty()
		_MOUNT_EVOLVE[ME.evolveId] = ME

def LoadMountFood():
	global _MOUNT_FOOD
	for ME in MountFood.ToClassType():
		if ME.foodId in _MOUNT_FOOD:
			print "GE_EXC, repeat FoodId in MountFood (%s)" % ME.foodId
		ME.InitProperty()
		_MOUNT_FOOD[ME.foodId] = ME
		
def LoadMountItem():
	global MOUNT_ITEM_DICT
	
	for cfg in MountItem.ToClassType():
		if cfg.coding in MOUNT_ITEM_DICT:
			print "GE_EXC, repeat coding(%s) in MountItem" % cfg.coding
		MOUNT_ITEM_DICT[cfg.coding] = cfg

def LoadMountExchange():
	global MOUNT_EXCHANGE_DICT
	for cfg in MountExchange.ToClassType():
		mountId = cfg.MountId
		if mountId in MOUNT_EXCHANGE_DICT:
			print "GE_EXC, repeat mountId(%s) in MOUNT_EXCHANGE_DICT" % mountId
		MOUNT_EXCHANGE_DICT[mountId] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadMountBase()
		LoadMountEvolve()
		LoadMountFood()
		LoadMountItem()
		LoadMountGrade()
		LoadMountExchange()
		
		