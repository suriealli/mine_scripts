#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.YeHuoBuSheng")
#===============================================================================
# 野火不生：减少自身受到的伤害，最大可减少40%
#===============================================================================
from Game.Fight import SkillBase

class YeHuoBuSheng(SkillBase.PassiveSkill):
	skill_id = 907
	level_to_damage_reduce_rate = [0, 0.08, 0.09, 0.11, 0.13, 0.16, 0.12, 0.13, 0.15, 0.17, 0.2, 0.23, 0.27, 0.31, 0.35, 0.4]
	
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
		self.unit.damage_reduce_rate += self.level_to_damage_reduce_rate [self.argv]

if "_HasLoad" not in dir():
	YeHuoBuSheng.reg()
