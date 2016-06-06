#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Dragon.DragonBase")
#===============================================================================
# 神龙基础
#===============================================================================
import copy
import Environment
from Game.Dragon import DragonConfig
from Game.Role.Data import EnumObj, EnumInt16, EnumTempObj

if "_HasLoad" not in dir():
	CAREER_INDEX = 1
	LEVEL_INDEX = 2
	EXP_INDEX = 3
	GRADE_INDEX = 4
	ACTIVE_SKILL_INDEX = 5
	PASSIVE_SKILL_INDEX = 6
	
class DragonMgr(object):
	def __init__(self, role):
		dragonDict = role.GetObj(EnumObj.Dragon)
		
		self.role = role
		self.career_id = dragonDict.get(CAREER_INDEX, 0)
		self.level = dragonDict.get(LEVEL_INDEX, 0)
		self.exp = dragonDict.get(EXP_INDEX, 0)
		self.grade = dragonDict.get(GRADE_INDEX, 0)
		#主动
		if ACTIVE_SKILL_INDEX in dragonDict:
			self.active_skill_dict = copy.deepcopy(dragonDict[ACTIVE_SKILL_INDEX])
		else:
			self.active_skill_dict = {}
		#被动
		if PASSIVE_SKILL_INDEX in dragonDict:
			self.passive_skill_dict = copy.deepcopy(dragonDict[PASSIVE_SKILL_INDEX])
		else:
			self.passive_skill_dict = {}
		
	def create_dragon(self, careerId, careerConfig):
		self.career_id = careerId
		self.set_dragon_level(1)
		self.grade = 1
		#初始主动技能
		self.active_skill_dict[careerConfig.activeSkill1] = 1
		#设置角色神龙职业
		self.role.SetDragonCareerID(careerId)
		
	def change_dragon(self, careerId, newCareerConfig):
		oldCareerConfig = DragonConfig.DRAGON_CAREER.get(self.career_id)
		if not oldCareerConfig:
			return
		
		#转职
		self.career_id = careerId
		
		#设置角色神龙职业
		self.role.SetDragonCareerID(careerId)
		
		#主动技能
		if oldCareerConfig.activeSkill1 in self.active_skill_dict:
			level = self.active_skill_dict[oldCareerConfig.activeSkill1]
			del self.active_skill_dict[oldCareerConfig.activeSkill1]
			self.active_skill_dict[newCareerConfig.activeSkill1] = level
		if oldCareerConfig.activeSkill2 in self.active_skill_dict:
			level = self.active_skill_dict[oldCareerConfig.activeSkill2]
			del self.active_skill_dict[oldCareerConfig.activeSkill2]
			self.active_skill_dict[newCareerConfig.activeSkill2] = level
		if oldCareerConfig.activeSkill3 in self.active_skill_dict:
			level = self.active_skill_dict[oldCareerConfig.activeSkill3]
			del self.active_skill_dict[oldCareerConfig.activeSkill3]
			self.active_skill_dict[newCareerConfig.activeSkill3] = level
			
		#被动技能
		if oldCareerConfig.passiveSkill1 in self.passive_skill_dict:
			level = self.passive_skill_dict[oldCareerConfig.passiveSkill1]
			del self.passive_skill_dict[oldCareerConfig.passiveSkill1]
			self.passive_skill_dict[newCareerConfig.passiveSkill1] = level
		
	def get_active_skills(self):
		careerConfig = DragonConfig.DRAGON_CAREER.get(self.career_id)
		if not careerConfig:
			return
		
		activeSkill1 = careerConfig.activeSkill1
		activeSkill2 = careerConfig.activeSkill2
		activeSkill3 = careerConfig.activeSkill3
		
		activeSkillsList = []
		if activeSkill1 in self.active_skill_dict:
			activeSkillsList.append((activeSkill1, self.active_skill_dict[activeSkill1]))
		if activeSkill2 in self.active_skill_dict:
			activeSkillsList.append((activeSkill2, self.active_skill_dict[activeSkill2]))
		if activeSkill3 in self.active_skill_dict:
			activeSkillsList.append((activeSkill3, self.active_skill_dict[activeSkill3]))
		
		return activeSkillsList
	
	def get_passive_skills(self):
		return self.passive_skill_dict.items()
	
	def set_dragon_level(self, level):
		self.level = level
		self.role.SetI16(EnumInt16.DragonLevel, level)
		
		#版本判断
		if Environment.EnvIsNA():
			#开服活动
			kaifuActMgr = self.role.GetTempObj(EnumTempObj.KaiFuActMgr)
			kaifuActMgr.dragon_level(level)
	
	def save(self):
		dragonDict = self.role.GetObj(EnumObj.Dragon)
		
		dragonDict[CAREER_INDEX] = self.career_id
		dragonDict[LEVEL_INDEX] = self.level
		dragonDict[EXP_INDEX] = self.exp
		dragonDict[GRADE_INDEX] = self.grade
		dragonDict[ACTIVE_SKILL_INDEX] = copy.deepcopy(self.active_skill_dict)
		dragonDict[PASSIVE_SKILL_INDEX] = copy.deepcopy(self.passive_skill_dict)

