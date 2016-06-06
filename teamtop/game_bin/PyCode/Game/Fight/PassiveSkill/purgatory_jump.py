#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.purgatory_jump")
#===============================================================================
# 心魔炼狱跳关被动技能 
# 可以跳关的那一波怪物都要配这个技能, 因为可能boss先死
# 被动技能的ID从500开始
#===============================================================================
from Game.Fight import SkillBase

class purgatory_jump(SkillBase.PassiveSkill):
	skill_id = 509
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._has_be_kill.add(self.auto_u_has_be_kill)
	
	def unload_event(self):
		self.unit._has_be_kill.discard(self.auto_u_has_be_kill)
	# AutoCodeEnd
	
	# 被杀
	def auto_u_has_be_kill(self, source, unit):
		#不是最后一只怪物被杀
		if len(unit.camp.pos_units) != 1:
			return
		#大于三回合
		if self.fight.round - self.unit.create_round > 3:
			return
		#删掉后面两波怪物
		CAMP = unit.camp
		for _ in xrange(2):
			if not CAMP.wheels:
				break
			CAMP.wheels.pop(0)
			CAMP.monster_wave += 1

if "_HasLoad" not in dir():
	purgatory_jump.reg()
