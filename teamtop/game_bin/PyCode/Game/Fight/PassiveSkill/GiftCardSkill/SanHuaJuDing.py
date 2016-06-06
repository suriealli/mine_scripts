#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.SanHuaJuDing")
#===============================================================================
# 三花聚顶：生命值低于50%时，提升自身的无视伤害的几率，最大可提升35%
#===============================================================================
import random
from Game.Fight import SkillBase

class SanHuaJuDing(SkillBase.PassiveSkill):
	skill_id = 912
	level_to_antidamage_rate = [0, 6, 8, 10, 12, 15, 8, 10, 12, 14, 17, 20, 23, 26, 30, 35]
	level_to_hp_rate = [0, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.trigger_round = -999
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_hurt.add(self.auto_u_before_hurt)
	
	def unload_event(self):
		self.unit._before_hurt.discard(self.auto_u_before_hurt)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_hurt(self, unit, original_jap, now_jap):
		if self.trigger_round < 0:
			if self.has_revive_status():
				return now_jap
			if float(self.unit.hp) / self.unit.max_hp < float (self.level_to_hp_rate[self.argv]):
				self.trigger_round = self.fight.round
				self.make_revive_status()
				if random.randint(0, 99) < self.level_to_antidamage_rate[self.argv]:
					return 0
				else:
					return now_jap
			else:
				return now_jap
		elif self.trigger_round + 1 >= self.fight.round:
			if random.randint(0, 99) < self.level_to_antidamage_rate[self.argv]:
				return 0
			else:
				return now_jap
		else:
			return now_jap

if "_HasLoad" not in dir():
	SanHuaJuDing.reg()
