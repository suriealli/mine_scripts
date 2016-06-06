#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.BaoJiTiSheng")
#===============================================================================
# 提升暴击伤害
#===============================================================================
from Game.Fight import SkillBase

class BaoJiTiSheng(SkillBase.PassiveSkill):
	skill_id = 3010
	level_to_crit_hurt = 0.1
	
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
			skill.crit_hurt += self.level_to_crit_hurt

if "_HasLoad" not in dir():
	BaoJiTiSheng.reg()
