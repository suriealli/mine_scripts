#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.FuZeZongSheng")
#===============================================================================
# 福泽众生 进入战斗后所有己方单位增伤+5%，减伤+5%
# 被动技能的ID从500开始
#===============================================================================
from Game.Fight import SkillBase

class FuZeZongSheng(SkillBase.PassiveSkill):
	skill_id = 505
	level_to_damage_upgrade_rate = [0, 0.05, 0.1]
	level_to_damage_reduce_rate = [0, 0.05, 0.1]
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_c_join(self, unit):
		unit.damage_upgrade_rate += self.level_to_damage_upgrade_rate[self.argv]
		unit.damage_reduce_rate += self.level_to_damage_reduce_rate[self.argv]

if "_HasLoad" not in dir():
	FuZeZongSheng.reg()
