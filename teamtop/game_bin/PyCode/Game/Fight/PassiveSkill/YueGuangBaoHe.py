#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.YueGuangBaoHe")
#===============================================================================
# 月光宝盒
# 进场后释放一次魔兽入侵主动技能（全秒对方）
# 被动技能的ID从500开始
#===============================================================================
from Game.Fight import SkillBase

class YueGuangBaoHe(SkillBase.PassiveSkill):
	skill_id = 508
	
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
		skill = self.unit.new_active_skill(302, None)
		skill.do()

if "_HasLoad" not in dir():
	YueGuangBaoHe.reg()
