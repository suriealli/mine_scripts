#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.HuiMie")
#===============================================================================
# 群体输出技能：攻击敌方全体目标造成百分之X伤害+X伤害
#===============================================================================
from Game.Fight import SkillBase

class HuiMie(SkillBase.ActiveSkillBase):
	skill_id = 2006			#技能ID
	prefix_round = 0		#前置回合数
	cd_round = 3			#CD回合数
	play_time = 2.8			#播放时间（秒）
	need_moral = 15		#需要士气
	is_aoe = True			#是否群攻
	aoe_need_target_cnt = 3
	level_to_rate = [0, 0.5, 0.5, 0.5, 0.5, 0.5]
	level_to_value = [0, 200, 400, 600, 800, 1000]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_rate = self.level_to_rate[argv]
		self.skill_value = self.level_to_value[argv]
	
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)

if "_HasLoad" not in dir():
	HuiMie.reg()
