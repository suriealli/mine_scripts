#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SevenStarAuxiliaryHero")
#===============================================================================
# 为我方全体目标持续回复生命值，并增加目标的攻击力，持续3回合
#===============================================================================
from Game.Fight import SkillBase

class SevenStarAuxiliaryHero(SkillBase.ActiveSkillBase):
	skill_id = 223			#技能ID
	skill_rate = 0.35		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	has_buff = True		#是否附带buff
	level_to_value = [0, 0, 3000]
	level_to_prefixround = [2, 1, 0]
	is_treat = True
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.add_attack = int(self.skill_rate * self.unit.attack)
		
		
	
	def select_targets(self):
		return self.unit.select_all_member()
	
	def do_effect(self, target):
		self.do_treat(target)
		argv = int(0.35 * self.unit.attack + self.skill_value)
		target.create_buff("HealthPerRound", 3, argv)
		target.create_buff("AddAttackAndCrit", 3, self.add_attack)


if "_HasLoad" not in dir():
	SevenStarAuxiliaryHero.reg()
