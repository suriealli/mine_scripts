#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.AddDoubleDamageBuff")
#===============================================================================
# 混沌神域技能，第四回合释放一次，增己方全体伤害100%
#===============================================================================
from Game.Fight import SkillBase

class AddDoubleDamageBuff(SkillBase.ActiveSkillBase):
	skill_id = 331			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 3		#前置回合数
	cd_round = 999			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	has_buff = True		#是否附带buff
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.add_damage = 1
		
	def select_targets(self):
		return self.unit.select_all_member()
	
	def do_effect(self, target):
		target.create_buff("AddDemage",999 , self.add_damage)


if "_HasLoad" not in dir():
	AddDoubleDamageBuff.reg()
