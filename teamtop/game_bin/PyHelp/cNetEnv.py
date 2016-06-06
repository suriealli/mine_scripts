#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有3个Py函数定义

def SetCanForward( uSessionID):
	'''
	设置网络层消息可重定向
	@param uSessionID : UI32
	@return: None 
			 line 18 Py_RETURN_NONE;
	@see : { "SetCanForward", SetCanForward, METH_O, "设置网络层消息可重定向 " },
	'''

def SetCanCombineMsg( ):
	'''
	设置网络层消息可拼包
	@return: None 
			 line 24 Py_RETURN_NONE;
	@see : { "SetCanCombineMsg", SetCanCombineMsg, METH_NOARGS, "设置网络层消息可拼包 " },
	'''

def SetTWGMaxSize( uSize):
	'''
	设置腾讯TGW的换行符数量
	@param uSize : UI16
	@return: None 
			 line 35 Py_RETURN_NONE;
	@see : { "SetTWGMaxSize", SetTWGMaxSize, METH_NOARGS, "设置腾讯TGW的换行符数量 " },
	'''

#automatic_end
