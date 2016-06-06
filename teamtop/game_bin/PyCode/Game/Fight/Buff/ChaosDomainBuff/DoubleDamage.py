#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.ChaosDomainBuff.DoubleDamage")
#===============================================================================
# 混沌神域buff，使技能效果加倍
#===============================================================================
from Game.Fight import BuffEx

class DoubleDamage(BuffEx.StateBuff):
	buff_id = 930
	
	def __init__(self, unit, life, argv):
		BuffEx.StateBuff.__init__(self, unit, life, argv)
		if self.be_merge:
			return
		self.unit.damage_upgrade_rate += argv
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_skill.add(self.auto_f_after_skill)
	
	def unload_event(self):
		self.fight._after_skill.discard(self.auto_f_after_skill)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	def before_del(self):
		self.unit.damage_upgrade_rate -= self.argv
	
	# 下面开始写buff事件
	def auto_f_after_skill(self):
		self.dec_life()

if "_HasLoad" not in dir():
	DoubleDamage.reg()
