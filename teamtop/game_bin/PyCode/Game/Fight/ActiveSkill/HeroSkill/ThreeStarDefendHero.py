#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.ThreeStarDefendHero")
#===============================================================================
# 三星防御将技能 攻击敌方全体目标，且降低敌方攻击力
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class ThreeStarDefendHero(SkillBase.ActiveSkillBase):
	skill_id = 209			#技能ID
	skill_rate = 0.3		#技能系数（1是平衡点）
	play_time = 2.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True		#是否群攻
	has_buff = True		#是否附带buff
	level_to_value = [0, 0, 200]			#技能绝对值
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		#降低敌方攻击力的BUFF
		argv = 0.2
		target.create_buff("ReduceAttack", 2, argv)

if "_HasLoad" not in dir():
	ThreeStarDefendHero.reg()
