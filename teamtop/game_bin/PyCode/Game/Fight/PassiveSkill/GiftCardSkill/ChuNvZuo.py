#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.ChuNvZuo")
#===============================================================================
# 处女座：敌方每回合持续掉血，减少血量为持有者攻击力的5%，无视防御。
#===============================================================================
from Game.Fight import SkillBase

class ChuNvZuo(SkillBase.PassiveSkill):
	skill_id = 806
	level_to_change_hp_rate = [0, 0.03, 0.04, 0.05, 0.06, 0.08, 0.05, 0.06, 0.07, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.08,	0.09, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.22, 0.24,	0.27, 0.3, 0.33, 0.36, 0.4]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_f_after_round(self):
		for unit in self.other_camp.pos_units.values():
			unit.hurt(int(self.unit.attack * self.level_to_change_hp_rate[self.argv]), None)
			#unit.change_hp(-int(self.unit.attack * self.level_to_change_hp_rate[self.argv]))

if "_HasLoad" not in dir():
	ChuNvZuo.reg()
