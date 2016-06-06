#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.FiveStarAttackHeroSSS")
#===============================================================================
# 攻击敌方随机单体目标，并造成昏迷，额外造成3500点伤害，持续1回合。
#===============================================================================
from Game.Fight import SkillBase

class FiveStarAttackHeroSSS(SkillBase.ActiveSkillBase):
	skill_id = 400			#技能ID
	skill_rate = 2.0
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	has_buff = True		#是否附带buff
	level_to_value = [0, 0, 3500]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_random_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		target.create_stun(99, 2)


if "_HasLoad" not in dir():
	FiveStarAttackHeroSSS.reg()
