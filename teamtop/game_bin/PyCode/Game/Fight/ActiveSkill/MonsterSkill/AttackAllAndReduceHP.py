#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.AttackAllAndReduceHP")
#===============================================================================
# 龙骑试炼13关技能，攻击敌方全体，专治各种带天鹅
#===============================================================================
from Game.Fight import SkillBase

class AttackAllAndReduceHP(SkillBase.ActiveSkillBase):
	skill_id = 313			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	skill_value = 25000			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_life_decrease_rate = [0, 0.03, 0.04, 0.05, 0.06, 0.08, 0.05, 0.06, 0.07, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2] #处理天鹅座回血
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		level = 0
		for tps in target.passive_skills:
			if tps.skill_id == 814:
				level = tps.argv
				break
		target.change_hp(-int(self.level_to_life_decrease_rate[level] * target.max_hp))


if "_HasLoad" not in dir():
	AttackAllAndReduceHP.reg()
