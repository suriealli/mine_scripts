#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.HealthPerRound")
#===============================================================================
# 每回合治愈
#===============================================================================
from Game.Fight import BuffEx

class HealthPerRound(BuffEx.StateBuff):
	buff_id = 7
	
	def __init__(self, unit, life, argv):
		BuffEx.StateBuff.__init__(self, unit, life, argv)
		if self.be_merge:
			return
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	
	# 下面开始写buff事件
	def auto_f_after_round(self):
		self.unit.treat(self.argv, self.unit)
		self.dec_life()

if "_HasLoad" not in dir():
	HealthPerRound.reg()
