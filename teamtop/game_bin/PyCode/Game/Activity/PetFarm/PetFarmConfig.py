#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PetFarm.PetFarmConfig")
#===============================================================================
# 宠物农场（宠物灵树）配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	PetFarm_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	PetFarm_FILE_FOLDER_PATH.AppendPath("PetFarm")
	
	PETFARMRANDOM = Random.RandomRate()
	PetFarmHarvestConfigDict = {}


class PetFarmHarvestConfig(TabFile.TabLine):
	'''
	宠物灵树配置表
	'''
	FilePath = PetFarm_FILE_FOLDER_PATH.FilePath("petfarm_harvest.txt")
	def __init__(self):
		self.pf_harvest_type = int
		self.pf_harvest_rate = int
		self.pf_harvest_items = self.GetEvalByString
		
def LoadPetFarmHarvestConfig():
	'''
	 载入宠物灵树配置表
	'''
	global PetFarmHarvestConfigDict
	global PETFARMRANDOM
	for config in PetFarmHarvestConfig.ToClassType():
		if config.pf_harvest_type in PetFarmHarvestConfigDict:
			print "GE_EXC, repeat config.pf_harvest_type(%) in LoadPetFarmHarvestConfi " % config.pf_harvest_type
		PETFARMRANDOM.AddRandomItem(config.pf_harvest_rate, config.pf_harvest_type)
		PetFarmHarvestConfigDict[config.pf_harvest_type] = config.pf_harvest_items

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPetFarmHarvestConfig()
		