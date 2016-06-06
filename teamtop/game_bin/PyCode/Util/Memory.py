#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Util.Memory")
#===============================================================================
# 计算内存大小
#===============================================================================
import os
import sys
import platform

def GetTotalMemorySize(obj):
	s = sys.getsizeof(obj)
	if isinstance(obj, str):
		s += len(obj)
	elif isinstance(obj, dict):
		for k, v in obj.iteritems():
			s += GetTotalMemorySize(k)
			s += GetTotalMemorySize(v)
	elif isinstance(obj, (tuple, list, set)):
		for o in obj:
			s += GetTotalMemorySize(o)
	return s

def GetProcessMemorySize():
	if platform.system() == "Windows":
		result = os.popen('tasklist /fi "pid eq %s"' % os.getpid()).read()
		l = []
		for row in result.split("\n"):
			if str(os.getpid()) not in row:
				continue
			for c in row.split("  "):
				if c:
					l.append(c)
			return l
	else:
		result = os.popen("ps -e -o 'pid,comm,pcpu,rsz,vsz' | grep 'ComplexServer' | grep '%s' | grep -v 'grep'" % os.getpid()).read()
		l = []
		for c in result.split(" "):
			if c:
				l.append(c)
		return l

if __name__ == "__main__":
	print GetProcessMemorySize()
