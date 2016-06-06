#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.ZengShangJianShang")
#===============================================================================
# 进入战斗时提升己方全队5%增伤和5%减伤
#===============================================================================
from Game.Fight import SkillBase

class ZengShangJianShang(SkillBase.PassiveSkill):
	skill_id = 3016
	level_to_damage_upgrade_rate = 0.05
	level_to_damage_reduce_rate = 0.05
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_c_join(self, unit):
		unit.damage_upgrade_rate += self.level_to_damage_upgrade_rate
		unit.damage_reduce_rate += self.level_to_damage_reduce_rate

if "_HasLoad" not in dir():
	ZengShangJianShang.reg()
