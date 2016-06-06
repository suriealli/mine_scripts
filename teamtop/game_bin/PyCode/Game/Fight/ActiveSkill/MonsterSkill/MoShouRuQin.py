#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.MoShouRuQin")
#===============================================================================
# 秒杀技能 4回合之后直接秒杀全部在场单位
# 怪物技能的ID从1000开始
#===============================================================================
from Game.Fight import SkillBase

class MoShouRuQin(SkillBase.ActiveSkillBase):
	skill_id = 302			#技能ID
	prefix_round = 3		#前置回合数
	cd_round = 0		#冷却回合数
	need_moral = 0		#需要士气
	is_aoe = False			#是否群攻
	
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		target.hurt(99999999999, self.unit)


if "_HasLoad" not in dir():
	MoShouRuQin.reg()
