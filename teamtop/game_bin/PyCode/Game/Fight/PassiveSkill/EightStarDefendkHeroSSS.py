#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.EightStarDefendkHeroSSS")
#===============================================================================
# 每次攻击伤害减免提升3%，最高可叠加5层
#===============================================================================
from Game.Fight import SkillBase

class EightStarDefendkHeroSSS(SkillBase.PassiveSkill):
	skill_id = 408
	level_to_damage_reduce_rate = {1:0.03, 2:0.06, 3:0.09, 4:0.12, 5:0.15}
	IS_MAX = 5
	
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
			fightround = 5
		self.unit.damage_reduce_rate += self.base_damage_reduce_rate + self.level_to_damage_reduce_rate.get(fightround)



if "_HasLoad" not in dir():
	EightStarDefendkHeroSSS.reg()
