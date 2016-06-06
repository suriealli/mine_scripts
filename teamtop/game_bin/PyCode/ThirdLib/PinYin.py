#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 汉字转拼音
#===============================================================================

if "_HasLoad" not in dir():
	D = {}

def Load():
	if D:
		return
	pos = __file__.find("PinYin")
	with open(__file__[:pos] + "pin_yin.data") as f:
		for l in f:
			if l[-1] == "\n":
				l = l[:-1]
			if l[-1] == "\r":
				l = l[:-1]
			kv = l.split("\t")
			D[kv[0]] = kv[1]

def Release():
	D.clear()

def GetPinYin(s):
	s = s.decode("utf-8")
	l = []
	for c in s:
		if c.istitle() or c.isdigit():
			l.append(c.encode("utf-8"))
		else:
			l.append(D.get("%X" % ord(c), "."))
	return l

if __name__ == "__main__":
	Load()
	print GetPinYin("我是阿萨2嘎")
	Release()
