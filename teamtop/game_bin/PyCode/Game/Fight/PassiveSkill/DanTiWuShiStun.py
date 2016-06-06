#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.DanTiWuShiStun")
#===============================================================================
# 之前的无视眩晕是阵营群体的，现在做一个单体怪物的。
#===============================================================================
from Game.Fight import SkillBase

class DanTiWuShiStun(SkillBase.PassiveSkill):
	#skill_id = 1
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_c_join(self,unit):
		self.unit.wushistun = 1

if "_HasLoad" not in dir():
	DanTiWuShiStun.reg()
