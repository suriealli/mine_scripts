#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.StarGirlSkill.StarGirlGongJi")
#===============================================================================
# 随机攻击单个目标1次，额外造成800点伤害,技能每提升一级，伤害提高100点，共可提升至7级
#===============================================================================
import random
from Game.Fight.ActiveSkill.StarGirlSkill import StarGirlBase

JDFY_FLAG = "JiangDiFangYu_flag"
JLNQ_FLAG = "JiLvNuQi_flag"
XY_FLAG = "XunaYun_flag"

class StarGirlGongJi(StarGirlBase.StarGirlBase):
	skill_id = 3201			#技能ID
	#skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 800			#技能绝对值
	play_time = 2.10			#播放时间（秒）
	play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 50		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_value = [0, 800, 900, 1000, 1100, 1200, 1300, 1400]
	
	def __init__(self, unit, argv):
		#设置技能系数
		self.skill_rate = unit.star_girl_skill_rate
		StarGirlBase.StarGirlBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[self.argv]
	
	def do_before(self, targets):
		UNIT = self.unit
		CAMP = self.camp
		
		if hasattr(UNIT, JDFY_FLAG):
			for target in targets:
				if target.camp is CAMP:
					continue
				target.create_buff("ReduceDefend", 2, int(0.1 * self.unit.attack))
		
		if hasattr(UNIT, JLNQ_FLAG):
			if random.randint(0, 99) < 20:
				UNIT.change_moral(25)
		
		if hasattr(UNIT, XY_FLAG):
			for target in targets:
				if target.camp is CAMP:
					continue
				target.create_stun(30, 2)
	
	def select_targets(self):
		return self.unit.select_random_enemy(1)
	
	def do_effect(self, target):
		self.do_hurt(target)


if "_HasLoad" not in dir():
	StarGirlGongJi.reg()
