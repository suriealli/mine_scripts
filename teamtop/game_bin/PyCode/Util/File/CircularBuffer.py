#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Util.File.CircularBuffer")
#===============================================================================
# 循环队列
#===============================================================================

from collections import deque

class CircularBuffer(object):
	def __init__(self, size = 10):
		self.circular = deque(maxlen = size)
	
	def from_list(self, arg):
		if type([]) == type(arg):
			for v in arg:
				self.circular.append(v)
		if type(()) == type(arg):
			for v in arg:
				self.circular.append(v)
		
	def to_list(self):
		return list(self.circular)
	
	def push_front(self, arg):
		self.circular.appendleft(arg)
		
	def push_rear(self, arg):
		self.circular.append(arg)
		
	def pop_front(self):
		self.circular.popleft()
		
	def pop_rear(self):
		self.circular.pop()
		
	def size(self):
		return len(self.circular)
		
	def clear(self):
		self.circular.clear()
	
	#唯一性用途,非唯一不要用下面的接口(其实可以继承一下的)
	def __contains__(self, arg):
		return arg in self.circular
	
	def push_front_unique(self, arg):
		if arg in self.circular:
			return False
		self.circular.appendleft(arg)
		
	def push_rear_unique(self, arg):
		if arg in self.circular:
			return False
		self.circular.append(arg)

