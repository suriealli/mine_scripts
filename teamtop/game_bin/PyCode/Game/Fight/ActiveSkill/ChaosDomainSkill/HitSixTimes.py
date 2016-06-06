#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.ChaosDomainSkill.HitSixTimes")
#===============================================================================
# 打六下
#===============================================================================
from Game.Fight import SkillBase
from Util import Random

class HitSixTimes(SkillBase.ActiveSkillBase):
	skill_id = 339			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	random_cnt_rate = [(20,3), (60,4), (15,5), (5,6)]#多少概率打几次
	
	def __init__(self,unit,argv):
		SkillBase.ActiveSkillBase.__init__(self,unit,argv)
		randomValue = Random.RandomRate()
		for rate,value in self.random_cnt_rate:
			randomValue.AddRandomItem(rate, value)
		self.random_cnt = randomValue.RandomOne()
		
	def do(self):
		self.do_cnt(self.random_cnt)
		
	def select_targets(self):
		return self.unit.select_random_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)


if "_HasLoad" not in dir():
	HitSixTimes.reg()
