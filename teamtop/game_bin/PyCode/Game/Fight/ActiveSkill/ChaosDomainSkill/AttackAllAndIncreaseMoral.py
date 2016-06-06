#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.AttackAllAndIncreaseMoral")
#===============================================================================
# 混沌神域技能：对全体目标造成伤害，且有概率眩晕，同时回复目标20点怒气
#===============================================================================
from Game.Fight import SkillBase

class AttackAllAndIncreaseMoral(SkillBase.ActiveSkillBase):
	skill_id = 333			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True	
	stun_rate = 25			#眩晕概率		#是否群攻
	#has_buff = False		
	add_moral = 20		#增加怒气
	
	def __init__(self,unit,argv):
		SkillBase.ActiveSkillBase.__init__(self,unit,argv)#是否附带buff
	
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		target.change_moral(self.add_moral)
		target.create_stun(self.stun_rate,2 , 18)


if "_HasLoad" not in dir():
	AttackAllAndIncreaseMoral.reg()
