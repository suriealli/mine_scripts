#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Shield")
#===============================================================================
# 屏蔽字符
#===============================================================================
import DynamicPath

def LoadConfig():
	FL = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FL.AppendPath("Shield")
	
	with open(FL.FilePath("ChatChar.txt")) as f:
		s = f.read()
		for c in s.split(' '):
			ChatChar.add(c)
	with open(FL.FilePath("NameChar.txt")) as f:
		s = f.read()
		for c in s.split(' '):
			NameChar.add(c)

def HasNameShield(s):
	'''
	是否有屏蔽字
	@param s:源字符串
	@return :字符串（屏蔽字）， 没有返回None
	'''
	for c in s:
		if c in NameChar:
			return c
	return None

if "_HasLoad" not in dir():
	ChatChar = set()
	NameChar = set()
