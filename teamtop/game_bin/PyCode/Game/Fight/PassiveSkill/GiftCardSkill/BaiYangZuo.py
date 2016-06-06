#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.BaiYangZuo")
#===============================================================================
# 白羊座：目标生命高于一定百分比时候，造成伤害提高一定比率
#===============================================================================
from Game.Fight import SkillBase

class BaiYangZuo(SkillBase.PassiveSkill):
	skill_id = 807
	level_to_target_skill_rate = [0, 0.2, 0.24, 0.29, 0.34, 0.40, 0.2, 0.24, 0.29, 0.34, 0.40, 0.46, 0.53, 0.60, 0.67, 0.75]
	level_to_hp_rate = [0, 0.7, 0.7, 0.7, 0.7, 0.7, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	def auto_u_before_target(self, target, skill):
		if target.hp < target.max_hp * float (self.level_to_hp_rate[self.argv]) :
			return
		if skill.is_treat:
			return
		skill.target_skill_rate += self.level_to_target_skill_rate [self.argv]

if "_HasLoad" not in dir():
	BaiYangZuo.reg()
