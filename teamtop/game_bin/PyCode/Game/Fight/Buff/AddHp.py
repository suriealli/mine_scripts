#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.AddHp")
#===============================================================================
# 临时加血的buff
#===============================================================================
from Game.Fight import BuffEx

class AddHp(BuffEx.StateBuff):
	buff_id = 40
	
	def __init__(self, unit, life, argv):
		BuffEx.StateBuff.__init__(self, unit, life, argv)
		if self.be_merge:
			return
		self.add_max_hp = int(self.unit.max_hp * argv)
		self.add_hp = int(self.unit.max_hp * argv)
		
		self.unit.change_max_hp(self.add_max_hp)
		self.unit.change_hp(self.add_hp)

	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	def before_del(self):
		self.unit.max_hp -= self.add_max_hp
		if self.unit.hp < self.unit.max_hp :
			self.unit.hp = self.unit.hp
		else :
			self.unit.hp = self.unit.max_hp

	
	# 下面开始写buff事件
	def auto_f_after_round(self):
		self.dec_life()

if "_HasLoad" not in dir():
	AddHp.reg()
