#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.AddMaxHp")
#===============================================================================
# 混沌神域技能，增加最大血量
#===============================================================================
from Game.Fight import SkillBase

class AddMaxHp(SkillBase.PassiveSkill):
	skill_id = 860
	add_max_hp_rate = 0.3
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_c_join(self,unit):
		if self.fight.round != 0:
			return
		self.add_hp_coef = self.add_max_hp_rate
		self.add_max_hp = int(self.unit.max_hp * self.add_hp_coef)
		self.add_hp = int(self.unit.hp * self.add_hp_coef)
		if self.unit is unit:
			self.unit.change_max_hp(self.add_max_hp)
			self.unit.change_max_hp_coef(self.add_hp_coef)
			self.unit.change_hp(self.add_hp)	

if "_HasLoad" not in dir():
	AddMaxHp.reg()
