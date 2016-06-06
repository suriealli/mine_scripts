#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# ---------------------E:\GameProject\CCode\ComplexServer\\PyLogStmt.cpp------------------------
# 有5个Py函数定义

def OnConnect( arg):
	'''
	预处理连接上
	@param arg : PyObject*
	@return: None 
			 line 68 Py_RETURN_NONE;
	@warning: _mysql_ConnectionObject* pObj = Py_mysql_ConnectionObject_FromObj(arg);
	@see : {"OnConnect", (PyCFunction)OnConnect, METH_O, "预处理连接上"},
	'''

def OnDisconnect( ):
	'''
	预处理断开连接
	@return: None 
			 line 74 Py_RETURN_NONE;
	@see : {"OnDisconnect", (PyCFunction)OnDisconnect, METH_NOARGS, "预处理断开连接"},
	'''

def LogBase( nLogID, uRoleId, uTransaction, uEvent, pObjContent):
	'''
	基本日志
	@param nLogID : I64
	@param uRoleId : UI64
	@param uTransaction : UI16
	@param uEvent : UI16
	@param pObjContent : PyObject*
	@return: None 
			 line 115 Py_RETURN_NONE;
	@see : {"LogBase", (PyCFunction)LogBase, METH_VARARGS, "基本日志"},
	'''

def LogObj( nLogID, uRoleId, uTransaction, uEvent, uObjId, uObjType, uObjInt, pObjContent, pObjData):
	'''
	对象日志
	@param nLogID : I64
	@param uRoleId : UI64
	@param uTransaction : UI16
	@param uEvent : UI16
	@param uObjId : UI64
	@param uObjType : UI32
	@param uObjInt : UI32
	@param pObjContent : PyObject*
	@param pObjData : PyObject*
	@return: None 
			 line 172 Py_RETURN_NONE;
	@see : {"LogObj", (PyCFunction)LogObj, METH_VARARGS, "对象日志"},
	'''

def LogValue( nLogID, uRoleId, uTransaction, uEvent, uOldValue, uNewValue, pObjContent):
	'''
	数值日志
	@param nLogID : I64
	@param uRoleId : UI64
	@param uTransaction : UI16
	@param uEvent : UI16
	@param uOldValue : I64
	@param uNewValue : I64
	@param pObjContent : PyObject*
	@return: None 
			 line 216 Py_RETURN_NONE;
	@see : {"LogValue", (PyCFunction)LogValue, METH_VARARGS, "数值日志"},
	'''

#automatic_end
