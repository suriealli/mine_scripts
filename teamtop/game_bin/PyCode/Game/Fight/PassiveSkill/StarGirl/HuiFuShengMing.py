#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.HuiFuShengMing")
#===============================================================================
# 主角生命低于30%，每回合恢复生命值的5%，持续3回合
#===============================================================================
from Game.Fight import SkillBase

class HuiFuShengMing(SkillBase.PassiveSkill):
	skill_id = 3018
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.has_used = False
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._change_hp.add(self.auto_c_change_hp)
	
	def unload_event(self):
		self.camp._change_hp.discard(self.auto_c_change_hp)
	# AutoCodeEnd
	
	# 改变血量
	def auto_c_change_hp(self, unit, jap):
		# 已经生效过
		if self.has_used:
			return
		# 不是主角
		if unit.unit_type != 1:
			return
		# 不是自己的主角
		if unit.role_id != self.unit.role_id:
			return
		# 血量没有低于50%
		if float(unit.hp) / unit.max_hp > 0.3:
			return
		self.has_used = True
		unit.create_buff("HealthPerRound", 2, int(unit.max_hp * 0.05))

if "_HasLoad" not in dir():
	HuiFuShengMing.reg()
