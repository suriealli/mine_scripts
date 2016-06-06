#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.CrossTowerSkill.StunEnd")
#===============================================================================
# 如果能够触发眩晕/冰封技能，怪物死亡失败（被动）
#===============================================================================
from Game.Fight import SkillBase

class StunEnd(SkillBase.PassiveSkill):
	skill_id = 1000
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	
		
	# 下面开始写事件代码

	
	def auto_f_after_round(self):
		if self.unit.stun:
			self.unit.fight.result = True

if "_HasLoad" not in dir():
	StunEnd.reg()
