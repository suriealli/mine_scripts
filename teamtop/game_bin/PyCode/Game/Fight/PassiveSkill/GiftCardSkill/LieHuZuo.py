#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.LieHuZuo")
#===============================================================================
# 单次收到的最大伤害不超过最大生命的70%，对boss的秒杀技能无效
#===============================================================================
from Game.Fight import SkillBase

class LieHuZuo(SkillBase.PassiveSkill):
	skill_id = 820
	level_to_change_hurt_rate = [0, 0.8, 0.76, 0.72, 0.68, 0.64, 0.70, 0.66, 0.62, 0.58, 0.54, 0.50, 0.45, 0.40, 0.35, 0.30]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
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
		change_hurt = int(self.unit.max_hp * self.level_to_change_hurt_rate[self.argv])
		if now_jap >= change_hurt:
			return change_hurt
		else:
			return now_jap

if "_HasLoad" not in dir():
	LieHuZuo.reg()
