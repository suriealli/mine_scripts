#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.ZhanLongJueA")
#===============================================================================
# 斩龙诀 攻击敌方全体目标 消耗16点怒气，无冷却CD
#===============================================================================
from Game.Fight import SkillBase

class ZhanLongJueA(SkillBase.ActiveSkillBase):
	skill_rate = 0.7		#技能系数（1是平衡点）
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	play_time = 1.4			#播放时间（秒）
	need_moral = 16		#需要士气
	is_aoe = True			#是否群攻
	aoe_need_target_cnt = 3
	level_to_value = [0, 800, 960, 1120, 1280, 1440]
	level_to_rate = [0, 0.7132, 0.7175, 0.7219, 0.7263, 0.735]
	
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[argv]
		self.skill_rate = self.level_to_rate[argv]
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)


if "_HasLoad" not in dir():
	ZhanLongJueA.reg()
