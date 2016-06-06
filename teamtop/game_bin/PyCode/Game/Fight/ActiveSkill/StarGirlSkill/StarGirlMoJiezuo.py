#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.StarGirlSkill.StarGirlMoJiezuo")
#===============================================================================
# 为己方一个单位恢复生命值，并持续回血一定血量，持续2回合。
#===============================================================================
import random
from Game.Fight.ActiveSkill.StarGirlSkill import StarGirlBase

JLNQ_FLAG = "JiLvNuQi_flag"
QCFM_FLAG = "QuChuFuMian_flag"
EWJX_FLAG = "EWaiJiaXueMoJieZuo_flag"
CXHX_FLAG = "ChiXuHuiXueMoJieZuo_flag"

class StarGirlMoJiezuo(StarGirlBase.StarGirlBase):
	skill_id = 3206			#技能ID
	#skill_rate = 0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 2.10			#播放时间（秒）
	play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 50		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_value = [0, 3000, 5000, 7000, 9000, 11000, 13000, 15000, 17000, 19000]
	is_treat = True
	
	def __init__(self, unit, argv):
		#设置技能系数
		self.extend_target = False
		StarGirlBase.StarGirlBase.__init__(self, unit, argv)
		
	def do_before(self, targets):
		UNIT = self.unit
		
		if hasattr(UNIT, JLNQ_FLAG):
			if random.randint(0, 99) < 20:
				UNIT.change_moral(25)
	
	def select_targets(self):
		self.extend_target = False
		if hasattr(self.unit, "ZengJiaMuBiaoMoJieZuo_flag"):
			return self.unit.select_least_hp_member(2)
		else:
			return self.unit.select_least_hp_member(1)
	
	def do_effect(self, target):
		# 计算被动技能带来的额外数值
		b = 0
		self.skill_rate = self.unit.star_girl_skill_rate
		self.skill_value = self.level_to_value[self.argv]
		if hasattr(self.unit, EWJX_FLAG):
			b = int(0.2 * self.unit.attack)
		self.skill_value = self.skill_value + b
		# 计算被动带来的额外回血效果
		passive_rate = (self.skill_rate / 10) + getattr(self.unit, "ChiXuHuiXueMoJieZuo_flag", 0.0)
		argv = int(passive_rate * self.unit.attack)
		# 如果是额外目标，效果减半
		if self.extend_target:
			self.skill_rate /= 2
			self.skill_value /= 2
			argv /= 2
		else:
			self.extend_target = True
		# 治疗
		self.do_treat(target)
		# 持续回血
		target.create_buff("HealthPerRound", 2, argv)
		
		if hasattr(self.unit, QCFM_FLAG):
			target.clear_buff(buff_info=False)


if "_HasLoad" not in dir():
	StarGirlMoJiezuo.reg()
