#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有3个Py函数定义

def PackPyMsg( uMsgType, pyObj):
	'''
	预打包一个消息
	@param uMsgType : UI16
	@param pyObj : PyObject*
	@see : { "PackPyMsg", PackPyMsg, METH_VARARGS, "预打包一个消息 " },
	'''

def MsgToString( ):
	'''
	消息序列化
	@return: PyObject* 
			 line 30 return PyString_FromStringAndSize(static_cast<const char*>(PackMessage::Instance()->GetHead()), PackMessage::Instance()->GetSize());
	@warning: return PyString_FromStringAndSize(static_cast<const char*>(PackMessage::Instance()->GetHead()), PackMessage::Instance()->GetSize());
	@see : { "MsgToString", MsgToString, METH_NOARGS, "消息序列化 " },
	'''

def StringToMsg( carg):
	'''
	消息反序列化
	@param carg : string
	@return: None 
			 line 45 Py_RETURN_NONE;
	@warning: if (!PyString_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyString_GET_SIZE(arg));
	@see : { "StringToMsg", StringToMsg, METH_O, "消息反序列化 " },
	'''

#automatic_end
