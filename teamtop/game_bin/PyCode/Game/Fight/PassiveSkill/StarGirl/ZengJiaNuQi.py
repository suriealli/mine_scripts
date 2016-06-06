#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.ZengJiaNuQi")
#===============================================================================
# 初始星灵增加25点怒气
#===============================================================================
from Game.Fight import SkillBase

class ZengJiaNuQi(SkillBase.PassiveSkill):
	skill_id = 3011
	
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
		self.unit.change_moral(25)

if "_HasLoad" not in dir():
	ZengJiaNuQi.reg()
