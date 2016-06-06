#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.HuHuZhiWei")
#===============================================================================
# 狐虎之威：提升自身的免破率，最大可提示X
#===============================================================================
from Game.Fight import SkillBase

class HuHuZhiWei(SkillBase.PassiveSkill):
	skill_id = 914 
	level_to_increase_not_broken_rate = [0, 0.07, 0.08, 0.09, 0.1, 0.12, 0.1, 0.11, 0.12, 0.13, 0.15, 0.17, 0.19, 0.22, 0.26, 0.3]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._join.add(self.auto_u_join)
	
	def unload_event(self):
		self.unit._join.discard(self.auto_u_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_join(self, unit):
		self.unit.not_broken_rate += self.level_to_increase_not_broken_rate[self.argv]

if "_HasLoad" not in dir():
	HuHuZhiWei.reg()
