#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ShenShuMiJing")
#===============================================================================
# 注释
# 神树秘境被动技能
# 每受到一次攻击掉1点血
#===============================================================================
from Game.Fight import SkillBase

class ShenShuMiJing(SkillBase.PassiveSkill):
	skill_id = 2204
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.be_hurt_basic = 666666
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_hurt.add(self.auto_u_before_hurt)
	
	def unload_event(self):
		self.unit._before_hurt.discard(self.auto_u_before_hurt)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_hurt(self, unit, original_jap, now_jap):
		if now_jap <= 0:
			return 0
		if original_jap >= 9999999999:
			return now_jap
		if now_jap >= 0:
			return self.be_hurt_basic
		else:
			return self.be_hurt_basic
		
			
if "_HasLoad" not in dir():
	ShenShuMiJing.reg()
