#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.AddDamage")
#===============================================================================
# 注释
#===============================================================================
from Game.Fight import SkillBase

class AddDamage(SkillBase.PassiveSkill):
	skill_id = 1233
	level_to_target_skill_rate = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:1500}
	IS_MAX = 10
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_target(self,target,skill):
		fightround = self.unit.fight.round
		if fightround > self.IS_MAX:
			fightround = 10
		self.unit.damage_upgrade_rate += self.level_to_target_skill_rate(fightround) 
		

if "_HasLoad" not in dir():
	AddDamage.reg()
