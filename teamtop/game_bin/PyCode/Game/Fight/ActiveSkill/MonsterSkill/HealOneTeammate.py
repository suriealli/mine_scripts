#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.HealOneTeammate")
#===============================================================================
# 怪物治疗单体目标
# 怪物技能的ID从1000开始
#===============================================================================
from Game.Fight import SkillBase

class HealOneTeammate(SkillBase.ActiveSkillBase):
	skill_rate = 9		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	level_to_value = [0, 0, 500]
	level_to_prefixround = [2, 1, 0]
	is_treat = True
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_least_hp_member()
	
	def do_effect(self, target):
		self.do_treat(target)


if "_HasLoad" not in dir():
	HealOneTeammate.reg()
