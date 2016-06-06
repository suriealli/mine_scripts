#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.StarGirlSkill.StarGirlGongJiShiZiZuo")
#===============================================================================
# 主动技能说明
#===============================================================================
import random
from Game.Fight.ActiveSkill.StarGirlSkill import StarGirlBase

JDFYSZZ_FLAG = "jiangdifangyuShiZiZuo_flag"
JLNQ_FLAG = "JiLvNuQi_flag"
XY_FLAG = "XunaYun_flag"

class StarGirlGongJiShiZiZuo(StarGirlBase.StarGirlBase):
	skill_id = 3205			#技能ID
	#skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 800			#技能绝对值
	#play_time = 1.0			#播放时间（秒）
	play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 50		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_value = [0, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500]
	
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
	
	def do_after(self, targets):
		UNIT = self.unit
		CAMP = self.camp
		if hasattr(UNIT, XY_FLAG):
			for target in targets:
				if target.camp is CAMP:
					continue
				target.create_stun(30, 2)
	
	def do_effect(self, target):
		if hasattr(self.unit, JDFYSZZ_FLAG) and (target.camp is self.other_camp):
			target.create_buff("ReduceDefend", 2, int(0.15 * self.unit.attack))
		self.do_hurt(target)
	
	# 释放技能
	def do(self):
		self.do_cnt(2)

if "_HasLoad" not in dir():
	StarGirlGongJiShiZiZuo.reg()
