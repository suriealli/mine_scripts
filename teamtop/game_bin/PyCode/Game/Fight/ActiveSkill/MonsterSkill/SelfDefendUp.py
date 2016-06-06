#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.SelfDefendUp")
#===============================================================================
# 提升自身防御的技能
#===============================================================================
from Game.Fight import SkillBase

class SelfDefendUp(SkillBase.ActiveSkillBase):
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	#play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	
	def select_targets(self):
		return self.unit.select_self()
	
	def do_effect(self, target):
		argv = int(self.skill_rate * self.unit.attack + self.skill_value)
		target.create_buff("AddDefend", 2, argv)


if "_HasLoad" not in dir():
	SelfDefendUp.reg()
