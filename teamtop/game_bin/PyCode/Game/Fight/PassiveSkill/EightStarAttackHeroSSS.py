#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.EightStarAttackHeroSSS")
#===============================================================================
# 敌方血量低于30%时，造成伤害加倍
#===============================================================================
from Game.Fight import SkillBase

class EightStarAttackHeroSSS(SkillBase.PassiveSkill):
	skill_id = 409
	level_to_target_skill_rate = [0, 0.5, 0.5]
	level_to_hp_rate = [0, 0.3, 0.3]
	
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
	
	# 下面开始写事件代码

if "_HasLoad" not in dir():
	EightStarAttackHeroSSS.reg()
