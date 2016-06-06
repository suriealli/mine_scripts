#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SevenStarAuxiliaryHeroSSS")
#===============================================================================
# 给我方全体目标释放一个护盾，额外吸收3500点伤害，持续3回合。
#===============================================================================
from Game.Fight import SkillBase

class SevenStarAuxiliaryHeroSSS(SkillBase.ActiveSkillBase):
	skill_id = 407			#技能ID
	skill_rate = 0.5		#技能系数（1是平衡点）
	play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	has_buff = True		#是否附带buff
	level_to_value = [0, 0, 1000]			#技能绝对值
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_all_member()
	
	def do_effect(self, target):
		argv = int(self.skill_rate * self.unit.attack + self.skill_value)
		target.create_buff("ReduceHurt", 3, argv)


if "_HasLoad" not in dir():
	SevenStarAuxiliaryHeroSSS.reg()
