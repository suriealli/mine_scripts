#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.StarGirlSkill.StarGirlShuangYuZuo")
#===============================================================================
#  随机给一个英雄或主角增加一个吸收护盾，多个护盾效果独立计算——双鱼座
#===============================================================================
import random
from Game.Fight.ActiveSkill.StarGirlSkill import StarGirlBase

ZJXS_FLAG = "ZengJiaXiShou_flag"
JLNQ_FLAG = "JiLvNuQi_flag"
EWXS_FLAG = "EWaiXiShou_flag"
FTSH_FLAG = "FanTanShangHai_flag"

class StarGirlShuangYuZuo(StarGirlBase.StarGirlBase):
	skill_id = 3207			#技能ID
	#skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 2.10			#播放时间（秒）
	play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 50		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_value = [0, 10000, 12000, 14000, 16000, 18000, 20000, 22000, 24000, 26000, 28000]
	
	def __init__(self, unit, argv):
		#设置技能系数
		self.skill_rate = unit.star_girl_skill_rate
		StarGirlBase.StarGirlBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[self.argv]
	
	def do_before(self, targets):
		if hasattr(self.unit, JLNQ_FLAG):
			if random.randint(0, 99) < 20:
				self.unit.change_moral(25)
	
	def select_targets(self):
		return self.unit.select_least_hp_member(1)
	
	def do_effect(self, target):
		rate = self.skill_rate
		value = self.level_to_value[self.argv]
		# 计算被动技能带来的额外数值
		if hasattr(self.unit, ZJXS_FLAG):
			rate *= 1.5
		if hasattr(self.unit, EWXS_FLAG):
			value += int(0.1 * self.unit.attack)
		argv = int(rate * self.unit.attack + value)
		# 构建Buff
		buff = target.create_buff("ReduceHurtAndBack", 2, argv)
		# 设置是否反弹伤害
		buff.strike_back = hasattr(self.unit, FTSH_FLAG)


if "_HasLoad" not in dir():
	StarGirlShuangYuZuo.reg()
