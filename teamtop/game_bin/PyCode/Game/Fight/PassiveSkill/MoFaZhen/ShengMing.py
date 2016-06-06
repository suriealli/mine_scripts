#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.MoFaZhen.ShengMing")
#===============================================================================
# 进入战斗后，增加全队的生命上限，增加的数值为自身最大生命值的百分比。战斗中生效一次
#===============================================================================
from Game.Fight import SkillBase

class ShengMing(SkillBase.PassiveSkill):
	skill_id = 704
	level_to_max_hp = [0, 0, 0, 0, 0, 0]
	level_to_rate = [0, 0.08, 0.12, 0.16, 0.2, 0.25]
	
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
		if self.fight.round != 0:
			return
		self.add_hp_coef = self.level_to_rate[self.argv]
		self.add_max_hp = self.level_to_max_hp[self.argv] + int(unit.max_hp * self.add_hp_coef)
		self.add_hp = self.level_to_max_hp[self.argv] + int(unit.hp * self.add_hp_coef)
		unit.change_max_hp(self.add_max_hp)
		unit.change_max_hp_coef(self.add_hp_coef)
		unit.change_hp(self.add_hp)
if "_HasLoad" not in dir():
	ShengMing.reg()
