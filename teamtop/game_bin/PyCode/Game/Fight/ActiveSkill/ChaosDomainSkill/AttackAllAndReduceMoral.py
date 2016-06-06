#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.AttackAllAndReduceMoral")
#===============================================================================
# 主动技能说明混沌神域技能：攻击敌方全体目标并减少目标30点怒气值
#===============================================================================
from Game.Fight import SkillBase

class AttackAllAndReduceMoral(SkillBase.ActiveSkillBase):
	skill_id = 330			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	moral_reduce = 30
	
	def __init__(self,unit,argv):
		SkillBase.ActiveSkillBase.__init__(self,unit,argv)
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		target.change_moral(-self.moral_reduce)


if "_HasLoad" not in dir():
	AttackAllAndReduceMoral.reg()
