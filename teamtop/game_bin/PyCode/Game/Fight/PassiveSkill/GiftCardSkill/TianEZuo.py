#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.TianEZuo")
#===============================================================================
# 每回合回复一定比例的自身最大血量
#===============================================================================
from Game.Fight import SkillBase

class TianEZuo(SkillBase.PassiveSkill):
	skill_id = 814
	level_to_life_upgrade_rate = [0, 0.03, 0.04, 0.05, 0.06, 0.08, 0.05, 0.06, 0.07, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2]
	
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
		life_upgrade = int(self.level_to_life_upgrade_rate[self.argv]* self.unit.max_hp )
		self.unit.treat(life_upgrade, self.unit)

if "_HasLoad" not in dir():
	TianEZuo.reg()
