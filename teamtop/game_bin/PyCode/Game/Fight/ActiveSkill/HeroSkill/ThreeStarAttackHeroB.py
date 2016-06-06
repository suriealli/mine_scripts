#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.ThreeStarAttackHeroB")
#===============================================================================
# 三星攻将技能B 攻击敌方一个竖排的目标，且攻击时无视防御
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class ThreeStarAttackHeroB(SkillBase.ActiveSkillBase):
	skill_id = 208			#技能ID
	skill_rate = 2.0		#技能系数（1是平衡点）
	cd_round = 2			#CD回合数
	need_moral = 0		#需要士气
	play_time = 1.4
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_value = [0, 0, 2400]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_cell_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target, True)

if "_HasLoad" not in dir():
	ThreeStarAttackHeroB.reg()
