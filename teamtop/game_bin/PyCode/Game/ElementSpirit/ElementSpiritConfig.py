#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ElementSpirit.ElementSpiritConfig")
#===============================================================================
# 元素之灵 config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Property import PropertyEnum


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ElementSpirit")
	
	#元素之灵 基本配置 {elementSpiritID:cfg,}
	ElementSpirit_BaseConfig_Dict = {}
	
	#元素之灵 技能配置 {skillType:skillId}
	ElementSpirit_SkillConfig_Dict = {}
	
	#元素之灵 技能名称{skillType:SpiritType,}
	ElementSpirit_SpiritName_Dict = {}

	
class ElementSpirit(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = FILE_FLODER_PATH.FilePath("ElementSpirit.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.elementSpiritId = int
		self.gradeLevel = int
		self.starLevel = int
		self.canFollow = int
		self.canBreak = int
		self.nextId = int
		self.elementCreamRange = self.GetEvalByString
		self.breakNeedItem = self.GetEvalByString
		self.skillLevel = int
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


def GetElementSpiritIDByCultivateCnt(CultivateCnt):
	'''
	返回 元素精华消耗次数获得的经验所属 元素之灵ID
	'''
	elementSpiritId = 0
	for cfg in ElementSpirit_BaseConfig_Dict.values():
		if cfg.elementCreamRange[0] <= CultivateCnt <= cfg.elementCreamRange[1]:
			elementSpiritId = cfg.elementSpiritId
			break
	
	return elementSpiritId
	
	
def LoadElementSpirit():
	global ElementSpirit_BaseConfig_Dict
	for cfg in ElementSpirit.ToClassType():
		elementSpiritId = cfg.elementSpiritId
		if elementSpiritId in ElementSpirit_BaseConfig_Dict:
			print "GE_EXC,repeat elementSpiritId(%s) in ElementSpirit_BaseConfig_Dict" % elementSpiritId
			
		elementCreamRange = cfg.elementCreamRange
		if elementCreamRange[0] > elementCreamRange[1]:
			print "GE_EXC, config error in elementSpiritID(%s), error elementCreamRange(%s)" % (elementSpiritId, elementCreamRange)
		
		cfg.InitProperty()
		cfg.InitPPT()
		ElementSpirit_BaseConfig_Dict[elementSpiritId] = cfg

	
class ElementSpiritSkll(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ElementSpiritSkill.txt")
	def __init__(self):
		self.skillType = int
		self.skillId = int
		self.SpiritType = str


def LoadElementSpiritSkll():
	global ElementSpirit_SpiritName_Dict
	global ElementSpirit_SkillConfig_Dict
	for cfg in ElementSpiritSkll.ToClassType():
		ElementSpirit_SpiritName_Dict[cfg.skillType] = cfg.SpiritType
		ElementSpirit_SkillConfig_Dict[cfg.skillType] = cfg.skillId


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadElementSpirit()
		LoadElementSpiritSkll()
	