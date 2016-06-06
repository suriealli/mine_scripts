#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.NiTianShaShen")
#===============================================================================
# 逆天杀神 攻击先前排再后排的目标，消耗40点怒气，冷却CD3个回合
#===============================================================================
from Game.Fight import SkillBase

class NiTianShaShen(SkillBase.ActiveSkillBase):
	skill_rate = 3.0		#技能系数（1是平衡点）
	prefix_round = 0		#前置回合数
	cd_round = 3			#CD回合数
	play_time = 3.0			#播放时间（秒）
	need_moral = 40		#需要士气
	level_to_value = [0, 560, 1120, 1680, 2240, 2800]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[argv]
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)


if "_HasLoad" not in dir():
	NiTianShaShen.reg()
