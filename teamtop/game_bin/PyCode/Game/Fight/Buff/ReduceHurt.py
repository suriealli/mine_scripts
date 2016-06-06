#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.ReduceHurt")
#===============================================================================
# 吸收伤害
#===============================================================================
from Game.Fight import BuffEx, Operate

class ReduceHurt(BuffEx.NormalBuff):
	buff_id = 5
	is_benefit = True
	reduce_hurt_rate = 1.0
	
	def __init__(self, unit, life, argv):
		BuffEx.NormalBuff.__init__(self, unit, life, argv)
		self.fight.play_info.append((Operate.ShieldNumber, unit.key, argv))
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
		self.unit._before_hurt.add(self.auto_u_before_hurt)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
		self.unit._before_hurt.discard(self.auto_u_before_hurt)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	#def before_del(self):
	#	pass
	
	# 下面开始写buff事件
	def auto_f_after_round(self):
		self.dec_life()
	
	def auto_u_before_hurt(self, unit, original_jap, now_jap):
		if now_jap <= 0:
			return 0
		reduce_hurt = int(now_jap * self.reduce_hurt_rate)
		if reduce_hurt > self.argv:
			self.fight.play_info.append((Operate.ReduceHurt, self.unit.key, self.argv))
			now_jap -= self.argv
			self.argv = 0
			self.dec_life(self.life)
		else:
			self.fight.play_info.append((Operate.ReduceHurt, self.unit.key, now_jap))
			self.argv -= reduce_hurt
			now_jap -= reduce_hurt
		return now_jap

if "_HasLoad" not in dir():
	ReduceHurt.reg()
