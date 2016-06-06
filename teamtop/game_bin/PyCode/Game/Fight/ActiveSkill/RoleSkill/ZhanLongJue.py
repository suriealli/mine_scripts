#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.ZhanLongJue")
#===============================================================================
# 斩龙诀 攻击敌方全体目标 消耗16点怒气，无冷却CD
#===============================================================================
from Game.Fight import SkillBase

class ZhanLongJue(SkillBase.ActiveSkillBase):
	skill_rate = 0.7		#技能系数（1是平衡点）
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	play_time = 1.4			#播放时间（秒）
	need_moral = 16		#需要士气
	is_aoe = True			#是否群攻
	aoe_need_target_cnt = 3
	level_to_value = [0, 0, 160, 320, 480, 640]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[argv]
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)


if "_HasLoad" not in dir():
	ZhanLongJue.reg()
