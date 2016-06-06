#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.DragonKnightChallenge11")
#===============================================================================
# 每回合伤害减免提升10%，最高可叠加8层
#===============================================================================
from Game.Fight import SkillBase

class DragonKnightChallenge11(SkillBase.PassiveSkill):
	skill_id = 513
	level_to_damage_reduce_rate = {1:0.1, 2:0.2, 3:0.3, 4:0.4, 5:0.5, 6:0.6, 7:0.7, 8:0.8}
	IS_MAX = 8
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.base_damage_reduce_rate = self.unit.damage_reduce_rate

	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_target(self, target, skill):
		fightround = self.unit.fight.round
		if fightround > self.IS_MAX:
			fightround = 8
		self.unit.damage_reduce_rate = self.base_damage_reduce_rate + self.level_to_damage_reduce_rate.get(fightround)



if "_HasLoad" not in dir():
	DragonKnightChallenge11.reg()