#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.EightStarDefendHeroBBSSS")
#===============================================================================
# 分担队友承受伤害的百分之X，最大不超过自己当前生命，持续2回合。增加临时生命值50%，持续2回合
#===============================================================================
from Game.Fight import SkillBase

class EightStarDefendHeroBBSSS(SkillBase.ActiveSkillBase):
	skill_id = 411			#技能ID
	skill_rate = 0.56		#技能系数（1是平衡点）
	play_time = 1.3			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	level_to_prefixround = [2, 1, 0]			#前置回合
	level_to_connect_rate = [0, 0.5, 0.5]
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_random_member_exclude_self(n=3)
	
	def do_effect(self, target):
		target.create_buff("HurtConnect", 2, ("EightStarDefendHeroBBSSS", 1, self.level_to_connect_rate[self.argv], self.unit))
		self.unit.create_buff("AddHp", 2, 0.5)


if "_HasLoad" not in dir():
	EightStarDefendHeroBBSSS.reg()
