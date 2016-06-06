#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.ShuiPingZuo")
#===============================================================================
# 水瓶座，反弹伤害，最大反伤值不超过自身生命值50%
#===============================================================================
from Game.Fight import SkillBase

class AutoClose(object):
	def __init__(self, fight):
		self.fight = fight
	
	def __enter__(self):
		self.fight.is_back_hurt_trigger = True
		return self
	
	def __exit__(self, _type, _value, _traceback):
		self.fight.is_back_hurt_trigger = False
		# 要将异常继续抛出
		return False

class ShuiPingZuo(SkillBase.PassiveSkill):
	skill_id = 801
	level_to_hurt_rate = [0, 0.03, 0.04, 0.05, 0.06, 0.08, 0.05, 0.06, 0.07, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.23, 0.26, 0.29, 0.32, 0.35, 0.38, 0.41, 0.45]
	level_to_change_hurt_rate = [0, 0.8, 0.76, 0.72, 0.68, 0.64, 0.70, 0.66, 0.62, 0.58, 0.54, 0.50, 0.45, 0.40, 0.35, 0.30]
	liehu_id = 820
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._has_be_hurt.add(self.auto_u_has_be_hurt)
	
	def unload_event(self):
		self.unit._has_be_hurt.discard(self.auto_u_has_be_hurt)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_has_be_hurt(self, source, hurt):
		level = 0
		
		if not source:
			return
		if source.is_out or source.hp <= 0:
			return
		if self.fight.is_back_hurt_trigger:
			return
		
		for skill in self.unit.passive_skills:
			if skill.skill_id == 820:
				level = skill.argv
				break
		
		with AutoClose(self.fight):
			if level == 0:
				hurt = min(int(hurt * self.level_to_hurt_rate[self.argv]), self.unit.max_hp / 2)
			else:
				hurt = min(int(hurt * self.level_to_hurt_rate[self.argv]), int(self.unit.max_hp * self.level_to_change_hurt_rate[level] * self.level_to_hurt_rate[self.argv]), self.unit.max_hp / 2)
			source.hurt(hurt, self.unit)

if "_HasLoad" not in dir():
	ShuiPingZuo.reg()
