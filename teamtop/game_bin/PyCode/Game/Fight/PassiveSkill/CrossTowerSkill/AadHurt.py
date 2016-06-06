#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.CrossTowerSkill.AadHurt")
#===============================================================================
# 注释
#===============================================================================
from Game.Fight import SkillBase

class AadHurt(SkillBase.PassiveSkill):
	skill_id = 1002
	level_to_target_skill_rate = {1:1, 2:2, 3:3, 4:4}
	IS_MAX = 4
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	
	def auto_u_before_target(self, target, skill):
		fightround = self.unit.fight.round
		if fightround > self.IS_MAX:
			fightround = 4
		skill.target_skill_rate += self.level_to_target_skill_rate.get(fightround)

if "_HasLoad" not in dir():
	AadHurt.reg()
