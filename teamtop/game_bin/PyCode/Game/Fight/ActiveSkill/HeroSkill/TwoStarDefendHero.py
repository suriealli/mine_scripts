#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.TwoStarDefendHero")
#===============================================================================
# 二星防将技能 获得一个吸收伤害的保护罩
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class TwoStarDefendHero(SkillBase.ActiveSkillBase):
	skill_id = 206			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	play_time = 1.5			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	has_buff = True		#是否附带buff
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_self()
	
	def do_effect(self, target):
		argv = int(self.skill_rate * self.unit.attack + self.skill_value)
		#玩家获得一个BUFF，吸收伤害值
		target.create_buff("ReduceHurt", 3, argv)


if "_HasLoad" not in dir():
	TwoStarDefendHero.reg()
