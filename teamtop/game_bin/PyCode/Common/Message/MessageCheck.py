#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 检测消息枚举
#===============================================================================
from Common import Coding
from Common.Message import CMessage, PyMessage, OtherMessage
from Util.PY import PyParseBuild

# 名称-->索引值
MSG = {}
# 值-->名称
_MSG = {}

def Check():
	from Common.Message import AutoMessage
	MSG.clear()
	dk = {}
	dv = {}
	CheckModule(dk, dv, CMessage, Coding.CMessageRange)
	CheckModule(dk, dv, PyMessage, Coding.PyMessageRange)
	CheckModule(dk, dv, OtherMessage, Coding.OtherMessageRange)
	CheckAutoMessage(dk, dv, AutoMessage.AutoMsg, Coding.AutoMessageRange)

def CheckModule(dk, dv, module, crange):
	mo = PyParseBuild.PyObj(module)
	minvalue, maxvalue = crange
	for k, v, z in mo.GetEnumerateInfo(False):
		if k in dk:
			print "GE_EXC, repeat define in module(%s) %s = %s #%s" % (module.__name__, k, v, z)
			continue
		if v in dv:
			print "GE_EXC, repeat value in module(%s) %s = %s #%s" % (module.__name__, k, v, z)
			continue
		if minvalue <= v < maxvalue:
			dk[k] = v
			dv[v] = k
		else:
			print "GE_EXC, out of range in module(%s) %s = %s range[%s, %s) #%s" % (module.__name__, k, v, minvalue, maxvalue, z)
		MSG[k] = v
		_MSG[v] = k

def CheckAutoMessage(dk, dv, d, crange):
	minvalue, maxvalue = crange
	z = "None"
	for k, (v, z) in d.iteritems():
		if k in dk:
			print "GE_EXC, repeat define in AutoMessage %s = %s #%s" % (k, v, z)
			continue
		if v in dv:
			print "GE_EXC, repeat value in AutoMessage %s = %s #%s" % (k, v, z)
			continue
		if minvalue <= v < maxvalue:
			dk[k] = v
			dv[v] = k
		else:
			print "GE_EXC, out of range in AutoMessage %s = %s range[%s, %s) #%s" % (k, v, minvalue, maxvalue, z)
		MSG[k] = v
		_MSG[v] = k

