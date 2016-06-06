#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Handle")
#===============================================================================
# 战斗触发
#===============================================================================
import traceback
from Util import Trace

class Handle(object):
	def __init__(self):
		# 流程事件
		self._join = set()
		self._before_round = set()
		self._after_round = set()
		self._before_skill = set()
		self._after_skill = set()
		self._has_kill = set()
		self._has_be_kill = set()
		self._before_hurt = set()
		self._has_hurt = set()
		self._has_be_hurt = set()
		self._change_hp = set()
		self._before_target = set()
		self._before_be_target = set()
	
	def try_trigger(self):
		assert False
	
	def _event(self, handle):
		if handle and self.try_trigger():
			for fun in tuple(handle):
				# 可能在回调函数中导致战斗单位死亡或者buff清除导致事件取消
				if fun not in handle:
					continue
				try:
					fun()
				except:
					handle.discard(fun)
					traceback.print_exc()
					Trace.StackWarn("_event error.")
	
	def _event_u(self, handle, unit):
		if handle and self.try_trigger():
			for fun in tuple(handle):
				if fun not in handle:
					continue
				try:
					fun(unit)
				except:
					handle.discard(fun)
					traceback.print_exc()
					Trace.StackWarn("_event_u error.")
	
	def _event_uj(self, handle, unit, jap):
		if handle and self.try_trigger():
			for fun in tuple(handle):
				if fun not in handle:
					continue
				try:
					fun(unit, jap)
				except:
					handle.discard(fun)
					traceback.print_exc()
					Trace.StackWarn("_event_uj error.")
	
	def _event_uu(self, handle, unit, target):
		if handle and self.try_trigger():
			for fun in tuple(handle):
				if fun not in handle:
					continue
				try:
					fun(unit, target)
				except:
					handle.discard(fun)
					traceback.print_exc()
					Trace.StackWarn("_event_uu error.")
	
	def _event_us(self, handle, unit, skill):
		if handle and self.try_trigger():
			for fun in tuple(handle):
				if fun not in handle:
					continue
				try:
					fun(unit, skill)
				except:
					handle.discard(fun)
					traceback.print_exc()
					Trace.StackWarn("_event_us error.")
	
	def _event_ujj(self, handle, unit, original_jap, now_jap):
		if handle and self.try_trigger():
			for fun in tuple(handle):
				if fun not in handle:
					continue
				try:
					now_jap = fun(unit, original_jap, now_jap)
				except:
					handle.discard(fun)
					traceback.print_exc()
					Trace.StackWarn("_event_ujj error.")
		return now_jap
	
	def event_join(self, unit):
		'''加入战场'''
		self._event_u(self._join, unit)
	
	def event_before_round(self):
		'''新的回合'''
		self._event(self._before_round)
	
	def event_after_round(self):
		'''回合结束'''
		self._event(self._after_round)
	
	def event_before_skill(self, unit, skill):
		'''使用技能之前'''
		self._event_us(self._before_skill, unit, skill)
	
	def event_after_skill(self, unit, skill):
		'''使用技能之后'''
		self._event_us(self._after_skill, unit, skill)
	
	def event_has_kill(self, unit, target):
		'''有人杀人'''
		self._event_uu(self._has_kill, unit, target)
	
	def event_has_be_kill(self, source, unit):
		'''有人被杀'''
		self._event_uu(self._has_be_kill, source, unit)
	
	def event_before_hurt(self, unit, original_jap, now_jap):
		'''伤害拦截'''
		return self._event_ujj(self._before_hurt, unit, original_jap, now_jap)
	
	def event_change_hp(self, unit, jap):
		'''HP改变'''
		self._event_uj(self._change_hp, unit, jap)
	
	def event_has_hurt(self, target, hurt):
		'''造成伤害'''
		return self._event_uj(self._has_hurt, target, hurt)
	
	def event_has_be_hurt(self, source, hurt):
		'''被造成伤害'''
		return self._event_uj(self._has_be_hurt, source, hurt)
	
	def event_before_target(self, target, skill):
		'''目标修正'''
		self._event_us(self._before_target, target, skill)
	
	def event_before_be_target(self, unit, skill):
		'''被选中为目标之前'''
		self._event_us(self._before_be_target, unit, skill)
	