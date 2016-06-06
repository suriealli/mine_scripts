#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有6个Py函数定义

def StartTransaction( uTransaction):
	'''
	开启事务
	@param uTransaction : UI16
	@return: None 
			 line 16 Py_RETURN_NONE;
	@see : {"StartTransaction", (PyCFunction)StartTransaction, METH_O, "开启事务  "},
	'''

def EndTransaction( ):
	'''
	关闭事务
	@return: None 
			 line 22 Py_RETURN_NONE;
	@see : {"EndTransaction", (PyCFunction)EndTransaction, METH_NOARGS, "关闭事务  "},
	'''

def HasTransaction( ):
	'''
	是否有事务
	@see : {"HasTransaction", (PyCFunction)HasTransaction, METH_NOARGS, "是否有事务  "},
	'''

def GetTransaction( ):
	'''
	获取事务
	@return: UI16,I64 
			 line 35 return Py_BuildValue("HL", uTransaction, nLogID);
	@see : {"GetTransaction", (PyCFunction)GetTransaction, METH_NOARGS, "获取事务  "},
	'''

def GetTransactionForEvent( ):
	'''
	为事件获取事务
	@return: UI16,I64 
			 line 43 return Py_BuildValue("HL", uTransaction, nLogID);
	@see : {"GetTransactionForEvent", (PyCFunction)GetTransactionForEvent, METH_NOARGS, "为事件获取事务  "},
	'''

def GetEvent( ):
	'''
	获取事件
	@return: UI32 
			 line 48 return GEPython::PyObjFromUI32(LogTransaction::Instance()->GetEvent());
	@see : {"GetEvent", (PyCFunction)GetEvent, METH_NOARGS, "获取事件  "},
	'''

#automatic_end
