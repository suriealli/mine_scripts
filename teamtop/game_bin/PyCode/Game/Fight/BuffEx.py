#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.BuffEx")
#===============================================================================
# Buff
#===============================================================================
from Game.Fight import BuffBase, Operate

class NormalBuff(BuffBase.BuffBase):
	buff_type = 1
	
	def __init__(self, unit, life, argv):
		BuffBase.BuffBase.__init__(self, unit, life, argv)
		self.unit.normal_buffs.add(self)
		self.load_event()
		self.fight.play_info.append((Operate.CreateBuff, self.key, unit.key, self.buff_id, life))
	
	def del_from_unit(self, play = True):
		self.life = 0
		self.unload_event()
		self.unit.normal_buffs.discard(self)
		if play:
			self.fight.play_info.append((Operate.DeleteBuff, self.key))

class StateBuff(BuffBase.BuffBase):
	buff_type = 2
	
	def __init__(self, unit, life, argv):
		BuffBase.BuffBase.__init__(self, unit, life, argv)
		self.be_merge = False
		state_buffs = unit.state_buffs
		buff_name = self.__class__.__name__
		old_buff = state_buffs.get(buff_name)
		if old_buff:
			self.be_merge = True
			if old_buff.life < life:
				old_buff.life = life
		else:
			state_buffs[buff_name] = self
			self.load_event()
			self.fight.play_info.append((Operate.CreateBuff, self.key, unit.key, self.buff_id, life))
	
	def del_from_unit(self, play = True):
		self.life = 0
		self.unload_event()
		del self.unit.state_buffs[self.__class__.__name__]
		if play:
			self.fight.play_info.append((Operate.DeleteBuff, self.key))
