#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.ShiZiZuo")
#===============================================================================
# 战斗开始时候有减伤效果，持续2回合
#===============================================================================
from Game.Fight import SkillBase

class ShiZiZuo(SkillBase.PassiveSkill):
	skill_id = 805
	level_to_damage_reduce_rate = [0, 0.16, 0.18, 0.22, 0.26, 0.32, 0.24, 0.26, 0.3, 0.34, 0.4, 0.46, 0.54, 0.62, 0.7, 0.8, 0.24, 0.26,	0.3, 0.34, 0.4, 0.46, 0.54,	0.62, 0.7, 0.8, 0.85, 0.9, 0.95, 1, 1.1]
	level_to_damage_reduce_round = [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.has_create_buff = False
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._join.add(self.auto_u_join)
	
	def unload_event(self):
		self.unit._join.discard(self.auto_u_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_join(self, unit):
		if self.has_create_buff == False :
			self.has_create_buff = True
			self.unit.create_buff("ReduceDamageUp", self.level_to_damage_reduce_round[self.argv], self.level_to_damage_reduce_rate[self.argv])

if "_HasLoad" not in dir():
	ShiZiZuo.reg()
