#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.JingLongShouHu")
#===============================================================================
# 金龙守护 提升玩家血量
#===============================================================================
from Game.Fight import SkillBase

class JingLongShouHu(SkillBase.PassiveSkill):
	skill_id = 2501
	level_to_life_upgrade_rate = [0, 0.3, 0.35, 0.4, 0.45, 0.5]
	level_to_life_upgrade_value = [0, 0, 0, 0, 0, 0]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._join.add(self.auto_u_join)
	
	def unload_event(self):
		self.unit._join.discard(self.auto_u_join)
	# AutoCodeEnd
	def auto_u_join(self, unit):
		self.life_upgrade = int(self.unit.hp * self.level_to_life_upgrade_rate[self.argv] + self.level_to_life_upgrade_value[self.argv])
		self.unit.hp += self.life_upgrade


if "_HasLoad" not in dir():
	JingLongShouHu.reg()
