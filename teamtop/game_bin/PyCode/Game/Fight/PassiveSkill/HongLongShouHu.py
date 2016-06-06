#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.HongLongShouHu")
#===============================================================================
# 红龙守护  提升玩家攻击 
#===============================================================================
from Game.Fight import SkillBase

class HongLongShouHu(SkillBase.PassiveSkill):
	skill_id = 2502
	level_to_attack_upgrade_rate = [0, 0.3, 0.35, 0.4, 0.45, 0.5]
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
		self.unit.attack_upgrade = int(self.unit.attack * self.level_to_attack_upgrade_rate[self.argv] + self.level_to_attack_upgrade_value[self.argv])
		self.unit.attack += self.unit.attack_upgrade


	# 下面开始写事件代码

if "_HasLoad" not in dir():
	HongLongShouHu.reg()
