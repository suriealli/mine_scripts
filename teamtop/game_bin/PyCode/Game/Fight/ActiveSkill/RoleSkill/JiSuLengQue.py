#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.JiSuLengQue")
#===============================================================================
# 使用后可立即重置主角所有技能的cd，并增加主角N点怒气
#===============================================================================
from Game.Fight import SkillBase

class JiSuLengQue(SkillBase.ActiveSkillBase):
	prefix_round = 0		#前置回合数
	cd_round = 9			#CD回合数S
	need_moral = 0		#需要士气
	play_time = 2.3			#播放时间（秒）
	level_to_moral = [0, 10, 15, 20, 25, 30]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.moral = self.level_to_moral[argv]
	
	def select_targets(self):
		return self.unit.select_self()
	
	def do_after(self, targets):
		unit = self.unit
		for skill in unit.active_skills:
			if skill is self:
				continue
			skill.set_round(-9)
		unit.change_moral(self.moral)

if "_HasLoad" not in dir():
	JiSuLengQue.reg()
