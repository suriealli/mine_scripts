#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.FengHuangZuo")
#===============================================================================
# 凤凰座:自身主动治疗效果提升一定百分比
#===============================================================================
from Game.Fight import SkillBase

class FengHuangZuo(SkillBase.PassiveSkill):
	skill_id = 812
	level_to_change_treat_rate = [0, 0.1, 0.12, 0.14, 0.17, 0.2, 0.15, 0.17, 0.19, 0.22, 0.25, 0.29, 0.33, 0.38, 0.44, 0.5]
	
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
		self.unit.treat_rate += self.level_to_change_treat_rate[self.argv]

if "_HasLoad" not in dir():
	FengHuangZuo.reg()
