#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.ReduceHurtAndBack")
#===============================================================================
# buff样例
#===============================================================================
from Game.Fight import BuffEx, Operate

class ReduceHurtAndBack(BuffEx.NormalBuff):
	buff_id = 16
	
	def __init__(self, unit, life, argv):
		BuffEx.NormalBuff.__init__(self, unit, life, argv)
		self.strike_back = False
		self.strike_rate = 0.1
		self.strike_max_hp_rate = 0.5
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
		self.unit._before_hurt.add(self.auto_u_before_hurt)
		self.unit._has_be_hurt.add(self.auto_u_has_be_hurt)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
		self.unit._before_hurt.discard(self.auto_u_before_hurt)
		self.unit._has_be_hurt.discard(self.auto_u_has_be_hurt)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	#def before_del(self):
	#	pass
	def auto_f_after_round(self):
		self.dec_life()
	
	def auto_u_before_hurt(self, unit, original_jap, now_jap):
		if now_jap <= 0:
			return 0
		if now_jap > self.argv:
			self.fight.play_info.append((Operate.ReduceHurt, self.unit.key, self.argv))
			now_jap -= self.argv
			self.argv = 0
			self.dec_life(self.life)
		else:
			self.fight.play_info.append((Operate.ReduceHurt, self.unit.key, now_jap))
			self.argv -= now_jap
			now_jap = 0
		return now_jap
	
	def auto_u_has_be_hurt(self, source, hurt):
		if not source:
			return
		if not self.strike_back:
			return
		hurt = min(int(self.strike_rate * hurt), int(self.strike_max_hp_rate * self.unit.max_hp))
		source.hurt(hurt, self.unit)
	
	# 下面开始写buff事件

if "_HasLoad" not in dir():
	ReduceHurtAndBack.reg()
