#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.ShangJinDuanMai")
#===============================================================================
# 伤筋断脉：提升自身的伤害量，最大可提升50%
#===============================================================================
from Game.Fight import SkillBase

class ShangJinDuanMai(SkillBase.PassiveSkill):
	skill_id = 908
	level_to_damage_upgrade_rate = [0, 0.1, 0.12, 0.14, 0.17, 0.20, 0.15, 0.17, 0.19, 0.22, 0.25, 0.29, 0.33, 0.38, 0.44, 0.50]
	
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
		self.unit.damage_upgrade_rate += self.level_to_damage_upgrade_rate[self.argv]

if "_HasLoad" not in dir():
	ShangJinDuanMai.reg()
