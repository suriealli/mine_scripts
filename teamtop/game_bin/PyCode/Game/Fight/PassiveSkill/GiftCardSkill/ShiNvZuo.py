#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.ShiNvZuo")
#===============================================================================
# 进入战斗后，增加自身生命值20%
#===============================================================================
from Game.Fight import SkillBase

class ShiNvZuo(SkillBase.PassiveSkill):
	skill_id = 819
	level_to_change_hp_rate = [0, 0.15, 0.18, 0.21, 0.25, 0.30, 0.25, 0.28, 0.31, 0.35, 0.40, 0.45, 0.51, 0.57, 0.63, 0.70, 0.35, 0.38, 0.41, 0.45, 0.49, 0.54, 0.59, 0.64, 0.7, 0.76, 0.82, 0.87, 0.94, 1.02, 1.1]
	
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
		self.add_hp_coef = self.level_to_change_hp_rate[self.argv]
		self.add_max_hp = int(self.unit.max_hp * self.add_hp_coef)
		self.add_hp = int(self.unit.hp * self.add_hp_coef)
		if self.unit is unit:
			self.unit.change_max_hp(self.add_max_hp)
			self.unit.change_max_hp_coef(self.add_hp_coef)
			self.unit.change_hp(self.add_hp)

if "_HasLoad" not in dir():
	ShiNvZuo.reg()
