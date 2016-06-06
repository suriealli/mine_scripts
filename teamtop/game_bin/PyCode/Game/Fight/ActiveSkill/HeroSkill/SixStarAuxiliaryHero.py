#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SixStarAuxiliaryHero")
#===============================================================================
# 六星辅将技能 治疗我方生命最低的两个单位
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class SixStarAuxiliaryHero(SkillBase.ActiveSkillBase):
	skill_id = 221			#技能ID
	skill_rate = 1.8		#技能系数（1是平衡点）
	cd_round = 3			#CD回合数
	need_moral =0		#需要士气
	is_treat = True
	level_to_value = [0, 0, 2500]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_least_hp_member(n = 2)
	
	def do_effect(self, target):
		self.do_treat(target)


if "_HasLoad" not in dir():
	SixStarAuxiliaryHero.reg()
