#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 函数辅助模块
#===============================================================================
import sys
import types

def FunctionPack_Check(fun):
	'''
	将一个函数打包成一个描述该函数的tuple
	@param fun:函数对象
	@return: (函数所在的模块, 函数名)
	'''
	assert(type(fun) == types.FunctionType)
	return FunctionPack_Uncheck(fun)

def FunctionPack_Uncheck(fun):
	'''
	将一个函数打包成一个描述该函数的tuple
	@param fun:函数对象
	@return: (函数所在的模块, 函数名)
	'''
	return fun.__module__, fun.__name__ 

def FunctionUnpack(moduleName, functionName):
	'''
	根据函数的描述，获取函数对象
	@param sModule:函数所在的模块
	@param sFunction:函数名
	@return: 函数对象
	'''
	__import__(moduleName)
	return getattr(sys.modules[moduleName], functionName)

if "_HasLoad" not in dir():
	FunctionPack = FunctionPack_Uncheck
	del FunctionPack_Check
	del FunctionPack_Uncheck


