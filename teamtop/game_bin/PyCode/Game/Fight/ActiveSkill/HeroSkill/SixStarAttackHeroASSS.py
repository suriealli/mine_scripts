#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SixStarAttackHeroASSS")
#===============================================================================
# 攻击敌方全体目标，并降低敌方防御、消耗对方主角30点怒气，额外造成3500点伤害。
#===============================================================================
from Game.Fight import SkillBase

class SixStarAttackHeroASSS(SkillBase.ActiveSkillBase):
	skill_id = 403			#技能ID
	skill_rate = 0.8		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	has_buff = True			#是否群攻
	level_to_value = [0, 0, 3500]
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
		# 如果是主角，减士气
		if target.unit_type == 1:
			target.change_moral(-30)

if "_HasLoad" not in dir():
	SixStarAttackHeroASSS.reg()
