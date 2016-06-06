#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.RecoverHealth")
#===============================================================================
# 混沌神域技能，生命值地狱30%时，回复100%生命值
#===============================================================================
from Game.Fight import SkillBase

class RecoverHealth(SkillBase.PassiveSkill):
	skill_id = 859
	health_recover_rate = 1		#回复生命百分比
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.another_has_run = False
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._change_hp.add(self.auto_u_change_hp)
	
	def unload_event(self):
		self.unit._change_hp.discard(self.auto_u_change_hp)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_change_hp(self,unit,jap):
		if self.another_has_run == False and float(self.unit.hp) /self.unit.max_hp < 0.3:
			self.another_has_run = True
			self.unit.change_hp(int(self.health_recover_rate * self.unit.max_hp))

if "_HasLoad" not in dir():
	RecoverHealth.reg()
