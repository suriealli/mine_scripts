#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.WuShiStun")
#===============================================================================
# 无视眩晕被动技能
#===============================================================================
from Game.Fight import SkillBase

class WuShiStun(SkillBase.PassiveSkill):
	skill_id = 821
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
	# AutoCodeEnd
	
	
	def auto_c_join(self, unit):
		unit.wushistun = 1
	


if "_HasLoad" not in dir():
	WuShiStun.reg()
