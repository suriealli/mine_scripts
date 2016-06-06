#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.AttackRandomAndPoison")
#===============================================================================
# 混沌神域技能，随机攻击一个目标，并添加中毒debuff
#===============================================================================
from Game.Fight import SkillBase

class AttackRandomAndPoison(SkillBase.ActiveSkillBase):
	skill_id = 337			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = False			#是否群攻
	has_buff = True		#是否附带buff
	poisonous_rate = 0.15 #每回合中毒掉血百分比
	
	def __init__(self,unit,argv):
		SkillBase.ActiveSkillBase.__init__(self,unit,argv)
	
	def select_targets(self):
		return self.unit.select_random_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		argv = int(self.poisonous_rate * target.max_hp)
		target.create_buff("Poisonous", 3 ,argv)


if "_HasLoad" not in dir():
	AttackRandomAndPoison.reg()
