#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.AttackTwoMaybeDouble")
#===============================================================================
# 随机攻击敌方两个目标，有大概率造成2倍伤害
#===============================================================================
import random
from Game.Fight import SkillBase

class AttackTwoMaybeDouble(SkillBase.ActiveSkillBase):
	skill_id = 343			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	skill_value = 3000			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_random_enemy( n = 2 )
	
	def do_effect(self, target):
		self.do_hurt(target)
		
		
	def computer_hurt(self, target, no_defence=False):
		hurt = SkillBase.ActiveSkillBase.computer_hurt(self, target, no_defence)
		if random.randint(0, 99) < 70:
			hurt *= 2
		return hurt


if "_HasLoad" not in dir():
	AttackTwoMaybeDouble.reg()
