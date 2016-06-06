#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.MoFaZhen.MoFaZhenConfig")
#===============================================================================
# 魔法阵 config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("MoFaZhen")
	
	MFZ_SkillBase_Dict = {}			#魔法阵技能升级配置 {skillID:cfg,}
	MFZ_SkillLevelUp_Dict = {}		#魔法阵技能配置{skillType:{skillLevel:cfg,},}
	
class MFZSkillLevelup(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("MFZSkillLevelup.txt")
	def __init__(self):
		self.skillID = int
		self.skillType = int
		self.skillLevel = int
		self.maxLevel = int
		self.name = str
		self.needSkillPointType = int
		self.needSkillPoint = int
		self.nextSkillID = int

def GetNeedSkillPointDict(skillType):
	'''
	获取对应类型技能 不同等级需要的技能点类型技能点
	'''
	skillTypeDict = MFZ_SkillLevelUp_Dict.get(skillType,{})
	needSPDict = {}
	for level, cfg in skillTypeDict.iteritems():
		needSPDict[level] = [cfg.needSkillPointType, cfg.needSkillPoint]
	
	if len(needSPDict) < 1:
		return None
	else:
		return needSPDict

def LoadMFZSkillLevelup():
	global MFZ_SkillBase_Dict
	global MFZ_SkillLevelUp_Dict
	for cfg in MFZSkillLevelup.ToClassType():
		skillID = cfg.skillID
		skillType = cfg.skillType
		skillLevel = cfg.skillLevel
		
		if skillID in MFZ_SkillBase_Dict:
			print "GE_EXC,repeat MFZSkillID(%s) in MFZ_SkillBase_Dict" % skillID
		MFZ_SkillBase_Dict[skillID] = cfg
		
		skillTypeDict = MFZ_SkillLevelUp_Dict.setdefault(skillType, {})
		if skillLevel in skillTypeDict:
			print "GE_EXC, repeat MFZSkillLevel(%S) in MFZ_SkillLevelUp_Dict with MFZSkillType(%s)" % (skillLevel, skillType)
		skillTypeDict[skillLevel] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadMFZSkillLevelup()
