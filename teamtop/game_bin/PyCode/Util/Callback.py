#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 回调辅助模块
# 注意，注册的函数回调的时候可能发生异常，要处理之
# 注意，有可能会循环触发，要处理之
#===============================================================================
import os
import inspect
import datetime
import traceback
import cDateTime

if "_HasLoad" not in dir():
	CallBackDict = {}
	GlobalTriggerDict = {}

def AsTime(arg):
	if isinstance(arg, datetime.datetime):
		return arg
	else:
		return datetime.datetime(*arg)

# 本地函数注册回调
class LocalCallback(object):
	def __init__(self, key = None):
		self.key = key
		self.funList = []
		if self.key is None:
			frame = inspect.stack()[1]
			f = frame[1]
			f = f[f.rfind(os.sep) + 1:]
			l = frame[2]
			self.key = "%s:%s" % (f, l)
		if self.key in CallBackDict:
			print "GE_EXC, repeat key(%s), is reload error?" % self.key
		CallBackDict[self.key] = self
	
	def RegCallbackFunction(self, fun, deadtime = (2038, 1, 1), index = -1):
		'''
		注册一个函数
		@param fun:函数对象
		@param deadtime:过期时间
		@param index:索引
		'''
		# 判断过期
		ddt = AsTime(deadtime)
		if ddt <= cDateTime.Now():
			return
		# 检测是否重复
		fun.__name__
		if fun in self.funList:
			print "GE_EXC, repeat Reg function(%s, %s)" % (fun.__module__, fun.__name__)
			return
		# 按照索引插入
		if index < 0:
			self.funList.append(fun)
		else:
			self.funList.insert(index, fun)
	
	def CallAllFunctions(self, *argv):
		'''
		调用所有的注册的函数
		'''
		# 检测循环触发
		KEY = self.key
		cnt = GlobalTriggerDict.get(KEY, 0)
		if cnt > 5:
			#大于5次循环调用才会触发打印
			print "GE_EXC, cycle trigger more then 5 times"
			for key, times in GlobalTriggerDict.iteritems(): 
				print key, times
			print self.key, argv
			return
		GlobalTriggerDict[KEY] = cnt + 1
		# 真正触发
		exceptFuns = []
		# 尝试调用各个注册的函数
		for fun in self.funList:
			try:
				fun(*argv)
			except:
				# 有异常记录，并打印异常
				exceptFuns.append(fun)
				traceback.print_exc()
		# 还原计数
		GlobalTriggerDict[KEY] = cnt
		# 没异常，直接返回
		if not exceptFuns:
			return
		# 否则移除发生了异常的函数
		for fun in exceptFuns:
			print "GE_EXC, !!!!!!CallAllFunctions except call Fun (%s)!!!!!!" % fun.__name__
	
	def ShowFunction(self, key):
		'''
		打印所有注册的函数
		'''
		print key, self.key
		print key in self.key
		if key not in self.key: return
		print self.key
		for fun in self.funList:
			print "--", fun.__module__, fun.__name__

# 本地函数注册回调
class LocalCallbacks(object):
	def __init__(self):
		self.fundict = {}
		frame = inspect.stack()[1]
		f = frame[1]
		f = f[f.rfind(os.sep) + 1:]
		l = frame[2]
		self.key = "%s:%s" % (f, l)
	
	def RegCallbackFunction(self, funtype, fun, deadtime = (2038, 1, 1), index = -1):
		'''
		注册一个回调函数
		@param funtype:函数类型
		@param fun:回调函数
		@param deadtime:过期时间
		@param index:索引
		'''
		# 判断过期
		ddt = AsTime(deadtime)
		if ddt <= cDateTime.Now():
			return
		if funtype not in self.fundict:
			callback = self.fundict[funtype] = LocalCallback("%s:%s" % (self.key, funtype))
		else:
			callback = self.fundict[funtype]
		callback.RegCallbackFunction(fun, deadtime, index)
	
	def CallAllFunctions(self, funtype, *argv):
		'''
		调用某个类型的所有回调函数
		@param funtype:
		'''
		callback = self.fundict.get(funtype)
		if callback:
			callback.CallAllFunctions(*argv)
	
	def CallAllFunctionExs(self, funtype, *argv):
		'''
		调用某个类型的所有回调函数
		@param funtype:
		'''
		callback = self.fundict.get(funtype)
		if callback:
			callback.CallAllFunctions(*argv)

