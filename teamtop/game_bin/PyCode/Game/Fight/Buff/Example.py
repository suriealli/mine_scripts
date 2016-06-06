#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Buff.Example")
#===============================================================================
# buff样例
#===============================================================================
from Game.Fight import BuffEx

class Example(BuffEx.StateBuff):
	buff_id = 1
	
	def __init__(self, unit, life, argv):
		BuffEx.StateBuff.__init__(self, unit, life, argv)
		if self.be_merge:
			return
		self.unit.change_hp(100)
	
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
		self.fight._before_round.add(self.auto_f_before_round)
		self.unit._after_skill.add(self.auto_u_after_skill)
		self.unit._before_hurt.add(self.auto_u_before_hurt)
		self.unit._before_skill.add(self.auto_u_before_skill)
		self.unit._has_be_kill.add(self.auto_u_has_be_kill)
		self.unit._has_kill.add(self.auto_u_has_kill)
		self.unit._join.add(self.auto_u_join)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
		self.fight._before_round.discard(self.auto_f_before_round)
		self.unit._after_skill.discard(self.auto_u_after_skill)
		self.unit._before_hurt.discard(self.auto_u_before_hurt)
		self.unit._before_skill.discard(self.auto_u_before_skill)
		self.unit._has_be_kill.discard(self.auto_u_has_be_kill)
		self.unit._has_kill.discard(self.auto_u_has_kill)
		self.unit._join.discard(self.auto_u_join)
	# AutoCodeEnd
	
	# 删除之前调用的函数
	def before_del(self):
		self.unit.change_hp(-100)
	
	# 有人加入战斗
	def auto_u_join(self, unit):
		pass
		
	# 回合开始
	def auto_f_before_round(self):
		self.dec_life()
	
	# 回合结束
	def auto_f_after_round(self):
		self.dec_life()
	
	# 使用技能之前
	def auto_u_before_skill(self, unit, skill):
		pass
	
	# 使用技能之后
	def auto_u_after_skill(self, unit, skill):
		pass
	
	# 击杀
	def auto_u_has_kill(self, unit, target):
		pass
	
	# 被杀
	def auto_u_has_be_kill(self, source, unit):
		pass
	
	def auto_u_before_hurt(self, unit, original_jap, now_jap):
		return 0

if "_HasLoad" not in dir():
	Example.reg()
