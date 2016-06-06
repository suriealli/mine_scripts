#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.FeiMaZuo")
#===============================================================================
# 飞马座：目标生命低于X时，伤害提升一定百分比
#===============================================================================
from Game.Fight import SkillBase

class FeiMaZuo(SkillBase.PassiveSkill):
	skill_id = 815
	level_to_target_skill_rate = [0, 0.2, 0.24, 0.29, 0.34, 0.4, 0.2, 0.24, 0.29, 0.34, 0.4, 0.46, 0.53, 0.6, 0.67, 0.75, 0.3, 0.34, 0.38, 0.43, 0.48, 0.54, 0.6, 0.67, 0.74, 0.82, 0.9, 0.98, 1.06, 1.15, 1.25]
	level_to_hp_rate = [0, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	def auto_u_before_target(self, target, skill):
		if target.hp > target.max_hp * float (self.level_to_hp_rate[self.argv]) :
			return
		if skill.is_treat:
			return
		skill.target_skill_rate += self.level_to_target_skill_rate [self.argv]

if "_HasLoad" not in dir():
	FeiMaZuo.reg()
