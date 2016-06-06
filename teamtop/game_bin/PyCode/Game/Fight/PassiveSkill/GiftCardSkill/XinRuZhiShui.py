#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.XinRuZhiShui")
#===============================================================================
# 心如止水：减少战斗开始时自身受到的伤害2回合，最大减少80%
#===============================================================================
from Game.Fight import SkillBase

class XinRuZhiShui(SkillBase.PassiveSkill):
	skill_id = 902
	level_to_damage_reduce_rate = [0, 0.16, 0.18, 0.22, 0.26, 0.32, 0.24, 0.26, 0.3, 0.34, 0.4, 0.46, 0.54, 0.62, 0.7, 0.8]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.has_create_buff = False
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._join.add(self.auto_u_join)
	
	def unload_event(self):
		self.unit._join.discard(self.auto_u_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_join(self, unit):
		if self.has_create_buff == False :
			self.has_create_buff = True
			self.unit.create_buff("ReduceDamageUp", 2, self.level_to_damage_reduce_rate[self.argv])

if "_HasLoad" not in dir():
	XinRuZhiShui.reg()
