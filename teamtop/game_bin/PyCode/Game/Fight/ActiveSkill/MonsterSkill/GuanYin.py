#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.GuanYin")
#===============================================================================
# 观音技能 攻击敌方全体目标，忽视目标防御
#===============================================================================
from Game.Fight import SkillBase

class GuanYin(SkillBase.ActiveSkillBase):
	skill_id = 304			#技能ID
	skill_rate = 0.71		#技能系数（1是平衡点）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	play_time = 1.5			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	level_to_value = [0, 0, 3000]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target, True)	#无视防御



if "_HasLoad" not in dir():
	GuanYin.reg()
