#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.MoFaZhen.MianShangBeiDong")
#===============================================================================
# 进入战斗后，自己免伤提升一定百分比。
#===============================================================================
from Game.Fight import SkillBase

class MianShangBeiDong(SkillBase.PassiveSkill):
	skill_id = 703
	level_to_damage_reduce_rate = [0, 0.08, 0.12, 0.16, 0.2, 0.25]
	
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
		self.unit.damage_reduce_rate += self.level_to_damage_reduce_rate[self.argv]

if "_HasLoad" not in dir():
	MianShangBeiDong.reg()
