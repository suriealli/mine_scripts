#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ZongJiShouHu")
#===============================================================================
# 终极守护 血量小于30%时，免伤60%三个回合
# 被动技能的ID从500开始
#===============================================================================

from Game.Fight import SkillBase
import random

class ZongJiShouHu(SkillBase.PassiveSkill):
	skill_id = 506
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.has_create_buff = False
		self.level_to_hp_rate = [0, 0.3, 0.4]
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._change_hp.add(self.auto_u_change_hp)
	
	def unload_event(self):
		self.unit._change_hp.discard(self.auto_u_change_hp)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_change_hp(self, unit, jap):
		if self.has_create_buff == False and float(self.unit.hp) / self.unit.max_hp < self.level_to_hp_rate[self.argv]:
			self.has_create_buff = True
			life = 3
			if self.argv == 2 and random.randint(0, 99) < 25:
				life = 4
			self.unit.create_buff("ReduceDamageUp", life, 0.6)

if "_HasLoad" not in dir():
	ZongJiShouHu.reg()
