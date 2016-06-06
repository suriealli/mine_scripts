#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.ZengJiaShenMing")
#===============================================================================
# 为主人和英雄加1370+星灵10%生命上限
#===============================================================================
from Game.Fight import SkillBase

class ZengJiaShenMing(SkillBase.PassiveSkill):
	skill_id = 3000
	level_to_max_hp = [0,
					1500, 3000, 4500, 6000, 7500,
					9000, 10500, 12000, 13500, 15000,
					16500, 18000, 19500, 21000, 22500,
					24000, 25500, 27000, 28500, 30000]
	level_to_rate = 0.1
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_c_join(self, unit):
		role_id = self.unit.role_id
		if unit.unit_type == 1 and role_id == unit.role_id:
			add_hp = self.level_to_max_hp[self.argv] + int(self.unit.max_hp * self.level_to_rate)
			unit.change_max_hp(add_hp)
			unit.change_hp(add_hp)

if "_HasLoad" not in dir():
	ZengJiaShenMing.reg()
