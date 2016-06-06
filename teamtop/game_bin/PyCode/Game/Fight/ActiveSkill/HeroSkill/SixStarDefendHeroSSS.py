#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SixStarDefendHeroSSS")
#===============================================================================
# 攻击敌方前排随机单体目标，额外造成3500点伤害，并恢复自身生命值。
#===============================================================================
from Game.Fight import SkillBase

class SixStarDefendHeroSSS(SkillBase.ActiveSkillBase):
	skill_id = 402			#技能ID
	skill_rate = 0.8		#技能系数（1是平衡点）
	play_time = 1.9			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_treat = True		#是治疗
	level_to_prefixround = [2, 1, 0]	#前置回合数
	level_to_hurt_value = [0, 0, 600]
	level_to_treat_value = [0, 0, 700]
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.skill_value = self.level_to_hurt_value[self.argv]
		self.skill_rate = 2.0
		self.do_hurt(target)
		
		self.skill_value = self.level_to_treat_value[self.argv]
		self.skill_rate = 1.8
		self.do_treat(self.unit)


if "_HasLoad" not in dir():
	SixStarDefendHeroSSS.reg()
