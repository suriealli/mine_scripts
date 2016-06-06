#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.ReduceDamage")
#===============================================================================
# 混沌神域技能，免伤30%
#===============================================================================
from Game.Fight import SkillBase

class ReduceDamage(SkillBase.PassiveSkill):
	skill_id = 856
	damge_reduce_rate = 0.3		#免伤比例
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._join.add(self.auto_u_join)
	
	def unload_event(self):
		self.unit._join.discard(self.auto_u_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_join(self,unit):
		self.unit.damage_reduce_rate += self.damge_reduce_rate

if "_HasLoad" not in dir():
	ReduceDamage.reg()
