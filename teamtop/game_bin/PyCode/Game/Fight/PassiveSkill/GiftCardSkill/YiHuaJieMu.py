#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.YiHuaJieMu")
#===============================================================================
# 移花接木：造成的伤害按比例转化为自身的生命值，最大可吸收20%
#===============================================================================
from Game.Fight import SkillBase

class YiHuaJieMu(SkillBase.PassiveSkill):
	skill_id = 903
	level_to_change_hp_rate = [0, 0.03, 0.04, 0.05, 0.06, 0.08, 0.05, 0.06, 0.07, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._after_skill.add(self.auto_u_after_skill)
	
	def unload_event(self):
		self.unit._after_skill.discard(self.auto_u_after_skill)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_after_skill(self, unit, skill):
		change_hp = int(self.unit.total_hurt * self.level_to_change_hp_rate[self.argv])
		if change_hp <= 0:
			return
		self.unit.treat(change_hp, self.unit)

if "_HasLoad" not in dir():
	YiHuaJieMu.reg()
