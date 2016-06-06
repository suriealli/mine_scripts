#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.AttackAllEnemyPerTwoRound")
#===============================================================================
# 混沌神域技能，每2回合群攻一次
#===============================================================================
from Game.Fight import SkillBase

class AttackAllEnemyPerTwoRound(SkillBase.ActiveSkillBase):
	skill_id = 332			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 1			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	#has_buff = False		#是否附带buff
	
	def __init__(self,unit,argv):
		SkillBase.ActiveSkillBase.__init__(self,unit,argv)
	
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)


if "_HasLoad" not in dir():
	AttackAllEnemyPerTwoRound.reg()
