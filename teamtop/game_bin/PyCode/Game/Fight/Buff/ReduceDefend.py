#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.ReduceDefend")
#===============================================================================
# 降低防御
#===============================================================================
from Game.Fight import BuffEx

class ReduceDefend(BuffEx.StateBuff):
	buff_id = 6
	is_benefit = False
	
	def __init__(self, unit, life, argv):
		BuffEx.StateBuff.__init__(self, unit, life, argv)
		if self.be_merge:
			return
		self.unit.change_defence(-argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	def before_del(self):
		self.unit.defence_m += self.argv
		self.unit.defence_p += self.argv
	
	# 下面开始写buff事件
	def auto_f_after_round(self):
		self.dec_life()

if "_HasLoad" not in dir():
	ReduceDefend.reg()
