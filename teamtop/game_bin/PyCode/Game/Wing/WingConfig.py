#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Wing.WingConfig")
#===============================================================================
# 翅膀配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Property import PropertyEnum

WING_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
WING_FILE_FOLDER_PATH.AppendPath("Wing")

if "_HasLoad" not in dir():
	WING_BASE = {}
	WING_EVOLVE = {}
	WING_COLLECT = []
	
class WingBase(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	翅膀基础配置
	'''
	FilePath = WING_FILE_FOLDER_PATH.FilePath("WingBase.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.wingId = int
		self.level = int
		self.levelUpExp = int
		self.maxLevel = int
		self.trainNeedRMB = int
		self.trainNeedItemCoding = int
		self.trainAddExp = int
		self.trainCrit = int
		self.trainCritOdds = int
		
class WingEvolve(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	翅膀进阶配置
	'''
	FilePath = WING_FILE_FOLDER_PATH.FilePath("WingEvolve.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.wingId = int
		self.grade = int
		self.needWingLevel = int
		self.maxGrade = int
		self.needItemCoding = int
		self.needItemCnt = int
		
class WingCollect(TabFile.TabLine):
	'''
	翅膀收集基础配置
	'''
	FilePath = WING_FILE_FOLDER_PATH.FilePath("WingCollect.txt")
	def __init__(self):
		self.wingLevel = int
		self.antibroken = int
		self.notbroken = int

def LoadWingBase():
	global WING_BASE
	for config in WingBase.ToClassType():
		config.InitProperty()
		WING_BASE[(config.wingId, config.level)] = config
		
def LoadWingEvolve():
	global WING_EVOLVE
	for config in WingEvolve.ToClassType():
		config.InitProperty()
		WING_EVOLVE[(config.wingId, config.grade)] = config
		
def LoadWingCollect():
	global WING_COLLECT
	for config in WingCollect.ToClassType():
		WING_COLLECT.append(config)
	#倒序
	WING_COLLECT.reverse()

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadWingBase()
		LoadWingEvolve()
		LoadWingCollect()
