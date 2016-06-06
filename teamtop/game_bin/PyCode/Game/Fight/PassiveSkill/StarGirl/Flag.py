#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.Flag")
#===============================================================================
# 标记被动技能
#===============================================================================
from Game.Fight import SkillBase

class Flag(SkillBase.PassiveSkill):
	#skill_id = 1
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		setattr(self.unit, self.__class__.__name__ + "_flag", self.get_flag())
	
	def get_flag(self):
		return self.argv
	
	# AutoCodeBegin
	def load_event(self):
		pass
	
	def unload_event(self):
		pass
	# AutoCodeEnd
	
	# 下面开始写事件代码

if "_HasLoad" not in dir():
	Flag.reg()
