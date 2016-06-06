#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumCheck")
#===============================================================================
# 检测角色数值枚举
#===============================================================================
from Util.PY import PyParseBuild
from Game.Role.Data import EnumCD, EnumDayInt1, EnumDayInt8, EnumDisperseInt32, EnumDynamicInt64
from Game.Role.Data import EnumObj, EnumInt1, EnumInt16, EnumInt32, EnumInt64, EnumInt8, EnumTempInt64

def Check():
	CheckModule(EnumCD)
	CheckModule(EnumDayInt1)
	CheckModule(EnumDayInt8)
	CheckModule(EnumDisperseInt32)
	CheckModule(EnumDynamicInt64)
	CheckModule(EnumObj)
	CheckModule(EnumInt1)
	CheckModule(EnumInt16)
	CheckModule(EnumInt32)
	CheckModule(EnumInt64)
	CheckModule(EnumInt8)
	CheckModule(EnumTempInt64)

def CheckModule(module):
	mo = PyParseBuild.PyObj(module)
	uk = set()
	uv = set()
	for k, v, z in mo.GetEnumerateInfo(False):
		if type(v) != int:
			continue
		if k in uk:
			print "GE_EXC, repeat define in module(%s) %s = %s #%s" % (module.__name__, k, v, z)
		if v in uv:
			print "GE_EXC, repeat value in module(%s) %s = %s #%s" % (module.__name__, k, v, z)
		uk.add(k)
		uv.add(v)

if "_HasLoad" not in dir():
	Check()

