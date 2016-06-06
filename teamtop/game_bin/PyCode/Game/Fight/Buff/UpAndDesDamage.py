#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.UpAndDesDamage")
#===============================================================================
# 增伤与减伤各增加5%
#===============================================================================
from Game.Fight import BuffEx

class UpAndDesDamage(BuffEx.StateBuff):
	buff_id = 11
	is_benefit = True
	
	def __init__(self, unit, life, argv):
		BuffEx.StateBuff.__init__(self, unit, life, argv)
		if self.be_merge:
			return
		self.unit.damage_upgrade_rate += 0.05
		self.unit.damage_reduce_rate += 0.05
	
	# AutoCodeBegin
	def load_event(self):
		pass
	
	def unload_event(self):
		pass
	# AutoCodeEnd
	
	# 删除之前调用的函数
	#def before_del(self):
	#	pass
	
	# 下面开始写buff事件

if "_HasLoad" not in dir():
	UpAndDesDamage.reg()
