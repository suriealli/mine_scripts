#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.EightStarAttackHero")
#===============================================================================
# 攻击六次敌方随机单体目标，前三次攻击必中，后三次攻击命中降低。
#===============================================================================
from Util import Random
from Game.Fight import SkillBase

class EightStarAttackHero(SkillBase.ActiveSkillBase):
	skill_id = 232			#技能ID
	skill_rate = 0.85		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	#play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	#prefix_round = 999		#前置回合数
	cd_round = 2			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.random_cnt = random_cnt_1
		if argv == 2:
			self.random_cnt = random_cnt_2
	
	def do(self):
		self.do_cnt(self.random_cnt.RandomOne())
	
	def select_targets(self):
		return self.unit.select_random_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)

if "_HasLoad" not in dir():
	random_cnt_1 = Random.RandomRate()
	random_cnt_1.AddRandomItem(20, 3)
	random_cnt_1.AddRandomItem(60, 4)
	random_cnt_1.AddRandomItem(15, 5)
	random_cnt_1.AddRandomItem(5, 6)
	
	random_cnt_2 = Random.RandomRate()
	random_cnt_2.AddRandomItem(20, 3)
	random_cnt_2.AddRandomItem(60, 4)
	random_cnt_2.AddRandomItem(15, 5)
	random_cnt_2.AddRandomItem(5, 6)
	
	EightStarAttackHero.reg()
