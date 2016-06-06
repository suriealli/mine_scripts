#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.MoFaZhen.HuDunBeiDong")
#===============================================================================
# 刚进入战斗中，自己生效一个护盾，护盾只能生效一回合，抵挡对方一定百分比的伤害，最高可以抵挡自己的n倍生命上限
#===============================================================================
from Game.Fight import SkillBase

class HuDunBeiDong(SkillBase.PassiveSkill):
	skill_id = 702
	level_to_damage_reduce_rate = [0, 0.192, 0.288, 0.384, 0.48, 0.6]
	level_to_damage_hp_rate = [0, 1, 1.5, 2, 2.5, 3]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._join.add(self.auto_u_join)
	
	def unload_event(self):
		self.unit._join.discard(self.auto_u_join)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_join(self, unit):
		if self.has_revive_status():
			return
		self.make_revive_status()
		buff = unit.create_buff("ReduceHurt", 1, int(unit.max_hp * self.level_to_damage_hp_rate[self.argv]))
		buff.reduce_hurt_rate = self.level_to_damage_reduce_rate[self.argv]

if "_HasLoad" not in dir():
	HuDunBeiDong.reg()
