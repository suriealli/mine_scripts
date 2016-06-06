#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.HuiXie")
#===============================================================================
# 回血：回复己方血量最低的单位*自己战力的X百分数
#===============================================================================
from Game.Fight import SkillBase

class HuiXie(SkillBase.ActiveSkillBase):
	skill_id = 2009			#技能ID
	skill_rate = 1.6		#技能系数（1是平衡点）
	play_time = 1.3			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 15		#需要士气
	level_to_value = [0, 0, 0, 0, 0, 0]
	level_to_attack_rate=[0, 0.8, 0.9, 1, 1.1, 1.2]
	prefix_round = 0
	is_treat = True
	
	def __init__(self, unit, argv):
		self.skill_value = int(unit.attack * self.level_to_attack_rate[argv])
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_least_hp_member()
	
	def do_effect(self, target):
		self.do_treat(target)

if "_HasLoad" not in dir():
	HuiXie.reg()
