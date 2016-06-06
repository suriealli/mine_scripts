#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.LongHou")
#===============================================================================
# 单体输出：攻击敌方前排目标，造成百分之X攻击伤害+X伤害
#===============================================================================
from Game.Fight import SkillBase

class LongHou(SkillBase.ActiveSkillBase):
	skill_id = 2005			#技能ID
	prefix_round = 0		#前置回合数
	cd_round = 3			#CD回合数
	play_time = 2.8			#播放时间（秒）
	need_moral = 15		#需要士气
	level_to_rate = [0, 1.6, 1.6, 1.6, 1.6, 1.6]
	level_to_value = [0, 600, 1200, 1800, 2400, 3000]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_rate = self.level_to_rate[argv]
		self.skill_value = self.level_to_value[argv]
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)

if "_HasLoad" not in dir():
	LongHou.reg()
