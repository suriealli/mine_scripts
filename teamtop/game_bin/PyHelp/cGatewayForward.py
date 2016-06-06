#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有10个Py函数定义

def OnClient_New( uSessionID, uProcessID):
	'''
	新的客户端连接（被动）
	@param uSessionID : UI32
	@param uProcessID : UI16
	@return: None 
			 line 19 Py_RETURN_NONE;
	@see : { "OnClient_New", OnClient_New, METH_VARARGS, "新的客户端连接（被动）  "},
	'''

def OnClient_Lost( uSessionID):
	'''
	失去客户端连接（被动）
	@param uSessionID : UI32
	@return: None 
			 line 30 Py_RETURN_NONE;
	@see : { "OnClient_Lost", OnClient_Lost, METH_O, "失去客户端连接（被动）  "},
	'''

def OnGatewayNew( uSessionID):
	'''
	新的网关连接（主动）
	@param uSessionID : UI32
	@return: None 
			 line 41 Py_RETURN_NONE;
	@see : { "OnGatewayNew", OnGatewayNew, METH_O, "新的网关连接（主动）  "},
	'''

def OnGatewayLost( uSessionID):
	'''
	失去网关连接（主动）
	@param uSessionID : UI32
	@return: None 
			 line 52 Py_RETURN_NONE;
	@see : { "OnGatewayLost", OnGatewayLost, METH_O, "失去网关连接（主动）  "},
	'''

def UseGateway( ):
	'''
	使用网关
	@return: None 
			 line 58 Py_RETURN_NONE;
	@see : { "UseGateway", UseGateway, METH_NOARGS, "使用网关  "},
	'''

def OnGateway_New( uSessionID):
	'''
	新的网关连接（被动）
	@param uSessionID : UI32
	@return: None 
			 line 69 Py_RETURN_NONE;
	@see : { "OnGateway_New", OnGateway_New, METH_O, "新的网关连接（被动）  "},
	'''

def OnGateway_Lost( uSessionID):
	'''
	失去网关连接（被动）
	@param uSessionID : UI32
	@return: None 
			 line 80 Py_RETURN_NONE;
	@see : { "OnGateway_Lost", OnGateway_Lost, METH_O, "失去网关连接（被动）  "},
	'''

def SendClientMsg( uClientKey, uMsgType, pMsg_BorrowRef=None ):
	'''
	给客户端连接发送Python消息
	@param uClientKey : UI64
	@param uMsgType : UI16
	@param pMsg_BorrowRef : PyObject*
	@return: None 
			 line 96 Py_RETURN_NONE;
	@see : { "SendClientMsg", SendClientMsg, METH_VARARGS, "给客户端连接发送Python消息  "},
	'''

def BroadClientMsg( uMsgType, pMsg_BorrowRef=None ):
	'''
	给客户端连接广播Python消息
	@param uMsgType : UI32
	@param pMsg_BorrowRef : PyObject*
	@return: None 
			 line 111 Py_RETURN_NONE;
	@see : { "BroadClientMsg", BroadClientMsg, METH_VARARGS, "给客户端连接广播Python消息  "},
	'''

def KickClient( uClientKey):
	'''
	主动要求踢掉客户端连接
	@param uClientKey : UI64
	@return: None 
			 line 122 Py_RETURN_NONE;
	@see : { "KickClient", KickClient, METH_O, "主动要求踢掉客户端连接  "},
	'''

#automatic_end
