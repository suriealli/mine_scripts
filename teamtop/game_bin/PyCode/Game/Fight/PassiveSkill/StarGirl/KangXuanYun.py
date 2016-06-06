#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.KangXuanYun")
#===============================================================================
# 进入战斗时主角抗眩晕率提高10%
#===============================================================================
from Game.Fight import SkillBase

class KangXuanYun(SkillBase.PassiveSkill):
	skill_id = 3015
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_c_join(self, unit):
		if unit.unit_type == 1:
			self.unit.defence_stun_rate += 0.1

if "_HasLoad" not in dir():
	KangXuanYun.reg()
