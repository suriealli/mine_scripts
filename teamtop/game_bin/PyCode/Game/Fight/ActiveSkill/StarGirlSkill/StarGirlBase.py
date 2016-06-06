#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.StarGirlSkill.StarGirlBase")
#===============================================================================
# 主动技能说明
#===============================================================================
from Game.Fight import SkillBase

class StarGirlBase(SkillBase.ActiveSkillBase):
	skill_id = 8800			#技能ID
	play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 50			#需要士气
	
	def can_do(self):
		return self.unit.moral >= self.need_moral
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)

if "_HasLoad" not in dir():
	StarGirlBase.reg()
