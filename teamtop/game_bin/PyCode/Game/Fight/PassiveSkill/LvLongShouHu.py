#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.LvLongShouHu")
#===============================================================================
# 绿龙守护 增加玩家血量和伤害值
#===============================================================================
from Game.Fight import SkillBase

class LvLongShouHu(SkillBase.PassiveSkill):
	skill_id = 2503
	level_to_life_upgrade_rate = [0, 0.15, 0.175, 0.2, 0.225, 0.25]
	level_to_life_upgrade_value = [0, 0, 0, 0, 0, 0]
	level_to_attack_upgrade_rate = [0, 0.15, 0.175, 0.2, 0.225, 0.25]
	level_to_attack_upgrade_value = [0, 0, 0, 0, 0, 0]
	
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
		self.attack_upgrade = int(self.unit.attack * self.level_to_attack_upgrade_rate[self.argv] + self.level_to_attack_upgrade_value[self.argv])
		self.unit.hp += self.life_upgrade
		self.unit.attack += self.attack_upgrade

if "_HasLoad" not in dir():
	LvLongShouHu.reg()
