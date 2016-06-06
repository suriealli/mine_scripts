#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Common.Serialize")
#===============================================================================
# Python对象序列化和反序列化
#===============================================================================
import cPickle
import datetime

datetime

String2PyObj = cPickle.loads

def String2PyObjEx(s):
	if s is None:
		return None
	else:
		return cPickle.loads(s)

def PyObj2String(obj):
	return cPickle.dumps(obj, 1)


