#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.NeZa")
#===============================================================================
# 哪吒单体加攻击的技能
# 怪物技能的ID从1000开始
#===============================================================================
from Game.Fight import SkillBase

class NeZa(SkillBase.ActiveSkillBase):
	skill_id = 303			#技能ID
	skill_rate = 0.6		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	level_to_prefixround = [2, 1, 0]		#前置回合数
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_self()
	
	def do_effect(self, target):
		argv = int(self.skill_rate * self.unit.attack + self.skill_value)
		target.create_buff("AddAttack", 2, argv)


if "_HasLoad" not in dir():
	NeZa.reg()
