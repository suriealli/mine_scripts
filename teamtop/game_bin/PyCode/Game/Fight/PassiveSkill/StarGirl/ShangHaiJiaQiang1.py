#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.ShangHaiJiaQiang1")
#===============================================================================
# 伤害提升一定百分比
#===============================================================================
from Game.Fight import SkillBase

class ShangHaiJiaQiang1(SkillBase.PassiveSkill):
	skill_id = 3009
	level_to_damage_upgrade_rate = 0.1
	
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
		self.unit.damage_upgrade_rate += self.level_to_damage_upgrade_rate

if "_HasLoad" not in dir():
	ShangHaiJiaQiang1.reg()
