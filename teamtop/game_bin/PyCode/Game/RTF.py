#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.RTF")
#===============================================================================
# Run Time Function 运行时调用的函数
# 提供一个网页操作界面，给客服调用
#注意，修改RTF的函数时，请不要马上提交，要在打版本之前提交，因为过早的提交会导致一个问题，运维会不定时更新外网
#后台，这样更新会把这个函数也更新出去，或者把这个函数的具体调用url修改也更新出去，导致外网正式服和后台的RTF对应不上
#出现了调用失败等问题！
#===============================================================================

if "_HasLoad" not in dir():
	RTF_FUN = {}
	RTF_BACK_FUN = {}

def RegFunction(fun):
	'''
	注册一个运行时可被网页调用的函数
	@param fun: 函数
	'''
	key = "%s.%s" % (fun.__module__, fun.__name__)
	RTF_FUN[key] = fun
	return fun


def RegFunctionBack(fun):
	'''
	注册一个运行时可被网页调用的函数(运维独立出来的)
	@param fun: 函数
	'''
	key = "%s.%s" % (fun.__module__, fun.__name__)
	RTF_BACK_FUN[key] = fun
	return fun

def CallFunction(key, arg):
	'''
	呼叫一个运行时可被网页调用的函数
	@param key:
	@param arg:
	'''
	fun = RTF_FUN.get(key)
	if not fun:
		print "GE_EXC, can't find key(%s) on CallFunction" % key
		return
	apply(fun, arg)

def CallFunctionBack(key, arg):
	'''
	呼叫一个运行时可被网页调用的函数
	@param key:
	@param arg:
	'''
	fun = RTF_BACK_FUN.get(key)
	if not fun:
		print "GE_EXC, can't find key(%s) on CallFunction" % key
		return
	apply(fun, arg)
