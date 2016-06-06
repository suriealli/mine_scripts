#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 随机的辅助模块
#===============================================================================
import random

# 按照概率随机的类
class RandomRate(object):
	def __init__(self):
		self.randomList = []
		self.totalRate = 0
	
	def AddRandomItem(self, rate, item):
		'''
		增加一个随机项
		@param rate:权重
		@param item:随机元素
		'''
		self.randomList.append((rate, item))
		self.totalRate += rate
	
	def RandomOne(self):
		'''
		按照权重随机出一个元素
		'''
		total = self.totalRate
		if total == 0:
			return None
		ran = random.randint(0, total - 1)
		for rate, item in self.randomList:
			total -= rate
			if total <= ran:
				return item
		return None
	
	def RandomMany(self, cnt = 1):
		'''
		按照权重不重复随机出最多cnt个元素的列表
		'''
		# 加速优化
		RANDOM_LIST = self.randomList
		copy_len = len(RANDOM_LIST)
		copy_total = self.totalRate
		if cnt >= copy_len:
			return [item for _, item in RANDOM_LIST]
		# 结果集
		many = []
		# 多次随机
		for _ in xrange(cnt):
			# 不能随机了
			if copy_total == 0:
				break
			# 随机一个
			total = copy_total
			ran = random.randint(0, total - 1)
			for idx in xrange(copy_len):
				info = RANDOM_LIST[idx]
				rate, item = info
				total -= rate
				# 随到了
				if total <= ran:
					many.append(item)
					# 将随机到的项调换到特定位置，并减少一个查找长度和一定的随机权重
					RANDOM_LIST[idx] = RANDOM_LIST[copy_len - 1]
					RANDOM_LIST[copy_len - 1] = info
					copy_len -= 1
					copy_total -= rate
					break
		return many

	def RandomOneThenDelete(self):
		'''
		按照权重随机出一个元素
		'''
		total = self.totalRate
		if total == 0:
			return None
		ran = random.randint(0, total - 1)
		
		i = 0
		r = 0
		for rate, item in self.randomList:
			total -= rate
			if total <= ran:
				i = item
				r = rate
				break
		
		if i > 0 and r > 0:
			self.randomList.remove((r, i))
			self.totalRate -= r
			return item
		else:
			return None

if __name__ == "__main__":
	r = RandomRate()
	r.AddRandomItem(10, 10)
	r.AddRandomItem(20, 20)
	r.AddRandomItem(40, 40)
	r.AddRandomItem(80, 80)
	r.AddRandomItem(160, 160)
	for _ in xrange(20):
		for _ in xrange(5):
			print r.RandomMany(4),
		print

