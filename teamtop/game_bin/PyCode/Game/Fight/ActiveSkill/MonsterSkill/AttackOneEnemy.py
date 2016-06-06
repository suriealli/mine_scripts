#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.AttackOneEnemy")
#===============================================================================
# 秒1技能，无技能ID，纯用于调用
# 怪物技能的ID从1000开始
#===============================================================================
from Game.Fight import SkillBase

class AttackOneEnemy(SkillBase.ActiveSkillBase):
	skill_rate = 1.0		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_random_enemy(n = 1)
	
	def do_effect(self, target):
		self.do_hurt(target)


if "_HasLoad" not in dir():
	AttackOneEnemy.reg()
