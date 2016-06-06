#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.Add50PercentDamage")
#===============================================================================
# 混沌神域技能，增加伤害
#===============================================================================
from Game.Fight import SkillBase

class Add50PercentDamage(SkillBase.PassiveSkill):
	skill_id = 858
	damge_upgrade_rate = 0.2
	
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._join.add(self.auto_u_join)
	
	def unload_event(self):
		self.unit._join.discard(self.auto_u_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_join(self, unit):
		self.unit.damage_upgrade_rate += self.damge_upgrade_rate

if "_HasLoad" not in dir():
	Add50PercentDamage.reg()
