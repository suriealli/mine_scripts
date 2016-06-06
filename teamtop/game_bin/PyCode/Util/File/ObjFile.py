#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 存取Python对象的文件
#===============================================================================
import datetime
datetime

def SaveObj(filePath, obj):
	'''
	保存一个对象到文件
	@param filePath:文件路径
	@param obj:对象
	'''
	open(filePath, 'w').write(repr(obj))

def LoadObj(filePath):
	'''
	从文件载入一个对象
	@param filePath:文件路径
	如果文件不存在会返回None，否则异常
	'''
	try:
		return eval(open(filePath).read())
	except IOError:
		return None
	except:
		raise

def GetObj(filePath, defual):
	'''
	从文件载入一个对象，如果异常返回默认值
	@param filePath:文件路径
	@param defual:默认值
	'''
	try:
		return eval(open(filePath).read())
	except:
		return defual

