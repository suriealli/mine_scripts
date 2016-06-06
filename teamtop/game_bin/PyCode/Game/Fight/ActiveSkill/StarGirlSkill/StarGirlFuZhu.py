#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.StarGirlSkill.StarGirlFuZhu")
#===============================================================================
# 血量最少1个单位10000点生命
#===============================================================================
import random
from Game.Fight.ActiveSkill.StarGirlSkill import StarGirlBase

JLNQ_FLAG = "JiLvNuQi_flag"
EWHF_FLAG = "EWaiHuiFu_flag"
QCFM_FLAG = "QuChuFuMian_flag"
EWJX_FLAG = "EWaiJiaXue_flag"

class StarGirlFuZhu(StarGirlBase.StarGirlBase):
	skill_id = 3202			#技能ID
	#skill_rate = 0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 2.10			#播放时间（秒）
	play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 50		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_value = [0, 3000, 5000, 7000, 9000, 11000, 13000, 15000]
	is_treat = True
	
	def __init__(self, unit, argv):
		#设置技能系数
		self.skill_rate = unit.star_girl_skill_rate
		StarGirlBase.StarGirlBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[self.argv]
		
	def do_before(self, targets):
		UNIT = self.unit
		
		if hasattr(UNIT, JLNQ_FLAG):
			if random.randint(0, 99) < 20:
				UNIT.change_moral(25)
	
	def select_targets(self):
		return self.unit.select_least_hp_member(n=1)
	
	def do_effect(self, target):
		# 计算被动技能带来的额外数值
		a = 0
		b = 0
		value = self.level_to_value[self.argv]
		if hasattr(self.unit, EWHF_FLAG):
			a = 5000
		if hasattr(self.unit, EWJX_FLAG):
			b = int(0.12 * self.unit.attack)
		value = value + a + b
		self.skill_value = value
		self.do_treat(target)
		
		if hasattr(self.unit, QCFM_FLAG):
			target.clear_buff(buff_info=False)
		
		


if "_HasLoad" not in dir():
	StarGirlFuZhu.reg()
