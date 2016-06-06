#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.FiveStarAuxiliaryHeroSSS")
#===============================================================================
# 治疗我方单体目标，额外回复3500点生命值
#===============================================================================
from Game.Fight import SkillBase

class FiveStarAuxiliaryHeroSSS(SkillBase.ActiveSkillBase):
	skill_id = 401			#技能ID
	skill_rate = 2.2
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_treat = True
	level_to_value = [0, 0, 3500]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_least_hp_member(n=1)
	
	def do_effect(self, target):
		self.do_treat(target)


if "_HasLoad" not in dir():
	FiveStarAuxiliaryHeroSSS.reg()
