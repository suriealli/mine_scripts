#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.AddDemage")
#===============================================================================
# 加成伤害
#===============================================================================
from Game.Fight import BuffEx

class AddDemage(BuffEx.StateBuff):
	buff_id = 900
	
	def __init__(self, unit, life, argv):
		BuffEx.StateBuff.__init__(self, unit, life, argv)
		if self.be_merge:
			return
		self.unit.damage_upgrade_rate += argv
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	def before_del(self):
		self.unit.damage_upgrade_rate -= self.argv
	#	pass
	
	# 下面开始写buff事件
	def auto_f_after_round(self):
		self.dec_life()

if "_HasLoad" not in dir():
	AddDemage.reg()
