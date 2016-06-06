#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.ReboundHurtAfter3Round")
#===============================================================================
# 三回合后开始反弹伤害
#===============================================================================
from Game.Fight import SkillBase

class AutoClose(object):
	def __init__(self,fight):
		self.fight = fight
		
	def __enter__(self):
		self.fight.is_back_hurt_trigger = True
		return self
	
	def __exit__(self,_type,_value,_traceback):
		self.fight.is_back_hurt_trigger = False
		# 抛出异常
		return False
	
class ReboundHurtAfter3Round(SkillBase.PassiveSkill):
	skill_id = 854
	rebound_rate = 0.1		#反弹比例
	prefix_round = 4		#前置回合数
	
	
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._has_be_hurt.add(self.auto_u_has_be_hurt)
	
	def unload_event(self):
		self.unit._has_be_hurt.discard(self.auto_u_has_be_hurt)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_has_be_hurt(self,source,hurt):
		if not source:
			return
		if source.is_out or source.hp < 0:
			return
		if self.fight.is_back_hurt_trigger:
			return
		if self.unit.fight.round < self.prefix_round:
			return
		
		with AutoClose(self.fight):
			hurt = int(hurt * self.rebound_rate)
			source.hurt(hurt,self.unit)

if "_HasLoad" not in dir():
	ReboundHurtAfter3Round.reg()