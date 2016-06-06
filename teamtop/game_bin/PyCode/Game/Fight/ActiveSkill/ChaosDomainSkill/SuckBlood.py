#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.SuckBlood")
#===============================================================================
# 混沌神域技能：每回合吸血
#===============================================================================
from Game.Fight import SkillBase

class SuckBlood(SkillBase.ActiveSkillBase):
	skill_id = 345			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	skill_value = 2220			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def need_treat(self):
		return self.unit.hp < int(0.8 * self.unit.max_hp)
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		self.do_treat(self.unit)
		self.unit.create_buff("AddDefend", 3, 500)


if "_HasLoad" not in dir():
	SuckBlood.reg()
