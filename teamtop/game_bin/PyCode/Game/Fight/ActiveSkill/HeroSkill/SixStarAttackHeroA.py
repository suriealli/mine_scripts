#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SixStarAttackHeroA")
#===============================================================================
# 六星攻将技能A 攻击敌方全体目标且降低目标的防御值，额外造成2500点伤害
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class SixStarAttackHeroA(SkillBase.ActiveSkillBase):
	skill_id = 218			#技能ID
	skill_rate = 0.7		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	has_buff = True			#是否群攻
	level_to_value = [0, 0, 2500]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		#被攻击单位获得BUFF，降低防御2个回合
		argv = int(0.2 * self.unit.attack)
		target.create_buff("ReduceDefend", 2, argv)


if "_HasLoad" not in dir():
	SixStarAttackHeroA.reg()
