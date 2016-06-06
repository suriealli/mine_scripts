#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.TwoStarAttackHero")
#===============================================================================
# 二星攻将技能 攻击随机三个目标且降级目标的防御值
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class TwoStarAttackHero(SkillBase.ActiveSkillBase):
	skill_id = 204			#技能ID
	skill_rate = 0.6		#技能系数（1是平衡点）
	play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	has_buff = True		#是否附带buff
	level_to_value = [0, 0, 1300]
	level_to_prefixround = [2, 1, 0] 
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_random_enemy(n = 3)
	
	def do_effect(self, target):
		self.do_hurt(target)
		#被攻击单位获得BUFF，降低防御2个回合
		argv = int(0.2 * self.unit.attack)
		target.create_buff("ReduceDefend", 2, argv)

if "_HasLoad" not in dir():
	TwoStarAttackHero.reg()
