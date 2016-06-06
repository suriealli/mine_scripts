#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.AddDamageTillDie")
#===============================================================================
# 混沌神域技能每次攻击增加20%直到死亡
#===============================================================================
from Game.Fight import SkillBase

class AddDamageTillDie(SkillBase.PassiveSkill):
	skill_id = 851
	damage_upgrade_rate = 0.2
	
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
		skill.target_skill_rate += self.damage_upgrade_rate * self.unit.fight.round

if "_HasLoad" not in dir():
	AddDamageTillDie.reg()
