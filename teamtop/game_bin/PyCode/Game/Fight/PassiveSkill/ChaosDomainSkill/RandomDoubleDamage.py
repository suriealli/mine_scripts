#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.RandomDoubleDamage")
#===============================================================================
# 混沌神域被动技能，随机造成1到10倍伤害
#===============================================================================
from Game.Fight import SkillBase
from Util import Random

random_rate = [(500 , 1), (500 , 2), (1000 , 3), (2500 , 4), (2000 , 5), (1500 , 6), (1000 , 7), (500 , 8), (300 , 9), (200 , 10)]

class RandomDoubleDamage(SkillBase.PassiveSkill):
	skill_id = 850
	
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_target(self , target, skill):
		if skill.is_treat:
			return
		randomValue =Random.RandomRate()
		for rate , value in random_rate:
			randomValue.AddRandomItem(rate, value)
			
		self.value = randomValue.RandomOne()
		
		skill.target_skill_rate += self.value

if "_HasLoad" not in dir():
	RandomDoubleDamage.reg()
