#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Dragon.DragonConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Property import PropertyEnum

DRAGON_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
DRAGON_FILE_FOLDER_PATH.AppendPath("Dragon")

if "_HasLoad" not in dir():
	DRAGON_BASE = {}
	DRAGON_GRADE = {}
	DRAGON_CAREER = {}
	DRAGON_EXP = {}
	DRAGON_EXP_ITEM = {}
	DRAGON_SKILL = {}
	SKILL_POINT_PROPERTY = {}
	CHANGE_JOB = {}
	MAX_CHANGE_JON_TIMES = 0	#转职业配置的最大次数
	EXP_ITEM_CODING_LIST = []	#神龙经验道具coding列表
	ACTIVE_SKILL_DICT = {}		#主动技能字典
	
	MAX_SKILL_POINT = 0		#最大技能点
	MIN_SKILL_POINT = 0		#最小技能点
	
class DragonBase(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	神龙基础配置表
	'''
	FilePath = DRAGON_FILE_FOLDER_PATH.FilePath("DragonBase.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.level = int
		self.grade = int
		
class DragonGrade(TabFile.TabLine):
	'''
	神龙阶级配置表
	'''
	FilePath = DRAGON_FILE_FOLDER_PATH.FilePath("DragonGrade.txt")
	def __init__(self):
		self.grade = int
		self.maxLevel = int
		self.needItemCoding = int
		self.needItemCnt = int
		self.skillPointReward = int
		
class DragonCareer(TabFile.TabLine):
	'''
	神龙职业配置表
	'''
	FilePath = DRAGON_FILE_FOLDER_PATH.FilePath("DragonCareer.txt")
	def __init__(self):
		self.careerId = int
		self.name = str
		self.activeSkill1 = int
		self.activeSkill2 = int
		self.activeSkill3 = int
		self.passiveSkill1 = int
		
class DragonExp(TabFile.TabLine):
	'''
	神龙经验配置表
	'''
	FilePath = DRAGON_FILE_FOLDER_PATH.FilePath("DragonExp.txt")
	def __init__(self):
		self.level = int
		self.exp = int
		
class DragonExpItem(TabFile.TabLine):
	'''
	神龙经验道具配置表
	'''
	FilePath = DRAGON_FILE_FOLDER_PATH.FilePath("DragonExpItem.txt")
	def __init__(self):
		self.itemCoding = int
		self.exp = int
		
class DragonSkill(TabFile.TabLine):
	'''
	神龙技能配置表
	'''
	FilePath = DRAGON_FILE_FOLDER_PATH.FilePath("DragonSkill.txt")
	def __init__(self):
		self.skillId = int
		self.level = int
		self.maxLevel = int
		self.needSkill = self.GetEvalByString
		self.needSkillPoint = int
	
class SkillPointProperty(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	组队技能点属性配置
	'''
	FilePath = DRAGON_FILE_FOLDER_PATH.FilePath("SkillPointProperty.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.level = int
		self.needSkillPoint = int
		
class ChangeJob(TabFile.TabLine):
	'''
	转换职业配置
	'''
	FilePath = DRAGON_FILE_FOLDER_PATH.FilePath("ChangeJob.txt")
	def __init__(self):
		self.cnt = int
		self.needRMB = int

def LoadDragonBase():
	global DRAGON_BASE
	for config in DragonBase.ToClassType():
		config.InitProperty()
		DRAGON_BASE[(config.level, config.grade)] = config
		
def LoadDragonGrade():
	global DRAGON_GRADE
	for config in DragonGrade.ToClassType():
		DRAGON_GRADE[config.grade] = config

def LoadDragonCareer():
	global DRAGON_CAREER
	global ACTIVE_SKILL_DICT
	for config in DragonCareer.ToClassType():
		DRAGON_CAREER[config.careerId] = config
		ACTIVE_SKILL_DICT.setdefault(config.careerId, [config.activeSkill1, config.activeSkill2, config.activeSkill3])
		
def LoadDragonExp():
	global DRAGON_EXP
	for config in DragonExp.ToClassType():
		DRAGON_EXP[config.level] = config
		
def LoadDragonExpItem():
	global DRAGON_EXP_ITEM
	global EXP_ITEM_CODING_LIST
	for config in DragonExpItem.ToClassType():
		DRAGON_EXP_ITEM[config.itemCoding] = config
		
		if config.itemCoding not in EXP_ITEM_CODING_LIST:
			EXP_ITEM_CODING_LIST.append(config.itemCoding)
			
def LoadDragonSkill():
	global DRAGON_SKILL
	for config in DragonSkill.ToClassType():
		DRAGON_SKILL[(config.skillId, config.level)] = config
		
def LoadSkillPointProperty():
	global SKILL_POINT_PROPERTY
	global MAX_SKILL_POINT
	global MIN_SKILL_POINT
	
	idx = 0
	for config in SkillPointProperty.ToClassType():
		config.InitProperty()
		
		if config.level == 1:
			MIN_SKILL_POINT = config.needSkillPoint
			
		if config.needSkillPoint > MAX_SKILL_POINT:
			MAX_SKILL_POINT = config.needSkillPoint
		
		start = idx
		for _ in xrange(start, config.needSkillPoint):
			idx += 1
			SKILL_POINT_PROPERTY[idx] = config
		
def LoadChangeJob():
	global CHANGE_JOB
	global MAX_CHANGE_JON_TIMES
	for config in ChangeJob.ToClassType():
		CHANGE_JOB[config.cnt] = config
		if MAX_CHANGE_JON_TIMES < config.cnt:
			MAX_CHANGE_JON_TIMES = config.cnt

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsNA() or Environment.IsDevelop):
		LoadDragonBase()
		LoadDragonGrade()
		LoadDragonCareer()
		LoadDragonExp()
		LoadDragonExpItem()
		LoadDragonSkill()
		LoadSkillPointProperty()
		LoadChangeJob()
		
