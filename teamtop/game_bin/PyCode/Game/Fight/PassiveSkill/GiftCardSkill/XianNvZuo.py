#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.GiftCardSkill.XianNvZuo")
#===============================================================================
# 生命低于50%时，伤害加成两个回合，一次战斗中只能生效一次
#===============================================================================
from Game.Fight import SkillBase

class XianNvZuo(SkillBase.PassiveSkill):
	skill_id = 810
	level_to_increase_damage_upgrade_rate= [0, 0.15, 0.18, 0.21, 0.25, 0.3, 0.2, 0.23, 0.26, 0.3, 0.35, 0.4, 0.45, 0.51, 0.58, 0.65, 0.25, 0.28, 0.31, 0.35, 0.4, 0.45, 0.5, 0.56, 0.63, 0.7, 0.78, 0.86, 0.94, 1.02, 1.1]
	level_to_hp_rate = [0, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.has_create_buff = False
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._change_hp.add(self.auto_u_change_hp)
	
	def unload_event(self):
		self.unit._change_hp.discard(self.auto_u_change_hp)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_change_hp(self, unit, jap):
		if self.has_create_buff == False and int(self.unit.hp) / self.unit.max_hp < float(self.level_to_hp_rate[self.argv]):
			self.has_create_buff = True
			self.unit.create_buff("AddDemage", 2, self.level_to_increase_damage_upgrade_rate[self.argv])
		
		

if "_HasLoad" not in dir():
	XianNvZuo.reg()
