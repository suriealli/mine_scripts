#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Util.IntSet")
#===============================================================================
# 节省存储的集合接口
# 以区间的方式存储int
# l = [1,2,3,4,5,  10,11,12,  16,  18]
# l = [[1, 5], [10,12], 16, 18] 
#===============================================================================

def AddInt(l, i):
	# 空列表，直接加入
	if not l:
		l.append(i)
	# 找到插入的位置
	pos = length = len(l)
	for idx in xrange(length):
		value = l[idx]
		if type(value) is int:
			left = value
			right = value
		else:
			left = value[0]
			right = value[1]
		# 找到合适的位置
		if i < left:
			pos = idx
			break
		# 已经在集合中
		elif i <= right:
			return
		# 此时i > right,还得继续找
		else:
			continue
	# 处理特殊位置1
	if pos == 0:
		now_value = l[pos]
		if type(now_value) is int:
			if i + 1 == now_value:
				l[pos] = [i, now_value]
			else:
				l.insert(pos, i)
		else:
			if i + 1 == now_value[0]:
				now_value[0] = i
			else:
				l.insert(pos, i)
	# 处理特殊位置2
	elif pos == length:
		prev_value = l[pos - 1]
		if type(prev_value) is int:
			if prev_value + 1 == i:
				l[pos - 1] = [prev_value, i]
			else:
				l.append(i)
		else:
			if prev_value[1] + 1 == i:
				prev_value[1] = i
			else:
				l.append(i)
	# 一般位置
	else:
		# 统一形式
		prev_change = False
		now_change = False
		prev_value = l[pos - 1]
		if type(prev_value) is int:
			l[pos - 1] = prev_value = [prev_value, prev_value]
			prev_change = True
		now_value = l[pos]
		if type(now_value) is int:
			l[pos] = now_value = [now_value, now_value]
			now_change = True
		# 计算融合
		prev_merge = False
		now_merge = False
		if prev_value[1] + 1 == i:
			prev_merge = True
		if i + 1 == now_value[0]:
			now_merge = True
		# 融合or插入
		if prev_merge and now_merge:
			prev_value[1] = now_value[1]
			l.pop(pos)
		elif prev_merge:
			prev_value[1] = i
			if now_change:
				l[pos] = now_value[0]
		elif now_merge:
			now_value[0] = i
			if prev_change:
				l[pos - 1] = prev_value[0]
		else:
			if prev_change:
				l[pos - 1] = prev_value[0]
			if now_change:
				l[pos] = now_value[0]
			l.insert(pos, i)

def HasInt(l, i):
	for value in l:
		if type(value) is int:
			left = value
			right = value
		else:
			left = value[0]
			right = value[1]
		# 确认没有这个数
		if i < left:
			return False
		# 已经在集合中
		elif i <= right:
			return True
		# 此时i > right,还得继续找
		else:
			continue
	return False

def ToSet(l):
	s = set()
	for value in l:
		if type(value) is int:
			s.add(value)
		else:
			for i in xrange(value[0], value[1] + 1):
				s.add(i)
	return s


def IterSet(l):
	for i in l:
		if type(i) == int:
			yield i
		else:
			for j in xrange(i[0], i[1] + 1):
				yield j

if __name__ == "__main__":
	l = []
	AddInt(l, 1)
	print l
	
	AddInt(l, 4)
	print l
	
	AddInt(l, 1)
	print l
	
	AddInt(l, 2)
	print l
	
	AddInt(l, 5)
	print l
	
	AddInt(l, 2)
	print l
	
	AddInt(l, 0)
	print l
	
	AddInt(l, 4)
	print l
	
	for i in xrange(7):
		print i, HasInt(l, i),
	print
	
	AddInt(l, 3)
	print l
