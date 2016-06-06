#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.MoFaZhen.XiXueBeiDong")
#===============================================================================
# 吸血：生命低于一定百分比有吸血效果， 然后加血的生效1次.战斗中只生效1次。
#===============================================================================
from Game.Fight import SkillBase

class XiXueBeiDong(SkillBase.PassiveSkill):
	skill_id = 705
	level_to_change_hp_rate = [0, 0.1, 0.15, 0.2, 0.25, 0.3]
	level_to_hp = [0, 0.3, 0.325, 0.35, 0.375, 0.4]
	
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
		if self.has_revive_status():
			return
		if float(self.unit.hp) / self.unit.max_hp < self.level_to_hp[self.argv]:
			self.make_revive_status()
			change_hp = int(self.unit.total_hurt * self.level_to_change_hp_rate[self.argv])
			if change_hp <= 0:
				return
			for u in self.camp.pos_units.itervalues():
				u.treat(change_hp, self.unit)

if "_HasLoad" not in dir():
	XiXueBeiDong.reg()
