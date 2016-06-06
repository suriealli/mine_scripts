#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有3个Py函数定义

def AllotFlagIndex( ):
	'''
	分配一个标识标识
	@return: UI32 
			 line 11 return GEPython::PyObjFromUI32(ScriptMgr::Instance()->AllotFlagIndex());
	@see : { "AllotFlagIndex", AllotFlagIndex, METH_NOARGS, "分配一个标识标识 " },
	'''

def DirtyFlag( uIdx):
	'''
	弄脏一个标识
	@param uIdx : UI16
	@return: None 
			 line 26 Py_RETURN_NONE;
	@see : { "DirtyFlag", DirtyFlag, METH_O, "弄脏一个标识 " },
	'''

def SetClearFun( uIdx, pyCallable):
	'''
	设置清理一个标识的函数
	@param uIdx : UI16
	@param pyCallable : PyObject*
	@return: None 
			 line 42 Py_RETURN_NONE;
	@see : { "SetClearFun", SetClearFun, METH_VARARGS, "设置清理一个标识的函数 " },
	'''

#automatic_end
