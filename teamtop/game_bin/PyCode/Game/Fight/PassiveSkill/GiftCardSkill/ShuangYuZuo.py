#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.ShuangYuZuo")
#===============================================================================
# 双鱼座：生命低于50%时，无视伤害（免伤100%）的概率两回合，一次战斗中只能生效一次
#===============================================================================
import random
from Game.Fight import SkillBase

class ShuangYuZuo(SkillBase.PassiveSkill):
	skill_id = 802
	level_to_antidamage_rate = [0, 6, 8, 10, 12, 15, 8, 10, 12, 14, 17, 20, 23, 26, 30, 35, 12, 14, 17, 20, 23, 26, 30, 34, 38, 42, 46, 50, 55, 60, 65]
	level_to_hp_rate = [0, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
	
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
	ShuangYuZuo.reg()
