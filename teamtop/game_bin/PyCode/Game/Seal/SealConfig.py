#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Seal.SealConfig")
#===============================================================================
# 圣印系统配置表
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Property import PropertyEnum

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("Seal")
	#圣印配置表{SId:cf}
	Seal_BaseConfig_Dict = {}
	
class Seal(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = FILE_FLODER_PATH.FilePath("Seal.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.SealId = int
		self.SealType = int
		self.needLiLianAmount = int
		self.needSealAmounts = int
		self.nextSSId = int
		self.skillState = self.GetEvalByString
		#属性万分比
		self.attack_pt = int
		self.attack_mt = int
		self.maxhp_t = int
		self.crit_t = int
		self.critpress_t = int
		self.parry_t = int
		self.puncture_t = int
		self.antibroken_t = int
		self.notbroken_t = int
	
	
	def InitPPT(self):
		'''
		预处理万分比属性
		'''
		self.ppt_dict = {}
		self.ppt_dict[PropertyEnum.attack_p] = self.attack_pt
		self.ppt_dict[PropertyEnum.attack_m] = self.attack_mt
		self.ppt_dict[PropertyEnum.maxhp] = self.maxhp_t
		self.ppt_dict[PropertyEnum.crit] = self.crit_t
		self.ppt_dict[PropertyEnum.critpress] = self.critpress_t
		self.ppt_dict[PropertyEnum.parry] = self.parry_t
		self.ppt_dict[PropertyEnum.puncture] = self.puncture_t
		self.ppt_dict[PropertyEnum.antibroken] = self.antibroken_t
		self.ppt_dict[PropertyEnum.notbroken] = self.notbroken_t	
	
	
def LoadSeal():
	global Seal_BaseConfig_Dict
	for cf in Seal.ToClassType():
		sealId = cf.SealId
		if sealId in Seal_BaseConfig_Dict :
			print "GE_EXC, repeat sealId %s is in Seal_BaseConfig_Dict" % sealId
		cf.InitProperty()
		cf.InitPPT()
		Seal_BaseConfig_Dict[sealId] = cf

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSeal()