#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.HurtConnect")
#===============================================================================
# 伤害链接
#===============================================================================
import Environment
import traceback
from Game.Fight import BuffEx

class HurtConnect(BuffEx.StateBuff):
	buff_id = 15
	
	def __init__(self, unit, life, argv):
		BuffEx.StateBuff.__init__(self, unit, life, argv)
		if self.be_merge:
			return
		if len(self.argv) == 3:
			self.buff_name, self.self_rate, self.member_rate = self.argv
		elif len(self.argv) == 4:
			self.buff_name, self.self_rate, self.member_rate, self.hurttagtet = self.argv
		else:
			self.buff_name, self.self_rate, self.member_rate, self.hurttagtet = self.argv
		self.buff_flag = self.buff_name + "_flag"
		self.get_all_buffs().add(self)
	
	def get_all_buffs(self):
		camp = self.camp
		buffs = getattr(camp, self.buff_name, None)
		if buffs is None:
			buffs = set()
			setattr(camp, self.buff_name, buffs)
		return buffs
	
	def transport_hurt(self, hurt):
		camp = self.camp
		# 如果正在伤害传递，则不再次进行伤害传递
		transport = getattr(camp, self.buff_flag, False)
		if transport:
			return
		# 标记在进行伤害传递
		setattr(camp, self.buff_flag, True)
		try:
			if len(self.argv) == 3:
				for buff in self.get_all_buffs():
					if buff != self and buff.unit and (not buff.unit.is_out):
						buff.unit.hurt(hurt, None)
				
			else:
				for buff in self.get_all_buffs():
					if buff != self:
						continue
					if buff.unit and (not buff.unit.is_out) and self.hurttagtet and (not self.hurttagtet.is_out):
						self.hurttagtet.hurt(hurt, None)
		except:
			traceback.print_exc()
		# 标记在离开伤害传递
		setattr(camp, self.buff_flag, False)
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
		self.unit._before_hurt.add(self.auto_u_before_hurt)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
		self.unit._before_hurt.discard(self.auto_u_before_hurt)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	def before_del(self):
		self.get_all_buffs().discard(self)
	
	# 下面开始写buff事件
	def auto_f_after_round(self):
		self.dec_life()
	
	def auto_u_before_hurt(self, unit, original_jap, now_jap):
		hurt = int(original_jap * self.member_rate)
		self.transport_hurt(hurt)
		return int(now_jap * self.self_rate)

if "_HasLoad" not in dir():
	HurtConnect.reg()
