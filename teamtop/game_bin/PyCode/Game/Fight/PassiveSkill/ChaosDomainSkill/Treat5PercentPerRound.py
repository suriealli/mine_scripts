#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.Treat5PercentPerRound")
#===============================================================================
# 混沌神域技能，每回合回复15%血量
#===============================================================================
from Game.Fight import SkillBase

class Treat5PercentPerRound(SkillBase.PassiveSkill):
	skill_id = 855
	life_upgrade_rate = 0.1
	
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
		life_upgrade = int(self.life_upgrade_rate * self.unit.max_hp)
		self.unit.treat(life_upgrade, self.unit)

if "_HasLoad" not in dir():
	Treat5PercentPerRound.reg()
