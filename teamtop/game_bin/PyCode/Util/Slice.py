#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Util.Slice")
#===============================================================================
# 切片
#===============================================================================
def IterSlice(squ, cnt):
	start = 0
	end = cnt
	l = len(squ)
	while True:
		yield squ[start:end]
		if end < l:
			start = end
			end += cnt
		else:
			raise StopIteration

def GetSlice(squ, cnt):
	return [item for item in IterSlice(squ, cnt)]

if __name__ == "__main__":
	for l in IterSlice(range(10), 4):
		print l
	