#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ZhanZhenSkill")
#===============================================================================
# 战阵技能
#===============================================================================
from Game.Fight import SkillBase

class ZhanZhenSkill(SkillBase.PassiveSkill):
	skill_id = 666
	level_to_target_skill_rate = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_be_target.add(self.auto_u_before_be_target)
	
	def unload_event(self):
		self.unit._before_be_target.discard(self.auto_u_before_be_target)
	# AutoCodeEnd
	def auto_u_before_be_target(self, unit, skill):
		level = self.argv
		if level > 2 and  unit.passive_skills:
			for ps in unit.passive_skills:
				if ps.skill_id != self.skill_id:
					continue
				if ps.argv <= level:
					break
				elif ps.argv > level:
					level = 2
					break
		
		self.unit.temp_damage_reduce_rate += self.level_to_target_skill_rate[level]


if "_HasLoad" not in dir():
	ZhanZhenSkill.reg()
