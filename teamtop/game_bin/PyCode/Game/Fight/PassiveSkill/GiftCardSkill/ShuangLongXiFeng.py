#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.ShuangLongXiFeng")
#===============================================================================
# 双龙戏凤：目标生命值低于50%时，提升自身伤害，最大可提升75%
#===============================================================================
from Game.Fight import SkillBase

class ShuangLongXiFeng(SkillBase.PassiveSkill):
	skill_id = 913
	level_to_target_skill_rate = [0, 0.2, 0.24, 0.29, 0.34, 0.4, 0.2, 0.24, 0.29, 0.34, 0.4, 0.46, 0.53, 0.6, 0.67, 0.75]
	level_to_hp_rate = [0, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_target(self, target, skill):
		if target.hp > target.max_hp * float (self.level_to_hp_rate[self.argv]) :
			return
		if skill.is_treat:
			return
		skill.target_skill_rate += self.level_to_target_skill_rate [self.argv]

if "_HasLoad" not in dir():
	ShuangLongXiFeng.reg()
