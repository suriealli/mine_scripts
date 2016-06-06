#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ElementSpirit.ElementalEssenceConfig")
#===============================================================================
# 元素精炼配置表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	EE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	EE_FILE_FOLDER_PATH.AppendPath("ElementSpirit")
	ElementalEssence = {}				#元素精炼
	ElementalEssenceRandom = {}			#元素抽奖


class ElementalEssenceConfig(TabFile.TabLine):
	FilePath = EE_FILE_FOLDER_PATH.FilePath("ElementalEssence.txt")
	def __init__(self):
		self.RefineId = int
		self.RefineType = int
		self.MinElementalEssence = int
		self.MaxElementalEssence = int
		self.Cost = int
		self.Rate = int
		
def LoadElementalEssenceConfig():
	global ElementalEssence,ElementalEssenceRandom
	for cf in ElementalEssenceConfig.ToClassType():
		if cf.RefineId in ElementalEssence :
			print "GE_EXC, repeat RefineId %s in ElementalEssence" % cf.RefineId
		ElementalEssence[cf.RefineId] = cf
		if cf.RefineType not in ElementalEssenceRandom :
			ElementalEssenceRandom[cf.RefineType] = Random.RandomRate()
		ElementalEssenceRandom[cf.RefineType].AddRandomItem(cf.Rate, cf.RefineId)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross: 
		LoadElementalEssenceConfig()