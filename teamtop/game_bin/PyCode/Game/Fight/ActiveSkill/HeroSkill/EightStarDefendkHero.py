#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.EightStarDefendkHero")
#===============================================================================
# 攻击敌方单体目标，为自己施放一个护盾，吸收大量伤害，并施放一个30%反伤buff，反伤最大不超过自身最大生命值。
#===============================================================================
from Game.Fight import SkillBase

class EightStarDefendkHero(SkillBase.ActiveSkillBase):
	skill_id = 231			#技能ID
	skill_rate = 1.5		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 2			#CD回合数
	need_moral = 0		#需要士气
	has_buff = True		#是否附带buff
	level_to_prefixround = [2, 1, 0]	#前置回合数
	level_to_value = [0, 0, 3500]
	level_to_back_rate = [0, 0.3, 0.3]
	
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_random_enemy(1)
	
	def do_effect(self, target):
		self.do_hurt(target)
		
	def do_after(self, targets):
		if self.unit.is_out:
			return
		argv = int(1.8 * self.unit.attack)
		buff = self.unit.create_buff("ReduceHurtAndBack", 2, argv)
		buff.strike_back = True
		buff.strike_rate = 0.3
		buff.strike_max_hp_rate = 1.0


if "_HasLoad" not in dir():
	EightStarDefendkHero.reg()
