#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.Damage70Percent")
#===============================================================================
# 混沌神域技能，第4回合释放，造成当前血量70%的伤害
#===============================================================================
from Game.Fight import SkillBase

class Damage70Percent(SkillBase.ActiveSkillBase):
	skill_id = 335			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 3		#前置回合数
	cd_round = 999			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	#has_buff = False		#是否附带buff
	damage_rate = 0.7
	
	def __init__(self,unit,argv):
		SkillBase.ActiveSkillBase.__init__(self,unit,argv)
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		hp_reduce = int(target.hp * self.damage_rate)
		target.change_hp(-hp_reduce)


if "_HasLoad" not in dir():
	Damage70Percent.reg()
