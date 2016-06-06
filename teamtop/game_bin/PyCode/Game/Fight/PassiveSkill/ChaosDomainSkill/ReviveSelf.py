#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.ReviveSelf")
#===============================================================================
# 混沌神域技能,复活自己一次
#===============================================================================
from Game.Fight import SkillBase

class ReviveSelf(SkillBase.PassiveSkill):
	skill_id = 857
	revive_hp_rate = 1		#复活后生命百分比
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._has_be_kill.add(self.auto_u_has_be_kill)
	
	def unload_event(self):
		self.unit._has_be_kill.discard(self.auto_u_has_be_kill)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_has_be_kill(self,source,unit):
		self.unit.revive_at_next_round(self.revive_hp_rate)

if "_HasLoad" not in dir():
	ReviveSelf.reg()
