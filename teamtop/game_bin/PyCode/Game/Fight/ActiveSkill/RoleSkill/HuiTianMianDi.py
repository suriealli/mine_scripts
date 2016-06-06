#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.HuiTianMianDi")
#===============================================================================
# 毁天灭地 群攻技能，消耗50点怒气，冷却CD3回合
#===============================================================================
from Game.Fight import SkillBase

class HuiTianMianDi(SkillBase.ActiveSkillBase):
	prefix_round = 0		#前置回合数
	cd_round = 3			#CD回合数
	play_time = 2.8			#播放时间（秒）
	need_moral = 50		#需要士气
	is_aoe = True			#是否群攻
	aoe_need_target_cnt = 2
	level_to_rate = [0, 1.4, 1.4, 1.5, 1.5, 1.55]
	level_to_value = [0, 660, 1320, 1980, 2640, 3300]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_rate = self.level_to_rate[argv]
		self.skill_value = self.level_to_value[argv]
	
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)


if "_HasLoad" not in dir():
	HuiTianMianDi.reg()
