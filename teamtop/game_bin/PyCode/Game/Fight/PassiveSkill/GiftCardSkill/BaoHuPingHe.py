#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.BaoHuPingHe")
#===============================================================================
# 暴虎冯河：增加自身的暴击伤害，最大可提升70%
#===============================================================================
from Game.Fight import SkillBase

class BaoHuPingHe(SkillBase.PassiveSkill):
	skill_id = 909
	level_to_crit_hurt = [0, 0.15, 0.18, 0.21, 0.25, 0.3, 0.25, 0.28, 0.31, 0.35, 0.4, 0.45, 0.51, 0.57, 0.63, 0.7]
	
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
		for skill in unit.get_all_active_skill():
			skill.crit_hurt += self.level_to_crit_hurt[self.argv]

if "_HasLoad" not in dir():
	BaoHuPingHe.reg()
