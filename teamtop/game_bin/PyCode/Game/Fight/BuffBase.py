#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.BuffBase")
#===============================================================================
# Buff基本
#===============================================================================

if "_HasLoad" not in dir():
	BUFFS = {}

class BuffBase(object):
	buff_id = 0
	buff_type = 0
	is_benefit = None
	
	@classmethod
	def reg(cls):
		if cls.__name__ in BUFFS:
			print "GE_EXC, repeat buff(%s)" % cls.__name__
		BUFFS[cls.__name__] = cls
		if cls.buff_id:
			if cls.buff_id in BUFFS:
				print "GE_EXC, repeat buff id(%s)" % cls.skill_id
			BUFFS[cls.buff_id] = cls
	
	def __init__(self, unit, life, argv):
		self.unit = unit
		self.life = life
		self.argv = argv
		self.camp = unit.camp
		self.other_camp = unit.other_camp
		self.fight = unit.fight
		self.key = unit.fight.allot_key()
	
	def dec_life(self, cnt = 1):
		# 有可能被其他的地方给清除掉了
		if self.life <= 0: return
		self.life -= cnt
		if self.life <= 0:
			self.before_del()
			self.del_from_unit()
			self.unit = None
			self.camp = None
			self.fight = None
	
	def before_del(self):
		pass
