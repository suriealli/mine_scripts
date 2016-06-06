#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SevenStarAttackHero")
#===============================================================================
# 攻击3次敌方随机单体目标，额外造成3000点伤害，并有几率造成昏迷，持续2回合。
#===============================================================================
from Game.Fight import SkillBase

class SevenStarAttackHero(SkillBase.ActiveSkillBase):
	skill_id = 222			#技能ID
	skill_rate = 1.0
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	level_to_value = [0, 0, 3000]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_random_enemy(n=3)
	
	def do_effect(self, target):
		self.do_hurt(target)
		target.create_stun(20, 2)


if "_HasLoad" not in dir():
	SevenStarAttackHero.reg()
