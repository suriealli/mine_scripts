#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有14个Py函数定义

def CreateRole( uRoleID, sRoleName, sOpenID, uClientKey, uCommandSize, uCommandIndex):
	'''
	创建一个角色
	@param uRoleID : UI64
	@param sRoleName : string
	@param sOpenID : string
	@param uClientKey : UI64
	@param uCommandSize : UI32
	@param uCommandIndex : UI32
	@return: None 
			 line 25 Py_RETURN_NONE;
	@return: PyObject* 
			 line 29 return pRole->GetPySelf().GetObj_NewRef();
	@warning: return pRole->GetPySelf().GetObj_NewRef();
	@see : { "CreateRole", CreateRole, METH_VARARGS, "创建一个角色  "},
	'''

def FindRoleByRoleID( uRoleID):
	'''
	根据角色ID查找角色
	@param uRoleID : UI64
	@return: None 
			 line 43 Py_RETURN_NONE;
	@return: PyObject* 
			 line 47 return pRole->GetPySelf().GetObj_NewRef();
	@warning: return pRole->GetPySelf().GetObj_NewRef();
	@see : { "FindRoleByRoleID", FindRoleByRoleID, METH_O, "根据角色ID查找角色  "},
	'''

def FindRoleByClientKey( uClientKey):
	'''
	根据ClientKey查找角色
	@param uClientKey : UI64
	@return: None 
			 line 61 Py_RETURN_NONE;
	@return: PyObject* 
			 line 65 return pRole->GetPySelf().GetObj_NewRef();
	@warning: return pRole->GetPySelf().GetObj_NewRef();
	@see : { "FindRoleByClientKey", FindRoleByClientKey, METH_O, "根据ClientKey查找角色  "},
	'''

def RegDistribute( uMsgType, pyFun):
	'''
	注册一个角色消息
	@param uMsgType : UI16
	@param pyFun : PyObject*
	@return: None 
			 line 79 Py_RETURN_NONE;
	@see : { "RegDistribute", RegRoleDistribute, METH_VARARGS, "注册一个角色消息  "},
	'''

def UnregDistribute( uMsgType):
	'''
	取消一个角色消息
	@param uMsgType : UI16
	@return: None 
			 line 90 Py_RETURN_NONE;
	@see : { "UnregDistribute", UnregRoleDistribute, METH_O, "取消一个角色消息  "},
	'''

def BroadMsg( ):
	'''
	给所有角色广播消息
	@return: None 
			 line 96 Py_RETURN_NONE;
	@see : { "BroadMsg", BroadMsg, METH_NOARGS, "给所有角色广播消息  "},
	'''

def Msg( msg_b8_UI32_1, msg_b8_UI32_0, pObj):
	'''
	给所有角色广播消息
	@param msg_b8_UI32_1 : I32
	@param msg_b8_UI32_0 : I32
	@param pObj : PyObject*
	@return: None 
			 line 112 Py_RETURN_NONE;
	@see : { "Msg", Msg, METH_VARARGS, "给所有角色广播消息  "},
	'''

def MsgPack( msg_b8_UI32_1, msg_b8_UI32_0, pObj):
	'''
	打包一条广播的提示消息
	@param msg_b8_UI32_1 : I32
	@param msg_b8_UI32_0 : I32
	@param pObj : PyObject*
	@return: None 
			 line 127 Py_RETURN_NONE;
	@see : { "MsgPack", MsgPack, METH_VARARGS, "打包一条广播的提示消息  " },
	'''

def GetAllRole( ):
	'''
	获取所有在线角色
	@return: PyObject* 
			 line 146 return lis.GetList_NewRef();
	@warning: return lis.GetList_NewRef();
	@see : { "GetAllRole", GetAllRole, METH_NOARGS, "获取所有在线角色  "},
	'''

def AddWatchRole( uRoleID):
	'''
	增加一个观察角色
	@param uRoleID : UI64
	@return: None 
			 line 157 Py_RETURN_NONE;
	@see : { "AddWatchRole", AddWatchRole, METH_O, "增加一个观察角色  "},
	'''

def ClearWatchRole( ):
	'''
	清空观察角色
	@return: None 
			 line 163 Py_RETURN_NONE;
	@see : { "ClearWatchRole", ClearWatchRole, METH_NOARGS, "清空观察角色  "},
	'''

def SetStatistics( arg):
	'''
	设置角色消息统计开关
	@param arg : PyObject*
	@return: None 
			 line 176 Py_RETURN_NONE;
	@warning: if (PyObject_IsTrue(arg))
	@see : { "SetStatistics", SetStatistics, METH_O, "设置角色消息统计开关  "},
	'''

def GetRoleMessage( ):
	'''
	获取角色消息统计结果
	@return: PyObject* 
			 line 206 return rold_dict.GetDict_NewRef();
	@warning: return rold_dict.GetDict_NewRef();
	@see : { "GetRoleMessage", GetRoleMessage, METH_NOARGS, "获取角色消息统计结果  "},
	'''

def SetEchoLevel( nLevel):
	'''
	设置角色消息统计开关
	@param nLevel : I32
	@return: None 
			 line 217 Py_RETURN_NONE;
	@see : { "SetEchoLevel", SetEchoLevel, METH_O, "设置角色消息统计开关  "},
	'''

#automatic_end

def __GetAllRole():
	return []
GetAllRole = __GetAllRole
