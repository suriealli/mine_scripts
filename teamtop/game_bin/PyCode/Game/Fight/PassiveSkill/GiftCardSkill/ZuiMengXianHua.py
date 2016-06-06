#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.ZuiMengXianHua")
#===============================================================================
# 醉梦仙花：反弹自身受到的伤害，最大可反弹20%，且不超过自身最大生命值50%
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
	
class ZuiMengXianHua(SkillBase.PassiveSkill):
	skill_id = 905
	level_to_hurt_rate = [0, 0.03, 0.04, 0.05, 0.06, 0.08, 0.05, 0.06, 0.07, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2]
	
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
		if not source:
			return
		if source.is_out or source.hp <= 0:
			return
		if self.fight.is_back_hurt_trigger:
			return
		with AutoClose(self.fight):
			hurt = min(int(hurt * self.level_to_hurt_rate[self.argv]), self.unit.max_hp / 2)
			source.hurt(hurt, self.unit)

if "_HasLoad" not in dir():
	ZuiMengXianHua.reg()
