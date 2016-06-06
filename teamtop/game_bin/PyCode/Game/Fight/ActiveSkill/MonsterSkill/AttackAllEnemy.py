#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.AttackAllEnemy")
#===============================================================================
# 攻击敌方全体目标，每回合发动。
#===============================================================================
from Game.Fight import SkillBase

class AttackAllEnemy(SkillBase.ActiveSkillBase):
	skill_id = 308
	skill_rate = 0.84
	cd_round = 0
	need_moral = 0
	play_time = 1.5
	level_to_value = [0, 0, 3000]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_all_enemy()

	def do_effect(self, target):
		self.do_hurt(target)




if "_HasLoad" not in dir():
	AttackAllEnemy.reg()
