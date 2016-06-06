#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.StunDie")
#===============================================================================
# 混沌神域技能：如果被眩晕即死亡
#===============================================================================
from Game.Fight import SkillBase

class StunDie(SkillBase.PassiveSkill):
	skill_id = 864
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_f_after_round(self):
		if self.unit.stun:
			self.unit.change_hp(-self.unit.max_hp)

if "_HasLoad" not in dir():
	StunDie.reg()
