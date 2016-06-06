#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.ReduceDamageUp")
#===============================================================================
# 降低受到的伤害
#===============================================================================
from Game.Fight import BuffEx

class ReduceDamageUp(BuffEx.NormalBuff):
	buff_id = 13
	is_benefit = True
	
	def __init__(self, unit, life, argv):
		BuffEx.NormalBuff.__init__(self, unit, life, argv)
		self.unit.damage_reduce_rate += argv
		
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	def before_del(self):
		self.unit.damage_reduce_rate -= self.argv
	
	# 下面开始写buff事件
	def auto_f_after_round(self):
		self.dec_life()

if "_HasLoad" not in dir():
	ReduceDamageUp.reg()
