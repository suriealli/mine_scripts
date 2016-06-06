#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.QiSiHuiSheng")
#===============================================================================
# 起死回生：战斗中复活且回复一定生命值，最大回复100%生命值
#===============================================================================
from Game.Fight import SkillBase

class QiSiHuiSheng(SkillBase.PassiveSkill):
	skill_id = 906
	leave_to_hp_rate = [0, 0.2, 0.24, 0.29, 0.34, 0.4, 0.3, 0.34, 0.39, 0.44, 0.5, 0.58, 0.66, 0.75, 0.85, 1.0]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._has_be_kill.add(self.auto_u_has_be_kill)
	
	def unload_event(self):
		self.unit._has_be_kill.discard(self.auto_u_has_be_kill)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_has_be_kill(self, source, unit):
		self.unit.revive_at_next_round(self.leave_to_hp_rate[self.argv])

if "_HasLoad" not in dir():
	QiSiHuiSheng.reg()
