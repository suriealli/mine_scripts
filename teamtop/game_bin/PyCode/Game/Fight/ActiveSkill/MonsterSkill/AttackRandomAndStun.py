#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.AttackRandomAndStun")
#===============================================================================
# 龙骑试炼13关技能：攻击随机目标，CD3回合，概率造成眩晕
#===============================================================================
from Game.Fight import SkillBase

class AttackRandomAndStun(SkillBase.ActiveSkillBase):
	skill_id = 312			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	skill_value = 50000			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	level_prefix_round = [2, 1, 0]		#前置回合数
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	stun_rate = 95		#眩晕概率
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_prefix_round[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_random_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		target.create_stun(self.stun_rate,2 , 18)


if "_HasLoad" not in dir():
	AttackRandomAndStun.reg()
