#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.EightStarAuxiliaryHeroA")
#===============================================================================
# 治疗我方全体单位，并额外恢复3500生命。
#===============================================================================
from Game.Fight import SkillBase

class EightStarAuxiliaryHeroA(SkillBase.ActiveSkillBase):
	skill_id = 229			#技能ID
	skill_rate = 0.65		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 2			#CD回合数
	need_moral = 0		#需要士气
	has_buff = True		#是否附带buff
	level_to_value = [0, 0, 3500]
	level_to_prefixround = [2, 1, 0]
	is_treat = True
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_all_member()
	
	def do_effect(self, target):
		self.do_treat(target)


if "_HasLoad" not in dir():
	EightStarAuxiliaryHeroA.reg()
