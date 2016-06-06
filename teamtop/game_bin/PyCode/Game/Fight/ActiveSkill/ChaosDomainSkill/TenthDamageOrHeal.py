#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.TenthDamageOrHeal")
#===============================================================================
# 混沌神域技能，攻击全体目标，50%概率造成10倍伤害，50%概率治疗目标
#===============================================================================
import random
from Game.Fight import SkillBase

class TenthDamageOrHeal(SkillBase.ActiveSkillBase):
	skill_id = 334			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	#has_buff = False		#是否附带buff
	tenth_damage_rate = 50	#造成10倍伤害的概率
	
	def __init__(self,unit,argv):
		SkillBase.ActiveSkillBase.__init__(self,unit,argv)
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		if random.randint(0,99) < self.tenth_damage_rate:
			self.skill_rate += 9
			self.do_hurt(target)
			self.skill_rate -= 9
		else:
			self.do_treat(target)


if "_HasLoad" not in dir():
	TenthDamageOrHeal.reg()
