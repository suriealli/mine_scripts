#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.CrossTowerSkill.DieEnd")
#===============================================================================
# 自己死亡之后（即某个单位死亡后），则该阵营方失败（被动）
#===============================================================================
from Game.Fight import SkillBase

class DieEnd(SkillBase.PassiveSkill):
	skill_id = 1001
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._has_be_kill.add(self.auto_u_has_be_kill)
	
	def unload_event(self):
		self.unit._has_be_kill.discard(self.auto_u_has_be_kill)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	# 被杀
	def auto_u_has_be_kill(self, source, unit):
		unit.fight.result = True
		

if "_HasLoad" not in dir():
	DieEnd.reg()
