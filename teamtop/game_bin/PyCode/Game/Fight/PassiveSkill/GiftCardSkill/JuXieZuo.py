#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.JuXieZuo")
#===============================================================================
# 生命低于30%时，回复血量30%，一次战斗中只能生效一次
#===============================================================================
from Game.Fight import SkillBase

class JuXieZuo(SkillBase.PassiveSkill):
	skill_id = 804
	level_to_recovery_hp = [0, 0.2, 0.24, 0.29, 0.34, 0.4, 0.3, 0.34, 0.39, 0.44, 0.5, 0.58, 0.66, 0.75, 0.85, 1]
	
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.has_run = False
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._change_hp.add(self.auto_u_change_hp)
	
	def unload_event(self):
		self.unit._change_hp.discard(self.auto_u_change_hp)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_change_hp(self, unit, jap):
		if self.has_run == False and float(self.unit.hp) / self.unit.max_hp < 0.3:
			self.has_run = True
			self.unit.change_hp(int(self.level_to_recovery_hp[self.argv] * self.unit.max_hp))
			

if "_HasLoad" not in dir():
	JuXieZuo.reg()
