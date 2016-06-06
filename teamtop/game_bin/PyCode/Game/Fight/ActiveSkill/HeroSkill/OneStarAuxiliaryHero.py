#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.OneStarAuxiliaryHero")
#===============================================================================
# 一星辅将技能 给己方全体提升攻击力
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class OneStarAuxiliaryHero(SkillBase.ActiveSkillBase):
	skill_id = 202			#技能ID
	skill_rate = 0.2		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.2			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	has_buff = True		#是否附带buff
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_all_member()
	
	def do_effect(self, target):
		argv = int(self.skill_rate * self.unit.attack + self.skill_value)
		target.create_buff("AddAttack", 2, argv)


if "_HasLoad" not in dir():
	OneStarAuxiliaryHero.reg()
