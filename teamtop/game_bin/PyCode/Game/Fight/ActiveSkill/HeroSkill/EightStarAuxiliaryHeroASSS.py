#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.EightStarAuxiliaryHeroASSS")
#===============================================================================
# 治疗我方全体单位，并额外恢复3500生命。持续回复生命值，持续3回合
#===============================================================================
from Game.Fight import SkillBase

class EightStarAuxiliaryHeroASSS(SkillBase.ActiveSkillBase):
	skill_id = 410			#技能ID
	skill_rate = 0.25		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
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
		argv = int(0.165 * self.unit.attack + self.skill_value)
		target.create_buff("HealthPerRound", 2, argv)


if "_HasLoad" not in dir():
	EightStarAuxiliaryHeroASSS.reg()
