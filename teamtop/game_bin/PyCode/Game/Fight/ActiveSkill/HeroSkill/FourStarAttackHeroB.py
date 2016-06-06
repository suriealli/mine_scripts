#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.FourStarAttackHeroB")
#===============================================================================
# 四星攻将大法师技能B 随机攻击敌方两个目标，有大概率造成2倍伤害值
# 英雄技能的ID从200开始
#===============================================================================
import random
from Game.Fight import SkillBase, Operate

class FourStarAttackHeroB(SkillBase.ActiveSkillBase):
	skill_id = 212			#技能ID
	skill_rate = 0.85		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	level_to_value = [0, 0, 1800]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_random_enemy(n = 2)
	
	def do_effect(self, target):
		self.do_hurt(target)
	
	# 通用造成伤害流程
	def computer_hurt(self, target, no_defence=False):
		hurt = SkillBase.ActiveSkillBase.computer_hurt(self, target, no_defence)
		if random.randint(0, 99) < 70:
			hurt *= 2
		return hurt

if "_HasLoad" not in dir():
	FourStarAttackHeroB.reg()
