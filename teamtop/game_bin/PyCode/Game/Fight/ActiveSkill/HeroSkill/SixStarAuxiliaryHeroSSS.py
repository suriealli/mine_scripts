#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SixStarAuxiliaryHeroSSS")
#===============================================================================
# 治疗我方生命值最低的两个单位。并额外回复3000生命值，并持续回复生命值，持续2回合
#===============================================================================
from Game.Fight import SkillBase

class SixStarAuxiliaryHeroSSS(SkillBase.ActiveSkillBase):
	skill_id = 405			#技能ID
	skill_rate = 1.9		#技能系数（1是平衡点）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_treat = True
	level_to_value = [0, 0, 3000]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_least_hp_member(n=2)
	
	def do_effect(self, target):
		self.do_treat(target)
		argv = int(0.18 * self.unit.attack + self.skill_value)
		target.create_buff("HealthPerRound", 2, argv)


if "_HasLoad" not in dir():
	SixStarAuxiliaryHeroSSS.reg()
