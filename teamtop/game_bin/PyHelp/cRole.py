#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有46个Py函数定义

def IsKick( ):
	'''
	角色是否已经被T掉
	@return: True 
			 line 23 Py_RETURN_TRUE;
	@return: False 
			 line 27 Py_RETURN_FALSE;
	@see : {"IsKick", (PyCFunction)IsKick, METH_NOARGS, "角色是否已经被T掉   "},
	'''

def Kick( isSave, res):
	'''
	T掉角色
	@param isSave : PyObject*
	@param res : PyObject*
	@return: None 
			 line 41 Py_RETURN_NONE;
	@see : {"Kick", (PyCFunction)Kick, METH_VARARGS, "T掉角色   "},
	'''

def Save( ):
	'''
	保存角色数据
	@return: None 
			 line 48 Py_RETURN_NONE;
	@see : {"Save", (PyCFunction)Save, METH_VARARGS, "保存角色数据   "},
	'''

def IsLost( ):
	'''
	角色是否已经被T掉
	@see : {"IsLost", (PyCFunction)IsLost, METH_NOARGS, "角色是否已经被T掉   "},
	'''

def Lost( ):
	'''
	角色暂时断开连接
	@return: None 
			 line 61 Py_RETURN_NONE;
	@see : {"Lost", (PyCFunction)Lost, METH_NOARGS, "角色暂时断开连接   "},
	'''

def ReLogin( uClientKey):
	'''
	断开连接的角色重新连接上
	@param uClientKey : UI64
	@see : {"ReLogin", (PyCFunction)ReLogin, METH_O, "断开连接的角色重新连接上   "},
	'''

def SyncByReLogin( ):
	'''
	角色重新连接，同步数组数据
	@return: None 
			 line 81 Py_RETURN_NONE;
	@see : {"SyncByReLogin", (PyCFunction)SyncByReLogin, METH_NOARGS, "角色重新连接，同步数组数据   "},
	'''

def ClearPerDay( ):
	'''
	角色每日清理
	@return: None 
			 line 88 Py_RETURN_NONE;
	@see : {"ClearPerDay", (PyCFunction)ClearPerDay, METH_NOARGS, "角色每日清理   "},
	'''

def CountTiLi( ):
	'''
	角色登录计算体力
	@return: None 
			 line 95 Py_RETURN_NONE;
	@see : {"CountTiLi", (PyCFunction)CountTiLi, METH_NOARGS, "角色登录计算体力   "},
	'''

def GetRoleID( ):
	'''
	获取角色ID
	@return: PyObject* 
			 line 101 return self->role_id;
	@warning: return self->role_id;
	@see : {"GetRoleID", (PyCFunction)GetRoleID, METH_NOARGS, "获取角色ID   "},
	'''

def GetClientKey( ):
	'''
	获取角色ClientKey
	@return: UI64 
			 line 107 return GEPython::PyObjFromUI64(self->cptr->GetClientKey());
	@see : {"GetClientKey", (PyCFunction)GetClientKey, METH_NOARGS, "获取角色ClientKey   "},
	'''

def RemoteEndPoint( ):
	'''
	获取角色连接IP
	@return: String 
			 line 119 return PyString_FromString(sIp.c_str());
	@return: None 
			 line 121 Py_RETURN_NONE;
	@see : {"RemoteEndPoint", (PyCFunction)RemoteEndPoint, METH_NOARGS, "获取角色连接IP   "},
	'''

def GetScene( ):
	'''
	获取场景
	@return: None 
			 line 131 Py_RETURN_NONE;
	@return: PyObject* 
			 line 133 return pScene->PySelf().GetObj_NewRef();
	@warning: return pScene->PySelf().GetObj_NewRef();
	@see : {"GetScene", (PyCFunction)GetScene, METH_NOARGS, "获取场景   "},
	'''

def GetSceneID( ):
	'''
	获取场景ID
	@return: UI32 
			 line 139 return GEPython::PyObjFromUI32(self->cptr->GetSceneID());
	@see : {"GetSceneID", (PyCFunction)GetSceneID, METH_NOARGS, "获取场景ID   "},
	'''

def GetLastSceneID( ):
	'''
	获取最后所在场景ID
	@return: UI32 
			 line 145 return GEPython::PyObjFromUI32(self->cptr->GetLastSceneID());
	@see : {"GetLastSceneID", (PyCFunction)GetLastSceneID, METH_NOARGS, "获取最后所在场景ID   "},
	'''

def GetPos( ):
	'''
	获取角色位置
	@return: UI16,UI16 
			 line 151 return Py_BuildValue("HH", self->cptr->GetPosX(), self->cptr->GetPosY());
	@see : {"GetPos", (PyCFunction)GetPos, METH_NOARGS, "获取角色位置   "},
	'''

def GetLastPos( ):
	'''
	获取角色最后所在位置
	@return: UI16,UI16 
			 line 157 return Py_BuildValue("HH", self->cptr->GetLastPosX(), self->cptr->GetLastPosY());
	@see : {"GetLastPos", (PyCFunction)GetLastPos, METH_NOARGS, "获取角色最后所在位置   "},
	'''

def DoIdle( ):
	'''
	服务器强制玩家静止
	@return: None 
			 line 164 Py_RETURN_NONE;
	@see : {"DoIdle", (PyCFunction)DoIdle, METH_NOARGS, "服务器强制玩家静止   "},
	'''

def SyncDataBase( ):
	'''
	同步角色基础数据
	@return: None 
			 line 171 Py_RETURN_NONE;
	@see : {"SyncDataBase", (PyCFunction)SyncDataBase, METH_NOARGS, "同步角色基础数据   "},
	'''

def SyncOK( ):
	'''
	同步角色基础数据OK
	@return: None 
			 line 177 Py_RETURN_NONE;
	@see : {"SyncOK", (PyCFunction)SyncOK, METH_NOARGS, "同步角色基础数据OK   "},
	'''

def GetRoleName( ):
	'''
	获取角色名
	@return: PyObject* 
			 line 183 return PyString_FromStringAndSize(self->cptr->GetRoleName().data(), self->cptr->GetRoleName().length());
	@warning: return PyString_FromStringAndSize(self->cptr->GetRoleName().data(), self->cptr->GetRoleName().length());
	@see : {"GetRoleName", (PyCFunction)GetRoleName, METH_NOARGS, "获取角色名   "},
	'''

def SetRoleName( arg):
	'''
	设置角色名
	@param arg : PyObject*
	@return: None 
			 line 195 Py_RETURN_NONE;
	@warning: if (!GEPython::PyObjToStr(arg, &sRoleName))
	@see : {"SetRoleName", (PyCFunction)SetRoleName, METH_O, "设置角色名   "},
	'''

def GetVersion1( ):
	'''
	获取角色版本号
	@return: UI32 
			 line 201 return  GEPython::PyObjFromUI32(self->cptr->GetVersion1());
	@see : {"GetVersion1", (PyCFunction)GetVersion1, METH_NOARGS, "获取角色版本号   "},
	'''

def SetApperance( pyKey, pyValue):
	'''
	设置一个外观信息
	@param pyKey : PyObject*
	@param pyValue : PyObject*
	@return: None 
			 line 214 Py_RETURN_NONE;
	@see : {"SetApperance", (PyCFunction)SetApperance, METH_VARARGS, "设置一个外观信息   "},
	'''

def DoCommand( uIndex):
	'''
	执行了一个离线命令
	@param uIndex : UI32
	@see : {"DoCommand", (PyCFunction)DoCommand, METH_O, "执行了一个离线命令   "},
	'''

def GetCommand( ):
	'''
	获取最后执行的离线命令
	@return: UI32,UI32 
			 line 231 return Py_BuildValue("II", self->cptr->GetCommandSize(), self->cptr->GetCommandIndex());
	@see : {"GetCommand", (PyCFunction)GetCommand, METH_NOARGS, "获取最后执行的离线命令   "},
	'''

def SendObj( uMsgType, pyObj):
	'''
	发送一个消息
	@param uMsgType : UI16
	@param pyObj : PyObject*
	@return: None 
			 line 244 Py_RETURN_NONE;
	@see : {"SendObj", (PyCFunction)SendObj, METH_VARARGS, "发送一个消息   "},
	'''

def SendObj_NoExcept( uMsgType, pyObj):
	'''
	发送一个消息（不抛异常）
	@param uMsgType : UI16
	@param pyObj : PyObject*
	@return: None 
			 line 259 Py_RETURN_NONE;
	@see : {"SendObj_NoExcept", (PyCFunction)SendObj_NoExcept, METH_VARARGS, "发送一个消息（不抛异常）   "},
	'''

def SendObjAndBack( uMsgType, pyObj, uSec, pyFun, pyParam=None ):
	'''
	发送一个消息，并等待回调
	@param uMsgType : UI16
	@param pyObj : PyObject*
	@param uSec : UI16
	@param pyFun : PyObject*
	@param pyParam : PyObject*
	@return: None 
			 line 275 Py_RETURN_NONE;
	@see : {"SendObjAndBack", (PyCFunction)SendObjAndBack, METH_VARARGS, "发送一个消息，并等待回调   "},
	'''

def SendObjAndBack_NoExcept( uMsgType, pyObj, uSec, pyFun, pyParam=None ):
	'''
	发送一个消息，并等待回调（不抛异常）
	@param uMsgType : UI16
	@param pyObj : PyObject*
	@param uSec : UI16
	@param pyFun : PyObject*
	@param pyParam : PyObject*
	@return: None 
			 line 293 Py_RETURN_NONE;
	@see : {"SendObjAndBack_NoExcept", (PyCFunction)SendObjAndBack_NoExcept, METH_VARARGS, "发送一个消息，并等待回调（不抛异常）   "},
	'''

def CallBackFunction( uFunID, pyObj=None ):
	'''
	回调一个消息
	@param uFunID : UI32
	@param pyObj : PyObject*
	@return: None 
			 line 306 Py_RETURN_NONE;
	@see : {"CallBackFunction", (PyCFunction)CallBackFunction, METH_VARARGS, "回调一个消息   "},
	'''

def BroadMsg( ):
	'''
	发送一个广播消息给客户端
	@return: None 
			 line 313 Py_RETURN_NONE;
	@see : {"BroadMsg", (PyCFunction)BroadMsg, METH_NOARGS, "发送一个广播消息给客户端   "},
	'''

def BroadMsg_NoExcept( ):
	'''
	发送一个广播消息给客户端
	@return: None 
			 line 322 Py_RETURN_NONE;
	@see : {"BroadMsg_NoExcept", (PyCFunction)BroadMsg_NoExcept, METH_NOARGS, "发送一个广播消息给客户端   "},
	'''

def Msg( msg_b8_UI32_1, msg_b8_UI32_0, pObj):
	'''
	发送一个字符串给客户端
	@param msg_b8_UI32_1 : I32
	@param msg_b8_UI32_0 : I32
	@param pObj : PyObject*
	@return: None 
			 line 339 Py_RETURN_NONE;
	@see : {"Msg", (PyCFunction)Msg, METH_VARARGS, "发送一个字符串给客户端   "},
	'''

def WPE( uCnt=None ):
	'''
	该角色可能在发网络封包
	@param uCnt : UI16
	@return: None 
			 line 351 Py_RETURN_NONE;
	@see : {"WPE", (PyCFunction)WPE, METH_VARARGS, "该角色可能在发网络封包   "},
	'''

def RegTick( uSec, fun_BorrowRef, regparam_BorrowRef=None ):
	'''
	注册一个Tick
	@param uSec : UI32
	@param fun_BorrowRef : PyObject*
	@param regparam_BorrowRef : PyObject*
	@return: I32 
			 line 370 return GEPython::PyObjFromI32(ID);
	@see : {"RegTick", (PyCFunction)RegTick, METH_VARARGS, "注册一个Tick   "},
	'''

def UnregTick( ID):
	'''
	注销一个Tick
	@param ID : I32
	@return: None 
			 line 382 Py_RETURN_NONE;
	@see : {"UnregTick", (PyCFunction)UnregTick, METH_O, "注销一个Tick   "},
	'''

def TiggerTick( ID, param_BorrowRef=None ):
	'''
	触发一个Tick
	@param ID : I32
	@param param_BorrowRef : PyObject*
	@return: None 
			 line 395 Py_RETURN_NONE;
	@see : {"TiggerTick", (PyCFunction)TiggerTick, METH_VARARGS, "触发一个Tick   "},
	'''

def SetChatInfo( pyKey, pyValue):
	'''
	设置聊天角色信息
	@param pyKey : PyObject*
	@param pyValue : PyObject*
	@return: None 
			 line 408 Py_RETURN_NONE;
	@see : {"SetChatInfo", (PyCFunction)SetChatInfo, METH_VARARGS, "设置聊天角色信息   "},
	'''

def BroadChat( uParam, pyObj):
	'''
	py广播一个世界聊天信息
	@param uParam : UI16
	@param pyObj : PyObject*
	@return: None 
			 line 429 Py_RETURN_NONE;
	@see : {"BroadChat", (PyCFunction)BroadChat, METH_VARARGS, "py广播一个世界聊天信息   "},
	'''

def Revive( uSceneID, uX, uY):
	'''
	角色传送
	@param uSceneID : UI32
	@param uX : UI16
	@param uY : UI16
	@return: None 
			 line 449 Py_RETURN_NONE;
	@see : {"Revive", (PyCFunction)Revive, METH_VARARGS, "角色传送   "},
	'''

def BackPublicScene( ):
	'''
	角色传送回去上一个保存坐标的场景
	@return: None 
			 line 467 Py_RETURN_NONE;
	@return: None 
			 line 474 Py_RETURN_NONE;
	@see : {"BackPublicScene", (PyCFunction)BackPublicScene, METH_NOARGS, "角色传送回去上一个保存坐标的场景   "},
	'''

def JumpPos( uX, uY):
	'''
	角色传送
	@param uX : UI16
	@param uY : UI16
	@return: None 
			 line 494 Py_RETURN_NONE;
	@see : {"JumpPos", (PyCFunction)JumpPos, METH_VARARGS, "角色传送   "},
	'''

def ForceRecountProperty( ):
	'''
	强制重算一下角色属性
	@return: None 
			 line 504 Py_RETURN_NONE;
	@see : {"ForceRecountProperty", (PyCFunction)ForceRecountProperty, METH_NOARGS, "强制重算一下角色属性   "},
	'''

def SetNeedRecount( ):
	'''
	设置需要重算
	@return: None 
			 line 511 Py_RETURN_NONE;
	@see : {"SetNeedRecount", (PyCFunction)SetNeedRecount, METH_NOARGS, "设置需要重算   "},
	'''

def FinishRecount( ):
	'''
	完成一次重算
	@return: None 
			 line 518 Py_RETURN_NONE;
	@see : {"FinishRecount", (PyCFunction)FinishRecount, METH_NOARGS, "完成一次重算   "},
	'''

# 有70个Py函数定义

def InitI64( arg):
	'''
	初始化I64数组
	@param arg : PyObject*
	@return: None 
			 line 10 Py_RETURN_NONE;
	@warning: self->cptr->InitI64(arg);
	@see : {"InitI64", (PyCFunction)InitI64, METH_O, "初始化I64数组   "},	\
	'''

def SeriI64( ):
	'''
	序列化I64数组
	@return: PyObject* 
			 line 16 return self->cptr->SeriI64_NewRef();
	@warning: return self->cptr->SeriI64_NewRef();
	@see : {"SeriI64", (PyCFunction)SeriI64, METH_NOARGS, "序列化I64数组   "},	\
	'''

def GetI64( uIdx):
	'''
	获取I64数组值
	@param uIdx : UI16
	@return: I64 
			 line 31 return GEPython::PyObjFromI64(self->cptr->GetI64(uIdx));
	@see : {"GetI64", (PyCFunction)GetI64, METH_O, "获取I64数组值   "},	\
	'''

def SetI64( uIdx, nValue):
	'''
	设置I64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 48 Py_RETURN_NONE;
	@see : {"SetI64", (PyCFunction)SetI64, METH_VARARGS, "设置I64数组值   "},	\
	'''

def IncI64( uIdx, nValue):
	'''
	增加I64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 69 Py_RETURN_NONE;
	@see : {"IncI64", (PyCFunction)IncI64, METH_VARARGS, "增加I64数组值   "},	\
	'''

def DecI64( uIdx, nValue):
	'''
	减少I64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 90 Py_RETURN_NONE;
	@see : {"DecI64", (PyCFunction)DecI64, METH_VARARGS, "减少I64数组值   "},	\
	'''

def InitDI32( arg):
	'''
	初始化DI32数组
	@param arg : PyObject*
	@return: None 
			 line 98 Py_RETURN_NONE;
	@warning: self->cptr->InitDI32(arg);
	@see : {"InitDI32", (PyCFunction)InitDI32, METH_O, "初始化DI32数组   "},	\
	'''

def SeriDI32( ):
	'''
	序列化DI32数组
	@return: PyObject* 
			 line 104 return self->cptr->SeriDI32_NewRef();
	@warning: return self->cptr->SeriDI32_NewRef();
	@see : {"SeriDI32", (PyCFunction)SeriDI32, METH_NOARGS, "序列化DI32数组   "},	\
	'''

def GetDI32( uIdx):
	'''
	获取DI32数组值
	@param uIdx : UI16
	@return: I32 
			 line 119 return GEPython::PyObjFromI32(self->cptr->GetDI32(uIdx));
	@see : {"GetDI32", (PyCFunction)GetDI32, METH_O, "获取DI32数组值   "},	\
	'''

def SetDI32( uIdx, nValue):
	'''
	设置DI32数组值
	@param uIdx : UI16
	@param nValue : I32
	@return: None 
			 line 136 Py_RETURN_NONE;
	@see : {"SetDI32", (PyCFunction)SetDI32, METH_VARARGS, "设置DI32数组值   "},	\
	'''

def IncDI32( uIdx, nValue):
	'''
	增加DI32数组值
	@param uIdx : UI16
	@param nValue : I32
	@return: None 
			 line 157 Py_RETURN_NONE;
	@see : {"IncDI32", (PyCFunction)IncDI32, METH_VARARGS, "增加DI32数组值   "},	\
	'''

def DecDI32( uIdx, nValue):
	'''
	减少DI32数组值
	@param uIdx : UI16
	@param nValue : I32
	@return: None 
			 line 178 Py_RETURN_NONE;
	@see : {"DecDI32", (PyCFunction)DecDI32, METH_VARARGS, "减少DI32数组值   "},	\
	'''

def InitI32( arg):
	'''
	初始化I32数组
	@param arg : PyObject*
	@return: None 
			 line 186 Py_RETURN_NONE;
	@warning: self->cptr->InitI32(arg);
	@see : {"InitI32", (PyCFunction)InitI32, METH_O, "初始化I32数组   "},	\
	'''

def SeriI32( ):
	'''
	序列化I32数组
	@return: PyObject* 
			 line 192 return self->cptr->SeriI32_NewRef();
	@warning: return self->cptr->SeriI32_NewRef();
	@see : {"SeriI32", (PyCFunction)SeriI32, METH_NOARGS, "序列化I32数组   "},	\
	'''

def GetI32( uIdx):
	'''
	获取I32数组值
	@param uIdx : UI16
	@return: I32 
			 line 207 return GEPython::PyObjFromI32(self->cptr->GetI32(uIdx));
	@see : {"GetI32", (PyCFunction)GetI32, METH_O, "获取I32数组值   "},	\
	'''

def SetI32( uIdx, nValue):
	'''
	设置I32数组值
	@param uIdx : UI16
	@param nValue : I32
	@return: None 
			 line 224 Py_RETURN_NONE;
	@see : {"SetI32", (PyCFunction)SetI32, METH_VARARGS, "设置I32数组值   "},	\
	'''

def IncI32( uIdx, nValue):
	'''
	增加I32数组值
	@param uIdx : UI16
	@param nValue : I32
	@return: None 
			 line 245 Py_RETURN_NONE;
	@see : {"IncI32", (PyCFunction)IncI32, METH_VARARGS, "增加I32数组值   "},	\
	'''

def DecI32( uIdx, nValue):
	'''
	减少I32数组值
	@param uIdx : UI16
	@param nValue : I32
	@return: None 
			 line 266 Py_RETURN_NONE;
	@see : {"DecI32", (PyCFunction)DecI32, METH_VARARGS, "减少I32数组值   "},	\
	'''

def InitI16( arg):
	'''
	初始化I16数组
	@param arg : PyObject*
	@return: None 
			 line 274 Py_RETURN_NONE;
	@warning: self->cptr->InitI16(arg);
	@see : {"InitI16", (PyCFunction)InitI16, METH_O, "初始化I16数组   "},	\
	'''

def SeriI16( ):
	'''
	序列化I16数组
	@return: PyObject* 
			 line 280 return self->cptr->SeriI16_NewRef();
	@warning: return self->cptr->SeriI16_NewRef();
	@see : {"SeriI16", (PyCFunction)SeriI16, METH_NOARGS, "序列化I16数组   "},	\
	'''

def GetI16( uIdx):
	'''
	获取I16数组值
	@param uIdx : UI16
	@return: I32 
			 line 295 return GEPython::PyObjFromI32(self->cptr->GetI16(uIdx));
	@see : {"GetI16", (PyCFunction)GetI16, METH_O, "获取I16数组值   "},	\
	'''

def SetI16( uIdx, nValue):
	'''
	设置I16数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 312 Py_RETURN_NONE;
	@see : {"SetI16", (PyCFunction)SetI16, METH_VARARGS, "设置I16数组值   "},	\
	'''

def IncI16( uIdx, nValue):
	'''
	增加I16数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 333 Py_RETURN_NONE;
	@see : {"IncI16", (PyCFunction)IncI16, METH_VARARGS, "增加I16数组值   "},	\
	'''

def DecI16( uIdx, nValue):
	'''
	减少I16数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 354 Py_RETURN_NONE;
	@see : {"DecI16", (PyCFunction)DecI16, METH_VARARGS, "减少I16数组值   "},	\
	'''

def InitI8( arg):
	'''
	初始化I8数组
	@param arg : PyObject*
	@return: None 
			 line 362 Py_RETURN_NONE;
	@warning: self->cptr->InitI8(arg);
	@see : {"InitI8", (PyCFunction)InitI8, METH_O, "初始化I8数组   "},	\
	'''

def SeriI8( ):
	'''
	序列化I8数组
	@return: PyObject* 
			 line 368 return self->cptr->SeriI8_NewRef();
	@warning: return self->cptr->SeriI8_NewRef();
	@see : {"SeriI8", (PyCFunction)SeriI8, METH_NOARGS, "序列化I8数组   "},	\
	'''

def GetI8( uIdx):
	'''
	获取I8数组值
	@param uIdx : UI16
	@return: I32 
			 line 383 return GEPython::PyObjFromI32(self->cptr->GetI8(uIdx));
	@see : {"GetI8", (PyCFunction)GetI8, METH_O, "获取I8数组值   "},	\
	'''

def SetI8( uIdx, nValue):
	'''
	设置I8数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 400 Py_RETURN_NONE;
	@see : {"SetI8", (PyCFunction)SetI8, METH_VARARGS, "设置I8数组值   "},	\
	'''

def IncI8( uIdx, nValue):
	'''
	增加I8数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 421 Py_RETURN_NONE;
	@see : {"IncI8", (PyCFunction)IncI8, METH_VARARGS, "增加I8数组值   "},	\
	'''

def DecI8( uIdx, nValue):
	'''
	减少I8数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 442 Py_RETURN_NONE;
	@see : {"DecI8", (PyCFunction)DecI8, METH_VARARGS, "减少I8数组值   "},	\
	'''

def InitDI8( arg):
	'''
	初始化DI8数组
	@param arg : PyObject*
	@return: None 
			 line 449 Py_RETURN_NONE;
	@warning: self->cptr->InitDI8(arg);
	@see : {"InitDI8", (PyCFunction)InitDI8, METH_O, "初始化DI8数组   "},	\
	'''

def SeriDI8( ):
	'''
	序列化DI8数组
	@return: PyObject* 
			 line 455 return self->cptr->SeriDI8_NewRef();
	@warning: return self->cptr->SeriDI8_NewRef();
	@see : {"SeriDI8", (PyCFunction)SeriDI8, METH_NOARGS, "序列化DI8数组   "},	\
	'''

def GetDI8( uIdx):
	'''
	获取DI8数组值
	@param uIdx : UI16
	@return: I32 
			 line 470 return GEPython::PyObjFromI32(self->cptr->GetDI8(uIdx));
	@see : {"GetDI8", (PyCFunction)GetDI8, METH_O, "获取DI8数组值   "},	\
	'''

def SetDI8( uIdx, nValue):
	'''
	设置DI8数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 487 Py_RETURN_NONE;
	@see : {"SetDI8", (PyCFunction)SetDI8, METH_VARARGS, "设置DI8数组值   "},	\
	'''

def IncDI8( uIdx, nValue):
	'''
	增加DI8数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 508 Py_RETURN_NONE;
	@see : {"IncDI8", (PyCFunction)IncDI8, METH_VARARGS, "增加DI8数组值   "},	\
	'''

def DecDI8( uIdx, nValue):
	'''
	减少DI8数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 529 Py_RETURN_NONE;
	@see : {"DecDI8", (PyCFunction)DecDI8, METH_VARARGS, "减少DI8数组值   "},	\
	'''

def InitI1( arg):
	'''
	初始化I1数组
	@param arg : PyObject*
	@return: None 
			 line 537 Py_RETURN_NONE;
	@warning: self->cptr->InitI1(arg);
	@see : {"InitI1", (PyCFunction)InitI1, METH_O, "初始化I1数组   "},	\
	'''

def SeriI1( ):
	'''
	序列化I1数组
	@return: PyObject* 
			 line 543 return self->cptr->SeriI1_NewRef();
	@warning: return self->cptr->SeriI1_NewRef();
	@see : {"SeriI1", (PyCFunction)SeriI1, METH_NOARGS, "序列化I1数组   "},	\
	'''

def GetI1( uIdx):
	'''
	获取I1数组值
	@param uIdx : UI16
	@see : {"GetI1", (PyCFunction)GetI1, METH_O, "获取I1数组值   "},	\
	'''

def SetI1( uIdx, pValue):
	'''
	设置I1数组值
	@param uIdx : UI16
	@param pValue : PyObject*
	@return: None 
			 line 582 Py_RETURN_NONE;
	@see : {"SetI1", (PyCFunction)SetI1, METH_VARARGS, "设置I1数组值   "},	\
	'''

def InitDI1( arg):
	'''
	初始化DI1数组
	@param arg : PyObject*
	@return: None 
			 line 589 Py_RETURN_NONE;
	@warning: self->cptr->InitDI1(arg);
	@see : {"InitDI1", (PyCFunction)InitDI1, METH_O, "初始化DI1数组   "},	\
	'''

def SeriDI1( ):
	'''
	序列化DI1数组
	@return: PyObject* 
			 line 595 return self->cptr->SeriDI1_NewRef();
	@warning: return self->cptr->SeriDI1_NewRef();
	@see : {"SeriDI1", (PyCFunction)SeriDI1, METH_NOARGS, "序列化DI1数组   "},	\
	'''

def GetDI1( uIdx):
	'''
	获取DI1数组值
	@param uIdx : UI16
	@see : {"GetDI1", (PyCFunction)GetDI1, METH_O, "获取DI1数组值   "},	\
	'''

def SetDI1( uIdx, pValue):
	'''
	设置DI1数组值
	@param uIdx : UI16
	@param pValue : PyObject*
	@return: None 
			 line 634 Py_RETURN_NONE;
	@see : {"SetDI1", (PyCFunction)SetDI1, METH_VARARGS, "设置DI1数组值   "},	\
	'''

def InitDI64( arg):
	'''
	初始化DI64数组
	@param arg : PyObject*
	@return: None 
			 line 641 Py_RETURN_NONE;
	@warning: self->cptr->InitDI64(arg);
	@see : {"InitDI64", (PyCFunction)InitDI64, METH_O, "初始化DI64数组   "},	\
	'''

def SeriDI64( ):
	'''
	序列化DI64数组
	@return: PyObject* 
			 line 647 return self->cptr->SeriDI64_NewRef();
	@warning: return self->cptr->SeriDI64_NewRef();
	@see : {"SeriDI64", (PyCFunction)SeriDI64, METH_NOARGS, "序列化DI64数组   "},	\
	'''

def GetDI64( uIdx):
	'''
	获取DI64数组值
	@param uIdx : UI16
	@return: I64 
			 line 662 return GEPython::PyObjFromI64(self->cptr->GetDI64(uIdx));
	@see : {"GetDI64", (PyCFunction)GetDI64, METH_O, "获取DI64数组值   "},	\
	'''

def SetDI64( uIdx, nValue):
	'''
	设置DI64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 679 Py_RETURN_NONE;
	@see : {"SetDI64", (PyCFunction)SetDI64, METH_VARARGS, "设置DI64数组值   "},	\
	'''

def IncDI64( uIdx, nValue):
	'''
	增加DI64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 700 Py_RETURN_NONE;
	@see : {"IncDI64", (PyCFunction)IncDI64, METH_VARARGS, "增加DI64数组值   "},	\
	'''

def DecDI64( uIdx, nValue):
	'''
	减少DI64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 721 Py_RETURN_NONE;
	@see : {"DecDI64", (PyCFunction)DecDI64, METH_VARARGS, "减少DI64数组值   "},	\
	'''

def InitCI8( arg):
	'''
	初始化CI8数组
	@param arg : PyObject*
	@return: None 
			 line 729 Py_RETURN_NONE;
	@warning: self->cptr->InitCI8(arg);
	@see : {"InitCI8", (PyCFunction)InitCI8, METH_O, "初始化CI8数组   "},	\
	'''

def SeriCI8( ):
	'''
	序列化CI8数组
	@return: PyObject* 
			 line 735 return self->cptr->SeriCI8_NewRef();
	@warning: return self->cptr->SeriCI8_NewRef();
	@see : {"SeriCI8", (PyCFunction)SeriCI8, METH_NOARGS, "序列化CI8数组   "},	\
	'''

def GetCI8( uIdx):
	'''
	获取CI8数组值
	@param uIdx : UI16
	@return: I32 
			 line 750 return GEPython::PyObjFromI32(self->cptr->GetCI8(uIdx));
	@see : {"GetCI8", (PyCFunction)GetCI8, METH_O, "获取CI8数组值   "},	\
	'''

def SetCI8( uIdx, nValue):
	'''
	设置CI8数组值
	@param uIdx : UI16
	@param nValue : I16
	@return: None 
			 line 767 Py_RETURN_NONE;
	@see : {"SetCI8", (PyCFunction)SetCI8, METH_VARARGS, "设置CI8数组值   "},	\
	'''

def GetTI64( uIdx):
	'''
	获取TI64数组值
	@param uIdx : UI16
	@return: I64 
			 line 782 return GEPython::PyObjFromI64(self->cptr->GetTI64(uIdx));
	@see : {"GetTI64", (PyCFunction)GetTI64, METH_O, "获取TI64数组值   "},	\
	'''

def SetTI64( uIdx, nValue):
	'''
	设置TI64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 799 Py_RETURN_NONE;
	@see : {"SetTI64", (PyCFunction)SetTI64, METH_VARARGS, "设置TI64数组值   "},	\
	'''

def IncTI64( uIdx, nValue):
	'''
	增加TI64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 820 Py_RETURN_NONE;
	@see : {"IncTI64", (PyCFunction)IncTI64, METH_VARARGS, "增加TI64数组值   "},	\
	'''

def DecTI64( uIdx, nValue):
	'''
	减少TI64数组值
	@param uIdx : UI16
	@param nValue : I64
	@return: None 
			 line 841 Py_RETURN_NONE;
	@see : {"DecTI64", (PyCFunction)DecTI64, METH_VARARGS, "减少TI64数组值   "},	\
	'''

def InitObj( arg):
	'''
	初始化Obj数组
	@param arg : PyObject*
	@return: None 
			 line 848 Py_RETURN_NONE;
	@warning: self->cptr->InitObj(arg);
	@see : {"InitObj", (PyCFunction)InitObj, METH_O, "初始化Obj数组   "},	\
	'''

def SeriObj( ):
	'''
	序列化Obj数组
	@return: PyObject* 
			 line 854 return self->cptr->SeriObj_NewRef();
	@warning: return self->cptr->SeriObj_NewRef();
	@see : {"SeriObj", (PyCFunction)SeriObj, METH_NOARGS, "序列化Obj数组   "},	\
	'''

def GetObj( uIdx):
	'''
	获取Obj
	@param uIdx : UI16
	@return: PyObject* 
			 line 869 return self->cptr->GetObj_NewRef(uIdx);
	@warning: return self->cptr->GetObj_NewRef(uIdx);
	@see : {"GetObj", (PyCFunction)GetObj, METH_O, "获取Obj   "},	\
	'''

def GetObj_ReadOnly( uIdx):
	'''
	获取Obj（只读）
	@param uIdx : UI16
	@return: PyObject* 
			 line 884 return self->cptr->GetObj_ReadOnly_NewRef(uIdx);
	@warning: return self->cptr->GetObj_ReadOnly_NewRef(uIdx);
	@see : {"GetObj_ReadOnly", (PyCFunction)GetObj_ReadOnly, METH_O, "获取Obj（只读）   "},	\
	'''

def SetObj( uIdx, pValue):
	'''
	设置Obj
	@param uIdx : UI16
	@param pValue : PyObject*
	@return: None 
			 line 901 Py_RETURN_NONE;
	@see : {"SetObj", (PyCFunction)SetObj, METH_VARARGS, "设置Obj   "},	\
	'''

def GetObjVersion( uIdx):
	'''
	获取Obj版本号
	@param uIdx : UI16
	@return: I32 
			 line 916 return GEPython::PyObjFromI32(self->cptr->GetObjVersion(uIdx));
	@see : {"GetObjVersion", (PyCFunction)GetObjVersion, METH_O, "获取Obj版本号   "},	\
	'''

def InitCD( arg):
	'''
	初始化TI64数组
	@param arg : PyObject*
	@return: None 
			 line 923 Py_RETURN_NONE;
	@warning: self->cptr->InitCD(arg);
	@see : {"InitCD", (PyCFunction)InitCD, METH_O, "初始化TI64数组   "},	\
	'''

def SeriCD( ):
	'''
	序列化TI64数组
	@return: PyObject* 
			 line 929 return self->cptr->SeriCD_NewRef();
	@warning: return self->cptr->SeriCD_NewRef();
	@see : {"SeriCD", (PyCFunction)SeriCD, METH_NOARGS, "序列化TI64数组   "},	\
	'''

def GetCD( uIdx):
	'''
	获取CI8数组值
	@param uIdx : UI16
	@return: I32 
			 line 944 return GEPython::PyObjFromI32(self->cptr->GetCD(uIdx));
	@see : {"GetCD", (PyCFunction)GetCD, METH_O, "获取CI8数组值   "},	\
	'''

def SetCD( uIdx, nValue):
	'''
	设置CI8数组值
	@param uIdx : UI16
	@param nValue : I32
	@return: None 
			 line 961 Py_RETURN_NONE;
	@see : {"SetCD", (PyCFunction)SetCD, METH_VARARGS, "设置CI8数组值   "},	\
	'''

def GetTempObj( uIdx):
	'''
	获取TempObj数组值
	@param uIdx : UI16
	@return: PyObject* 
			 line 976 return self->cptr->GetTempObj_NewRef(uIdx);
	@warning: return self->cptr->GetTempObj_NewRef(uIdx);
	@see : {"GetTempObj", (PyCFunction)GetTempObj, METH_O, "获取TempObj数组值   "},	\
	'''

def SetTempObj( uIdx, pValue):
	'''
	设置TempObj数组值
	@param uIdx : UI16
	@param pValue : PyObject*
	@return: None 
			 line 993 Py_RETURN_NONE;
	@see : {"SetTempObj", (PyCFunction)SetTempObj, METH_VARARGS, "设置TempObj数组值   "},	\
	'''

# 有202个Py函数定义

def IncExp( arg):
	'''
	None
	@param arg : PyObject*
	@return: PyObject* 
			 line 237 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncExp", (PyCFunction)IncExp, METH_VARARGS, "None "}, \
	'''

def GetExpCoef( ):
	'''
	None
	@return: PyObject* 
			 line 245 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetExpCoef.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetExpCoef.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetExpCoef", (PyCFunction)GetExpCoef, METH_NOARGS, "None "}, \
	'''

def GetAllHero( ):
	'''
	获取所有英雄 英雄id --> 英雄对象
	@return: PyObject* 
			 line 253 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetAllHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetAllHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetAllHero", (PyCFunction)GetAllHero, METH_NOARGS, "获取所有英雄 英雄id --> 英雄对象 "}, \
	'''

def GetHero( arg):
	'''
	根据英雄id获取英雄对象 返回英雄对象或者None
	@param arg : PyObject*
	@return: PyObject* 
			 line 270 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetHero", (PyCFunction)GetHero, METH_VARARGS, "根据英雄id获取英雄对象 返回英雄对象或者None "}, \
	'''

def IsLocalServer( ):
	'''
	是否是本服(包括合服的角色)
	@return: PyObject* 
			 line 278 return PyObject_CallObject(ScriptHold::Instance()->m_pyIsLocalServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIsLocalServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IsLocalServer", (PyCFunction)IsLocalServer, METH_NOARGS, "是否是本服(包括合服的角色) "}, \
	'''

def GetPid( ):
	'''
	获取角色原始进程ID
	@return: PyObject* 
			 line 286 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPid.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPid.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetPid", (PyCFunction)GetPid, METH_NOARGS, "获取角色原始进程ID "}, \
	'''

def GotoLocalServer( arg):
	'''
	None
	@param arg : PyObject*
	@return: PyObject* 
			 line 303 return PyObject_CallObject(ScriptHold::Instance()->m_pyGotoLocalServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGotoLocalServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GotoLocalServer", (PyCFunction)GotoLocalServer, METH_VARARGS, "None "}, \
	'''

def GotoCrossServer( arg):
	'''
	None
	@param arg : PyObject*
	@return: PyObject* 
			 line 320 return PyObject_CallObject(ScriptHold::Instance()->m_pyGotoCrossServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGotoCrossServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GotoCrossServer", (PyCFunction)GotoCrossServer, METH_VARARGS, "None "}, \
	'''

def RegPersistenceTick( arg):
	'''
	None
	@param arg : PyObject*
	@return: PyObject* 
			 line 337 return PyObject_CallObject(ScriptHold::Instance()->m_pyRegPersistenceTick.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyRegPersistenceTick.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"RegPersistenceTick", (PyCFunction)RegPersistenceTick, METH_VARARGS, "None "}, \
	'''

def GetTeam( ):
	'''
	获取当前的组队对象
	@return: PyObject* 
			 line 345 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTeam.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTeam.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetTeam", (PyCFunction)GetTeam, METH_NOARGS, "获取当前的组队对象 "}, \
	'''

def HasTeam( ):
	'''
	判断角色是否有队伍了 team
	@return: PyObject* 
			 line 353 return PyObject_CallObject(ScriptHold::Instance()->m_pyHasTeam.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyHasTeam.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"HasTeam", (PyCFunction)HasTeam, METH_NOARGS, "判断角色是否有队伍了 team "}, \
	'''

def ClientCommand( arg):
	'''
	命令很多话执行命令
	@param arg : PyObject*
	@return: PyObject* 
			 line 370 return PyObject_CallObject(ScriptHold::Instance()->m_pyClientCommand.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyClientCommand.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ClientCommand", (PyCFunction)ClientCommand, METH_VARARGS, "命令很多话执行命令 "}, \
	'''

def AddHero( arg):
	'''
	直接增加一个英雄
	@param arg : PyObject*
	@return: PyObject* 
			 line 387 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddHero", (PyCFunction)AddHero, METH_VARARGS, "直接增加一个英雄 "}, \
	'''

def GetUnionObj( ):
	'''
	获取公会对象
	@return: PyObject* 
			 line 395 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnionObj.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnionObj.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetUnionObj", (PyCFunction)GetUnionObj, METH_NOARGS, "获取公会对象 "}, \
	'''

def AddWing( arg):
	'''
	添加一个翅膀
	@param arg : PyObject*
	@return: PyObject* 
			 line 412 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddWing.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddWing.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddWing", (PyCFunction)AddWing, METH_VARARGS, "添加一个翅膀 "}, \
	'''

def AddPet( arg):
	'''
	None
	@param arg : PyObject*
	@return: PyObject* 
			 line 429 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddPet.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddPet.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddPet", (PyCFunction)AddPet, METH_VARARGS, "None "}, \
	'''

def AddTarotCard( arg):
	'''
	增加一个命魂
	@param arg : PyObject*
	@return: PyObject* 
			 line 446 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddTarotCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddTarotCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddTarotCard", (PyCFunction)AddTarotCard, METH_VARARGS, "增加一个命魂 "}, \
	'''

def TarotPackageIsFull( ):
	'''
	命魂背包是否已经满了
	@return: PyObject* 
			 line 454 return PyObject_CallObject(ScriptHold::Instance()->m_pyTarotPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyTarotPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"TarotPackageIsFull", (PyCFunction)TarotPackageIsFull, METH_NOARGS, "命魂背包是否已经满了 "}, \
	'''

def GetTarotEmptySize( ):
	'''
	获取命魂背包格子数
	@return: PyObject* 
			 line 462 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTarotEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTarotEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetTarotEmptySize", (PyCFunction)GetTarotEmptySize, METH_NOARGS, "获取命魂背包格子数 "}, \
	'''

def ActiveWeddingRing( ):
	'''
	激活婚戒
	@return: PyObject* 
			 line 470 return PyObject_CallObject(ScriptHold::Instance()->m_pyActiveWeddingRing.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyActiveWeddingRing.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ActiveWeddingRing", (PyCFunction)ActiveWeddingRing, METH_NOARGS, "激活婚戒 "}, \
	'''

def AddTalentCard( arg):
	'''
	增加一个天赋卡
	@param arg : PyObject*
	@return: PyObject* 
			 line 487 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddTalentCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddTalentCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddTalentCard", (PyCFunction)AddTalentCard, METH_VARARGS, "增加一个天赋卡 "}, \
	'''

def AddMount( arg):
	'''
	None
	@param arg : PyObject*
	@return: PyObject* 
			 line 504 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddMount.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddMount.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddMount", (PyCFunction)AddMount, METH_VARARGS, "None "}, \
	'''

def ToLevel( arg):
	'''
	直接升至多少级
	@param arg : PyObject*
	@return: PyObject* 
			 line 521 return PyObject_CallObject(ScriptHold::Instance()->m_pyToLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyToLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ToLevel", (PyCFunction)ToLevel, METH_VARARGS, "直接升至多少级 "}, \
	'''

def GetOnLineTimeToday( ):
	'''
	获取当前累计在线时间
	@return: PyObject* 
			 line 529 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetOnLineTimeToday.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetOnLineTimeToday.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetOnLineTimeToday", (PyCFunction)GetOnLineTimeToday, METH_NOARGS, "获取当前累计在线时间 "}, \
	'''

def GetJTObj( ):
	'''
	获取战队对象(本服逻辑进程专用)
	@return: PyObject* 
			 line 537 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTObj.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTObj.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetJTObj", (PyCFunction)GetJTObj, METH_NOARGS, "获取战队对象(本服逻辑进程专用) "}, \
	'''

def GetJTeamScore( ):
	'''
	获取战队积分
	@return: PyObject* 
			 line 545 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTeamScore.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTeamScore.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetJTeamScore", (PyCFunction)GetJTeamScore, METH_NOARGS, "获取战队积分 "}, \
	'''

def GetTotalGemLevel( ):
	'''
	None
	@return: PyObject* 
			 line 553 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTotalGemLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTotalGemLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetTotalGemLevel", (PyCFunction)GetTotalGemLevel, METH_NOARGS, "None "}, \
	'''

def GetRoleZDL( ):
	'''
	None
	@return: PyObject* 
			 line 561 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRoleZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRoleZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetRoleZDL", (PyCFunction)GetRoleZDL, METH_NOARGS, "None "}, \
	'''

def GetHeroZDL( ):
	'''
	None
	@return: PyObject* 
			 line 569 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHeroZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHeroZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetHeroZDL", (PyCFunction)GetHeroZDL, METH_NOARGS, "None "}, \
	'''

def AddCardAtlas( arg):
	'''
	增加卡牌
	@param arg : PyObject*
	@return: PyObject* 
			 line 586 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddCardAtlas.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddCardAtlas.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddCardAtlas", (PyCFunction)AddCardAtlas, METH_VARARGS, "增加卡牌 "}, \
	'''

def CardAtlasPackageIsFull( ):
	'''
	卡牌图鉴背包是否满了
	@return: PyObject* 
			 line 594 return PyObject_CallObject(ScriptHold::Instance()->m_pyCardAtlasPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyCardAtlasPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"CardAtlasPackageIsFull", (PyCFunction)CardAtlasPackageIsFull, METH_NOARGS, "卡牌图鉴背包是否满了 "}, \
	'''

def CardAtlasPackageEmptySize( ):
	'''
	卡牌图鉴背包空格数
	@return: PyObject* 
			 line 602 return PyObject_CallObject(ScriptHold::Instance()->m_pyCardAtlasPackageEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyCardAtlasPackageEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"CardAtlasPackageEmptySize", (PyCFunction)CardAtlasPackageEmptySize, METH_NOARGS, "卡牌图鉴背包空格数 "}, \
	'''

def AddItem( arg):
	'''
	将一个物品加入背包 (coding
	@param arg : PyObject*
	@return: PyObject* 
			 line 619 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddItem", (PyCFunction)AddItem, METH_VARARGS, "将一个物品加入背包 (coding, cnt) "}, \
	'''

def DecPropCnt( arg):
	'''
	None
	@param arg : PyObject*
	@return: PyObject* 
			 line 636 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecPropCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecPropCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecPropCnt", (PyCFunction)DecPropCnt, METH_VARARGS, "None "}, \
	'''

def DelItem( arg):
	'''
	将一个物品从背包删除 (coding
	@param arg : PyObject*
	@return: PyObject* 
			 line 653 return PyObject_CallObject(ScriptHold::Instance()->m_pyDelItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDelItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DelItem", (PyCFunction)DelItem, METH_VARARGS, "将一个物品从背包删除 (coding, cnt) 返回真正删除的个数 "}, \
	'''

def DelProp( arg):
	'''
	将一个道具从背包删除 (propId) 返回是否删除成功
	@param arg : PyObject*
	@return: PyObject* 
			 line 670 return PyObject_CallObject(ScriptHold::Instance()->m_pyDelProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDelProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DelProp", (PyCFunction)DelProp, METH_VARARGS, "将一个道具从背包删除 (propId) 返回是否删除成功 "}, \
	'''

def FindGlobalProp( arg):
	'''
	根据道具id，查询一个全局的物品
	@param arg : PyObject*
	@return: PyObject* 
			 line 687 return PyObject_CallObject(ScriptHold::Instance()->m_pyFindGlobalProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyFindGlobalProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"FindGlobalProp", (PyCFunction)FindGlobalProp, METH_VARARGS, "根据道具id，查询一个全局的物品 "}, \
	'''

def FindItem( arg):
	'''
	根据道具coding，获取背包中的道具 返回道具对象或者None
	@param arg : PyObject*
	@return: PyObject* 
			 line 704 return PyObject_CallObject(ScriptHold::Instance()->m_pyFindItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyFindItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"FindItem", (PyCFunction)FindItem, METH_VARARGS, "根据道具coding，获取背包中的道具 返回道具对象或者None "}, \
	'''

def FindPackProp( arg):
	'''
	根据道具id，获取背包中的道具 返回道具对象或者None
	@param arg : PyObject*
	@return: PyObject* 
			 line 721 return PyObject_CallObject(ScriptHold::Instance()->m_pyFindPackProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyFindPackProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"FindPackProp", (PyCFunction)FindPackProp, METH_VARARGS, "根据道具id，获取背包中的道具 返回道具对象或者None "}, \
	'''

def ItemCnt( arg):
	'''
	获取物品数量 (coding) 返回物品数量
	@param arg : PyObject*
	@return: PyObject* 
			 line 738 return PyObject_CallObject(ScriptHold::Instance()->m_pyItemCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyItemCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ItemCnt", (PyCFunction)ItemCnt, METH_VARARGS, "获取物品数量 (coding) 返回物品数量 "}, \
	'''

def ItemCnt_NotTimeOut( arg):
	'''
	获取物品数量 (coding) 返回还没有过期的物品数量
	@param arg : PyObject*
	@return: PyObject* 
			 line 755 return PyObject_CallObject(ScriptHold::Instance()->m_pyItemCnt_NotTimeOut.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyItemCnt_NotTimeOut.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ItemCnt_NotTimeOut", (PyCFunction)ItemCnt_NotTimeOut, METH_VARARGS, "获取物品数量 (coding) 返回还没有过期的物品数量   "}, \
	'''

def PackageEmptySize( ):
	'''
	获取背包空格子数
	@return: PyObject* 
			 line 763 return PyObject_CallObject(ScriptHold::Instance()->m_pyPackageEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyPackageEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"PackageEmptySize", (PyCFunction)PackageEmptySize, METH_NOARGS, "获取背包空格子数 "}, \
	'''

def PackageIsFull( ):
	'''
	判断背包是否满
	@return: PyObject* 
			 line 771 return PyObject_CallObject(ScriptHold::Instance()->m_pyPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"PackageIsFull", (PyCFunction)PackageIsFull, METH_NOARGS, "判断背包是否满 "}, \
	'''

def AddCuiLian( arg):
	'''
	增加角色淬炼次数
	@param arg : PyObject*
	@return: PyObject* 
			 line 788 return PyObject_CallObject(ScriptHold::Instance()->m_pyAddCuiLian.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyAddCuiLian.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"AddCuiLian", (PyCFunction)AddCuiLian, METH_VARARGS, "	增加角色淬炼次数	 "}, \
	'''

def ChangeSex( ):
	'''
	改变角色性别
	@return: PyObject* 
			 line 796 return PyObject_CallObject(ScriptHold::Instance()->m_pyChangeSex.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyChangeSex.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ChangeSex", (PyCFunction)ChangeSex, METH_NOARGS, "改变角色性别 "}, \
	'''

def DecBindRMB( arg):
	'''
	减少绑定(魔晶)
	@param arg : PyObject*
	@return: PyObject* 
			 line 813 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecBindRMB", (PyCFunction)DecBindRMB, METH_VARARGS, "减少绑定(魔晶) "}, \
	'''

def DecContribution( arg):
	'''
	减少公会贡献
	@param arg : PyObject*
	@return: PyObject* 
			 line 830 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecContribution", (PyCFunction)DecContribution, METH_VARARGS, "减少公会贡献 "}, \
	'''

def DecDragonSoul( arg):
	'''
	减少龙灵数量
	@param arg : PyObject*
	@return: PyObject* 
			 line 847 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecDragonSoul", (PyCFunction)DecDragonSoul, METH_VARARGS, "减少龙灵数量 "}, \
	'''

def DecGongXun( arg):
	'''
	减少功勋
	@param arg : PyObject*
	@return: PyObject* 
			 line 864 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecGongXun", (PyCFunction)DecGongXun, METH_VARARGS, "减少功勋 "}, \
	'''

def DecKuaFuMoney( arg):
	'''
	减少跨服币
	@param arg : PyObject*
	@return: PyObject* 
			 line 881 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecKuaFuMoney", (PyCFunction)DecKuaFuMoney, METH_VARARGS, "减少跨服币 "}, \
	'''

def DecMoney( arg):
	'''
	减少金钱
	@param arg : PyObject*
	@return: PyObject* 
			 line 898 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecMoney", (PyCFunction)DecMoney, METH_VARARGS, "减少金钱 "}, \
	'''

def DecRMB( arg):
	'''
	减少魔晶和神石
	@param arg : PyObject*
	@return: PyObject* 
			 line 915 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecRMB", (PyCFunction)DecRMB, METH_VARARGS, "减少魔晶和神石 "}, \
	'''

def DecReputation( arg):
	'''
	减少声望
	@param arg : PyObject*
	@return: PyObject* 
			 line 932 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecReputation", (PyCFunction)DecReputation, METH_VARARGS, "减少声望 "}, \
	'''

def DecRongYu( arg):
	'''
	减少荣誉
	@param arg : PyObject*
	@return: PyObject* 
			 line 949 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecRongYu", (PyCFunction)DecRongYu, METH_VARARGS, "减少荣誉 "}, \
	'''

def DecStarLucky( arg):
	'''
	减少星运数量
	@param arg : PyObject*
	@return: PyObject* 
			 line 966 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecStarLucky", (PyCFunction)DecStarLucky, METH_VARARGS, "减少星运数量 "}, \
	'''

def DecUnbindRMB( arg):
	'''
	减少非绑定(神石)
	@param arg : PyObject*
	@return: PyObject* 
			 line 983 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecUnbindRMB", (PyCFunction)DecUnbindRMB, METH_VARARGS, "减少非绑定(神石) "}, \
	'''

def DecUnbindRMB_Q( arg):
	'''
	减少非绑定(充值 神石)
	@param arg : PyObject*
	@return: PyObject* 
			 line 1000 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecUnbindRMB_Q", (PyCFunction)DecUnbindRMB_Q, METH_VARARGS, "减少非绑定(充值 神石) "}, \
	'''

def DecUnbindRMB_S( arg):
	'''
	减少非绑定(系统 神石)
	@param arg : PyObject*
	@return: PyObject* 
			 line 1017 return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"DecUnbindRMB_S", (PyCFunction)DecUnbindRMB_S, METH_VARARGS, "减少非绑定(系统 神石) "}, \
	'''

def GetArtifactCuiLianHoleLevel( ):
	'''
	获取角色神器淬炼光环等级
	@return: PyObject* 
			 line 1025 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetArtifactCuiLianHoleLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetArtifactCuiLianHoleLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetArtifactCuiLianHoleLevel", (PyCFunction)GetArtifactCuiLianHoleLevel, METH_NOARGS, "获取角色神器淬炼光环等级 "}, \
	'''

def GetArtifactMgr( ):
	'''
	获取神器管理器
	@return: PyObject* 
			 line 1033 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetArtifactMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetArtifactMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetArtifactMgr", (PyCFunction)GetArtifactMgr, METH_NOARGS, "获取神器管理器 "}, \
	'''

def GetBindRMB( ):
	'''
	获取绑定(魔晶)
	@return: PyObject* 
			 line 1041 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetBindRMB", (PyCFunction)GetBindRMB, METH_NOARGS, "获取绑定(魔晶) "}, \
	'''

def GetCampID( ):
	'''
	获取阵营ID
	@return: PyObject* 
			 line 1049 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCampID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCampID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetCampID", (PyCFunction)GetCampID, METH_NOARGS, "获取阵营ID "}, \
	'''

def GetColorCode( ):
	'''
	获取主角颜色编码
	@return: PyObject* 
			 line 1057 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetColorCode.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetColorCode.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetColorCode", (PyCFunction)GetColorCode, METH_NOARGS, "获取主角颜色编码 "}, \
	'''

def GetConsumeQPoint( ):
	'''
	获取消费点
	@return: PyObject* 
			 line 1065 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetConsumeQPoint", (PyCFunction)GetConsumeQPoint, METH_NOARGS, "获取消费点 "}, \
	'''

def GetContribution( ):
	'''
	获取公会贡献
	@return: PyObject* 
			 line 1073 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetContribution", (PyCFunction)GetContribution, METH_NOARGS, "获取公会贡献 "}, \
	'''

def GetCuiLian( ):
	'''
	返回角色淬炼次数
	@return: PyObject* 
			 line 1081 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCuiLian.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCuiLian.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetCuiLian", (PyCFunction)GetCuiLian, METH_NOARGS, "	返回角色淬炼次数	 "}, \
	'''

def GetCuiLian_MaxCnt( ):
	'''
	返回角色可以淬炼的最大次数
	@return: PyObject* 
			 line 1089 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCuiLian_MaxCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCuiLian_MaxCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetCuiLian_MaxCnt", (PyCFunction)GetCuiLian_MaxCnt, METH_NOARGS, "	返回角色可以淬炼的最大次数	 "}, \
	'''

def GetDayBuyUnbindRMB_Q( ):
	'''
	获取每日充值神石
	@return: PyObject* 
			 line 1097 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayBuyUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayBuyUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetDayBuyUnbindRMB_Q", (PyCFunction)GetDayBuyUnbindRMB_Q, METH_NOARGS, "获取每日充值神石 "}, \
	'''

def GetDayConsumeUnbindRMB( ):
	'''
	获取每日消费神石，包括充值神石和系统神石
	@return: PyObject* 
			 line 1105 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayConsumeUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayConsumeUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetDayConsumeUnbindRMB", (PyCFunction)GetDayConsumeUnbindRMB, METH_NOARGS, "获取每日消费神石，包括充值神石和系统神石 "}, \
	'''

def GetDayWangZheJiFen( ):
	'''
	返回玩家今日王者公测积分
	@return: PyObject* 
			 line 1113 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayWangZheJiFen.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayWangZheJiFen.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetDayWangZheJiFen", (PyCFunction)GetDayWangZheJiFen, METH_NOARGS, "返回玩家今日王者公测积分 "}, \
	'''

def GetDragonCareerID( ):
	'''
	获取神龙职业ID
	@return: PyObject* 
			 line 1121 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDragonCareerID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDragonCareerID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetDragonCareerID", (PyCFunction)GetDragonCareerID, METH_NOARGS, "获取神龙职业ID "}, \
	'''

def GetDragonSoul( ):
	'''
	获取龙灵数量
	@return: PyObject* 
			 line 1129 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetDragonSoul", (PyCFunction)GetDragonSoul, METH_NOARGS, "获取龙灵数量 "}, \
	'''

def GetEarningExpBuff( ):
	'''
	获取城主经验加成buff
	@return: PyObject* 
			 line 1137 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEarningExpBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEarningExpBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetEarningExpBuff", (PyCFunction)GetEarningExpBuff, METH_NOARGS, "获取城主经验加成buff "}, \
	'''

def GetEarningGoldBuff( ):
	'''
	获取城主金钱加成buff
	@return: PyObject* 
			 line 1145 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEarningGoldBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEarningGoldBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetEarningGoldBuff", (PyCFunction)GetEarningGoldBuff, METH_NOARGS, "获取城主金钱加成buff "}, \
	'''

def GetElementBrandMgr( ):
	'''
	返回元素印记管理器
	@return: PyObject* 
			 line 1153 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetElementBrandMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetElementBrandMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetElementBrandMgr", (PyCFunction)GetElementBrandMgr, METH_NOARGS, "返回元素印记管理器 "}, \
	'''

def GetElementSpiritSkill( ):
	'''
	返回元素之灵技能
	@return: PyObject* 
			 line 1161 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetElementSpiritSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetElementSpiritSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetElementSpiritSkill", (PyCFunction)GetElementSpiritSkill, METH_NOARGS, "返回元素之灵技能 "}, \
	'''

def GetEquipmentMgr( ):
	'''
	获取装备管理器
	@return: PyObject* 
			 line 1169 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEquipmentMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEquipmentMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetEquipmentMgr", (PyCFunction)GetEquipmentMgr, METH_NOARGS, "获取装备管理器 "}, \
	'''

def GetExp( ):
	'''
	获取经验
	@return: PyObject* 
			 line 1177 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetExp", (PyCFunction)GetExp, METH_NOARGS, "获取经验 "}, \
	'''

def GetFTVIP( ):
	'''
	获取繁体VIP
	@return: PyObject* 
			 line 1185 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetFTVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetFTVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetFTVIP", (PyCFunction)GetFTVIP, METH_NOARGS, "获取繁体VIP "}, \
	'''

def GetFightType( ):
	'''
	获取当前临时的战斗类型
	@return: PyObject* 
			 line 1193 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetFightType.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetFightType.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetFightType", (PyCFunction)GetFightType, METH_NOARGS, "获取当前临时的战斗类型 "}, \
	'''

def GetGongXun( ):
	'''
	获取功勋
	@return: PyObject* 
			 line 1201 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetGongXun", (PyCFunction)GetGongXun, METH_NOARGS, "获取功勋 "}, \
	'''

def GetGrade( ):
	'''
	获取进阶
	@return: PyObject* 
			 line 1209 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetGrade.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetGrade.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetGrade", (PyCFunction)GetGrade, METH_NOARGS, "获取进阶 "}, \
	'''

def GetHallowsMgr( ):
	'''
	获取圣器管理器
	@return: PyObject* 
			 line 1217 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHallowsMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHallowsMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetHallowsMgr", (PyCFunction)GetHallowsMgr, METH_NOARGS, "获取圣器管理器 "}, \
	'''

def GetHistoryContribution( ):
	'''
	获取公会历史贡献
	@return: PyObject* 
			 line 1225 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetHistoryContribution", (PyCFunction)GetHistoryContribution, METH_NOARGS, "获取公会历史贡献 "}, \
	'''

def GetJTProcessID( ):
	'''
	获取组队竞技场是的本服进程ID
	@return: PyObject* 
			 line 1233 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTProcessID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTProcessID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetJTProcessID", (PyCFunction)GetJTProcessID, METH_NOARGS, "获取组队竞技场是的本服进程ID "}, \
	'''

def GetJTeamID( ):
	'''
	获取战队id
	@return: PyObject* 
			 line 1241 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTeamID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTeamID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetJTeamID", (PyCFunction)GetJTeamID, METH_NOARGS, "获取战队id "}, \
	'''

def GetJobID( ):
	'''
	获取公会职位ID
	@return: PyObject* 
			 line 1249 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJobID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJobID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetJobID", (PyCFunction)GetJobID, METH_NOARGS, "获取公会职位ID "}, \
	'''

def GetKuaFuMoney( ):
	'''
	获取跨服币
	@return: PyObject* 
			 line 1257 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetKuaFuMoney", (PyCFunction)GetKuaFuMoney, METH_NOARGS, "获取跨服币 "}, \
	'''

def GetLevel( ):
	'''
	获取角色等级
	@return: PyObject* 
			 line 1265 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetLevel", (PyCFunction)GetLevel, METH_NOARGS, "获取角色等级 "}, \
	'''

def GetMFZSkill( ):
	'''
	获取当前携带的魔法阵技能
	@return: PyObject* 
			 line 1273 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMFZSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMFZSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetMFZSkill", (PyCFunction)GetMFZSkill, METH_NOARGS, "	获取当前携带的魔法阵技能 "}, \
	'''

def GetMFZSkillPointDict( ):
	'''
	获取魔法阵技能点字典
	@return: PyObject* 
			 line 1281 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMFZSkillPointDict.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMFZSkillPointDict.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetMFZSkillPointDict", (PyCFunction)GetMFZSkillPointDict, METH_NOARGS, "获取魔法阵技能点字典 "}, \
	'''

def GetMagicSpiritMgr( ):
	'''
	获取魔灵管理器
	@return: PyObject* 
			 line 1289 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMagicSpiritMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMagicSpiritMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetMagicSpiritMgr", (PyCFunction)GetMagicSpiritMgr, METH_NOARGS, "获取魔灵管理器 "}, \
	'''

def GetMoFaZhen( ):
	'''
	返回魔法阵数据
	@return: PyObject* 
			 line 1297 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMoFaZhen.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMoFaZhen.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetMoFaZhen", (PyCFunction)GetMoFaZhen, METH_NOARGS, "返回魔法阵数据 "}, \
	'''

def GetMoney( ):
	'''
	获取金钱
	@return: PyObject* 
			 line 1305 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetMoney", (PyCFunction)GetMoney, METH_NOARGS, "获取金钱 "}, \
	'''

def GetPet( ):
	'''
	获取角色佩戴的宠物
	@return: PyObject* 
			 line 1313 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPet.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPet.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetPet", (PyCFunction)GetPet, METH_NOARGS, "获取角色佩戴的宠物 "}, \
	'''

def GetPortrait( ):
	'''
	获取头像信息(性别
	@return: PyObject* 
			 line 1321 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPortrait.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPortrait.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetPortrait", (PyCFunction)GetPortrait, METH_NOARGS, "获取头像信息(性别, 职业, 进阶) "}, \
	'''

def GetRMB( ):
	'''
	获取魔晶和神石
	@return: PyObject* 
			 line 1329 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetRMB", (PyCFunction)GetRMB, METH_NOARGS, "获取魔晶和神石 "}, \
	'''

def GetReputation( ):
	'''
	获取声望
	@return: PyObject* 
			 line 1337 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetReputation", (PyCFunction)GetReputation, METH_NOARGS, "获取声望 "}, \
	'''

def GetRightMountID( ):
	'''
	获取玩家当前骑乘坐骑ID
	@return: PyObject* 
			 line 1345 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRightMountID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRightMountID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetRightMountID", (PyCFunction)GetRightMountID, METH_NOARGS, "获取玩家当前骑乘坐骑ID "}, \
	'''

def GetRongYu( ):
	'''
	获取荣誉
	@return: PyObject* 
			 line 1353 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetRongYu", (PyCFunction)GetRongYu, METH_NOARGS, "获取荣誉 "}, \
	'''

def GetSex( ):
	'''
	获取角色性别
	@return: PyObject* 
			 line 1361 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetSex.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetSex.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetSex", (PyCFunction)GetSex, METH_NOARGS, "获取角色性别 "}, \
	'''

def GetStar( ):
	'''
	获取主角星级
	@return: PyObject* 
			 line 1369 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStar.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStar.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetStar", (PyCFunction)GetStar, METH_NOARGS, "获取主角星级 "}, \
	'''

def GetStarLucky( ):
	'''
	获取星运数量
	@return: PyObject* 
			 line 1377 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetStarLucky", (PyCFunction)GetStarLucky, METH_NOARGS, "获取星运数量 "}, \
	'''

def GetStationID( ):
	'''
	获取阵位ID
	@return: PyObject* 
			 line 1385 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStationID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStationID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetStationID", (PyCFunction)GetStationID, METH_NOARGS, "获取阵位ID "}, \
	'''

def GetStationSoulSkill( ):
	'''
	返回角色当前阵灵技能
	@return: PyObject* 
			 line 1393 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStationSoulSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStationSoulSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetStationSoulSkill", (PyCFunction)GetStationSoulSkill, METH_NOARGS, "返回角色当前阵灵技能 "}, \
	'''

def GetTalentEmptySize( ):
	'''
	获取天赋卡背包空余格子数
	@return: PyObject* 
			 line 1401 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetTalentEmptySize", (PyCFunction)GetTalentEmptySize, METH_NOARGS, "获取天赋卡背包空余格子数 "}, \
	'''

def GetTalentMgr( ):
	'''
	获取天赋卡管理器
	@return: PyObject* 
			 line 1409 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetTalentMgr", (PyCFunction)GetTalentMgr, METH_NOARGS, "获取天赋卡管理器 "}, \
	'''

def GetTalentZDL( ):
	'''
	获取玩家天赋卡技能战斗力（只有主角）
	@return: PyObject* 
			 line 1417 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetTalentZDL", (PyCFunction)GetTalentZDL, METH_NOARGS, "获取玩家天赋卡技能战斗力（只有主角） "}, \
	'''

def GetUnbindRMB( ):
	'''
	获取非绑定(神石)
	@return: PyObject* 
			 line 1425 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetUnbindRMB", (PyCFunction)GetUnbindRMB, METH_NOARGS, "获取非绑定(神石) "}, \
	'''

def GetUnbindRMB_Q( ):
	'''
	获取非绑定(充值 神石)
	@return: PyObject* 
			 line 1433 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetUnbindRMB_Q", (PyCFunction)GetUnbindRMB_Q, METH_NOARGS, "获取非绑定(充值 神石) "}, \
	'''

def GetUnbindRMB_S( ):
	'''
	获取非绑定(系统 神石)
	@return: PyObject* 
			 line 1441 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetUnbindRMB_S", (PyCFunction)GetUnbindRMB_S, METH_NOARGS, "获取非绑定(系统 神石) "}, \
	'''

def GetUnionID( ):
	'''
	获取公会ID
	@return: PyObject* 
			 line 1449 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnionID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnionID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetUnionID", (PyCFunction)GetUnionID, METH_NOARGS, "获取公会ID "}, \
	'''

def GetVIP( ):
	'''
	获取VIP
	@return: PyObject* 
			 line 1457 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetVIP", (PyCFunction)GetVIP, METH_NOARGS, "获取VIP "}, \
	'''

def GetWeek( ):
	'''
	获取当前周数
	@return: PyObject* 
			 line 1465 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetWeek.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetWeek.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetWeek", (PyCFunction)GetWeek, METH_NOARGS, "获取当前周数 "}, \
	'''

def GetWingID( ):
	'''
	获取翅膀ID
	@return: PyObject* 
			 line 1473 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetWingID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetWingID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetWingID", (PyCFunction)GetWingID, METH_NOARGS, "获取翅膀ID "}, \
	'''

def GetXinYueLevel( ):
	'''
	心悦VIP等级
	@return: PyObject* 
			 line 1481 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetXinYueLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetXinYueLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetXinYueLevel", (PyCFunction)GetXinYueLevel, METH_NOARGS, "心悦VIP等级 "}, \
	'''

def GetZDL( ):
	'''
	获取战斗力
	@return: PyObject* 
			 line 1489 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetZDL", (PyCFunction)GetZDL, METH_NOARGS, "获取战斗力 "}, \
	'''

def GetZhuanShengHaloAddi( ):
	'''
	获取角色转生光环加成
	@return: PyObject* 
			 line 1497 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengHaloAddi.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengHaloAddi.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetZhuanShengHaloAddi", (PyCFunction)GetZhuanShengHaloAddi, METH_NOARGS, "获取角色转生光环加成 "}, \
	'''

def GetZhuanShengHaloLevel( ):
	'''
	获取角色转生光环等级
	@return: PyObject* 
			 line 1505 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengHaloLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengHaloLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetZhuanShengHaloLevel", (PyCFunction)GetZhuanShengHaloLevel, METH_NOARGS, "获取角色转生光环等级 "}, \
	'''

def GetZhuanShengLevel( ):
	'''
	获取角色转生等级
	@return: PyObject* 
			 line 1513 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetZhuanShengLevel", (PyCFunction)GetZhuanShengLevel, METH_NOARGS, "获取角色转生等级 "}, \
	'''

def IncBindRMB( arg):
	'''
	增加绑定(魔晶)
	@param arg : PyObject*
	@return: PyObject* 
			 line 1530 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncBindRMB", (PyCFunction)IncBindRMB, METH_VARARGS, "增加绑定(魔晶) "}, \
	'''

def IncConsumeQPoint( arg):
	'''
	增加消费点
	@param arg : PyObject*
	@return: PyObject* 
			 line 1547 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncConsumeQPoint", (PyCFunction)IncConsumeQPoint, METH_VARARGS, "增加消费点 "}, \
	'''

def IncContribution( arg):
	'''
	增加公会贡献
	@param arg : PyObject*
	@return: PyObject* 
			 line 1564 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncContribution", (PyCFunction)IncContribution, METH_VARARGS, "增加公会贡献 "}, \
	'''

def IncDragonSoul( arg):
	'''
	增加龙灵数量
	@param arg : PyObject*
	@return: PyObject* 
			 line 1581 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncDragonSoul", (PyCFunction)IncDragonSoul, METH_VARARGS, "增加龙灵数量 "}, \
	'''

def IncGongXun( arg):
	'''
	增加功勋
	@param arg : PyObject*
	@return: PyObject* 
			 line 1598 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncGongXun", (PyCFunction)IncGongXun, METH_VARARGS, "增加功勋 "}, \
	'''

def IncHistoryContribution( arg):
	'''
	增加公会历史贡献
	@param arg : PyObject*
	@return: PyObject* 
			 line 1615 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncHistoryContribution", (PyCFunction)IncHistoryContribution, METH_VARARGS, "增加公会历史贡献 "}, \
	'''

def IncKuaFuMoney( arg):
	'''
	增加跨服币
	@param arg : PyObject*
	@return: PyObject* 
			 line 1632 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncKuaFuMoney", (PyCFunction)IncKuaFuMoney, METH_VARARGS, "增加跨服币 "}, \
	'''

def IncLevel( arg):
	'''
	提升角色等级
	@param arg : PyObject*
	@return: PyObject* 
			 line 1649 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncLevel", (PyCFunction)IncLevel, METH_VARARGS, "提升角色等级 "}, \
	'''

def IncMoney( arg):
	'''
	增加金钱
	@param arg : PyObject*
	@return: PyObject* 
			 line 1666 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncMoney", (PyCFunction)IncMoney, METH_VARARGS, "增加金钱 "}, \
	'''

def IncReputation( arg):
	'''
	增加声望
	@param arg : PyObject*
	@return: PyObject* 
			 line 1683 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncReputation", (PyCFunction)IncReputation, METH_VARARGS, "增加声望 "}, \
	'''

def IncRongYu( arg):
	'''
	增加荣誉
	@param arg : PyObject*
	@return: PyObject* 
			 line 1700 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncRongYu", (PyCFunction)IncRongYu, METH_VARARGS, "增加荣誉 "}, \
	'''

def IncStarLucky( arg):
	'''
	增加星运数量
	@param arg : PyObject*
	@return: PyObject* 
			 line 1717 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncStarLucky", (PyCFunction)IncStarLucky, METH_VARARGS, "增加星运数量 "}, \
	'''

def IncTarotHP( arg):
	'''
	增加命力
	@param arg : PyObject*
	@return: PyObject* 
			 line 1734 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncTarotHP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncTarotHP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncTarotHP", (PyCFunction)IncTarotHP, METH_VARARGS, "增加命力 "}, \
	'''

def IncTouchGoldPoint( arg):
	'''
	None
	@param arg : PyObject*
	@return: PyObject* 
			 line 1751 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncTouchGoldPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncTouchGoldPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncTouchGoldPoint", (PyCFunction)IncTouchGoldPoint, METH_VARARGS, "None "}, \
	'''

def IncUnbindRMB_Q( arg):
	'''
	增加非绑定(充值 神石)
	@param arg : PyObject*
	@return: PyObject* 
			 line 1768 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncUnbindRMB_Q", (PyCFunction)IncUnbindRMB_Q, METH_VARARGS, "增加非绑定(充值 神石) "}, \
	'''

def IncUnbindRMB_S( arg):
	'''
	增加非绑定(系统 神石)
	@param arg : PyObject*
	@return: PyObject* 
			 line 1785 return PyObject_CallObject(ScriptHold::Instance()->m_pyIncUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIncUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IncUnbindRMB_S", (PyCFunction)IncUnbindRMB_S, METH_VARARGS, "增加非绑定(系统 神石) "}, \
	'''

def IsKongJianDecennialRole( ):
	'''
	判断玩家登录渠道是否为 空间、朋友网、 QQ游戏大厅、3366、官网
	@return: PyObject* 
			 line 1793 return PyObject_CallObject(ScriptHold::Instance()->m_pyIsKongJianDecennialRole.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIsKongJianDecennialRole.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IsKongJianDecennialRole", (PyCFunction)IsKongJianDecennialRole, METH_NOARGS, "判断玩家登录渠道是否为 空间、朋友网、 QQ游戏大厅、3366、官网 "}, \
	'''

def IsMonthCard( ):
	'''
	是否月卡
	@return: PyObject* 
			 line 1801 return PyObject_CallObject(ScriptHold::Instance()->m_pyIsMonthCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyIsMonthCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"IsMonthCard", (PyCFunction)IsMonthCard, METH_NOARGS, "是否月卡 "}, \
	'''

def SetBindRMB( arg):
	'''
	设置绑定(魔晶)
	@param arg : PyObject*
	@return: PyObject* 
			 line 1818 return PyObject_CallObject(ScriptHold::Instance()->m_pySetBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetBindRMB", (PyCFunction)SetBindRMB, METH_VARARGS, "设置绑定(魔晶) "}, \
	'''

def SetCampID( arg):
	'''
	设置阵营ID
	@param arg : PyObject*
	@return: PyObject* 
			 line 1835 return PyObject_CallObject(ScriptHold::Instance()->m_pySetCampID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetCampID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetCampID", (PyCFunction)SetCampID, METH_VARARGS, "设置阵营ID "}, \
	'''

def SetCanChatTime( arg):
	'''
	设置可发言的时间（解/禁 发言）
	@param arg : PyObject*
	@return: PyObject* 
			 line 1852 return PyObject_CallObject(ScriptHold::Instance()->m_pySetCanChatTime.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetCanChatTime.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetCanChatTime", (PyCFunction)SetCanChatTime, METH_VARARGS, "设置可发言的时间（解/禁 发言） "}, \
	'''

def SetCanLoginTime( arg):
	'''
	设置可登录时间，并且T掉角色（封角色）
	@param arg : PyObject*
	@return: PyObject* 
			 line 1869 return PyObject_CallObject(ScriptHold::Instance()->m_pySetCanLoginTime.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetCanLoginTime.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetCanLoginTime", (PyCFunction)SetCanLoginTime, METH_VARARGS, "设置可登录时间，并且T掉角色（封角色） "}, \
	'''

def SetConsumeQPoint( arg):
	'''
	设置消费点
	@param arg : PyObject*
	@return: PyObject* 
			 line 1886 return PyObject_CallObject(ScriptHold::Instance()->m_pySetConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetConsumeQPoint", (PyCFunction)SetConsumeQPoint, METH_VARARGS, "设置消费点 "}, \
	'''

def SetContribution( arg):
	'''
	设置公会贡献
	@param arg : PyObject*
	@return: PyObject* 
			 line 1903 return PyObject_CallObject(ScriptHold::Instance()->m_pySetContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetContribution", (PyCFunction)SetContribution, METH_VARARGS, "设置公会贡献 "}, \
	'''

def SetDragonCareerID( arg):
	'''
	设置神龙职业ID
	@param arg : PyObject*
	@return: PyObject* 
			 line 1920 return PyObject_CallObject(ScriptHold::Instance()->m_pySetDragonCareerID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetDragonCareerID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetDragonCareerID", (PyCFunction)SetDragonCareerID, METH_VARARGS, "设置神龙职业ID "}, \
	'''

def SetDragonSoul( arg):
	'''
	设置龙灵数量
	@param arg : PyObject*
	@return: PyObject* 
			 line 1937 return PyObject_CallObject(ScriptHold::Instance()->m_pySetDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetDragonSoul", (PyCFunction)SetDragonSoul, METH_VARARGS, "设置龙灵数量 "}, \
	'''

def SetEarningExpBuff( arg):
	'''
	设置城主经验加成buff
	@param arg : PyObject*
	@return: PyObject* 
			 line 1954 return PyObject_CallObject(ScriptHold::Instance()->m_pySetEarningExpBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetEarningExpBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetEarningExpBuff", (PyCFunction)SetEarningExpBuff, METH_VARARGS, "设置城主经验加成buff "}, \
	'''

def SetEarningGoldBuff( arg):
	'''
	设置城主金钱加成buff
	@param arg : PyObject*
	@return: PyObject* 
			 line 1971 return PyObject_CallObject(ScriptHold::Instance()->m_pySetEarningGoldBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetEarningGoldBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetEarningGoldBuff", (PyCFunction)SetEarningGoldBuff, METH_VARARGS, "设置城主金钱加成buff "}, \
	'''

def SetExp( arg):
	'''
	设置经验 （小心使用）
	@param arg : PyObject*
	@return: PyObject* 
			 line 1988 return PyObject_CallObject(ScriptHold::Instance()->m_pySetExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetExp", (PyCFunction)SetExp, METH_VARARGS, "设置经验 （小心使用） "}, \
	'''

def SetFightType( arg):
	'''
	设置当前临时的战斗类型
	@param arg : PyObject*
	@return: PyObject* 
			 line 2005 return PyObject_CallObject(ScriptHold::Instance()->m_pySetFightType.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetFightType.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetFightType", (PyCFunction)SetFightType, METH_VARARGS, "设置当前临时的战斗类型 "}, \
	'''

def SetGongXun( arg):
	'''
	设置功勋
	@param arg : PyObject*
	@return: PyObject* 
			 line 2022 return PyObject_CallObject(ScriptHold::Instance()->m_pySetGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetGongXun", (PyCFunction)SetGongXun, METH_VARARGS, "设置功勋 "}, \
	'''

def SetGrade( arg):
	'''
	设置进阶
	@param arg : PyObject*
	@return: PyObject* 
			 line 2039 return PyObject_CallObject(ScriptHold::Instance()->m_pySetGrade.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetGrade.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetGrade", (PyCFunction)SetGrade, METH_VARARGS, "设置进阶 "}, \
	'''

def SetHistoryContribution( arg):
	'''
	设置公会历史贡献
	@param arg : PyObject*
	@return: PyObject* 
			 line 2056 return PyObject_CallObject(ScriptHold::Instance()->m_pySetHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetHistoryContribution", (PyCFunction)SetHistoryContribution, METH_VARARGS, "设置公会历史贡献 "}, \
	'''

def SetJTeamID( arg):
	'''
	设置战队ID
	@param arg : PyObject*
	@return: PyObject* 
			 line 2073 return PyObject_CallObject(ScriptHold::Instance()->m_pySetJTeamID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetJTeamID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetJTeamID", (PyCFunction)SetJTeamID, METH_VARARGS, "设置战队ID "}, \
	'''

def SetJobID( arg):
	'''
	设置公会职位ID
	@param arg : PyObject*
	@return: PyObject* 
			 line 2090 return PyObject_CallObject(ScriptHold::Instance()->m_pySetJobID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetJobID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetJobID", (PyCFunction)SetJobID, METH_VARARGS, "设置公会职位ID "}, \
	'''

def SetKuaFuMoney( arg):
	'''
	设置跨服币
	@param arg : PyObject*
	@return: PyObject* 
			 line 2107 return PyObject_CallObject(ScriptHold::Instance()->m_pySetKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetKuaFuMoney", (PyCFunction)SetKuaFuMoney, METH_VARARGS, "设置跨服币 "}, \
	'''

def SetMoney( arg):
	'''
	设置金钱
	@param arg : PyObject*
	@return: PyObject* 
			 line 2124 return PyObject_CallObject(ScriptHold::Instance()->m_pySetMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetMoney", (PyCFunction)SetMoney, METH_VARARGS, "设置金钱 "}, \
	'''

def SetReputation( arg):
	'''
	设置声望
	@param arg : PyObject*
	@return: PyObject* 
			 line 2141 return PyObject_CallObject(ScriptHold::Instance()->m_pySetReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetReputation", (PyCFunction)SetReputation, METH_VARARGS, "设置声望 "}, \
	'''

def SetRightMountID( arg):
	'''
	设置玩家当前骑乘坐骑ID
	@param arg : PyObject*
	@return: PyObject* 
			 line 2158 return PyObject_CallObject(ScriptHold::Instance()->m_pySetRightMountID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetRightMountID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetRightMountID", (PyCFunction)SetRightMountID, METH_VARARGS, "设置玩家当前骑乘坐骑ID "}, \
	'''

def SetRongYu( arg):
	'''
	设置荣誉
	@param arg : PyObject*
	@return: PyObject* 
			 line 2175 return PyObject_CallObject(ScriptHold::Instance()->m_pySetRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetRongYu", (PyCFunction)SetRongYu, METH_VARARGS, "设置荣誉 "}, \
	'''

def SetStarLucky( arg):
	'''
	设置星运数量
	@param arg : PyObject*
	@return: PyObject* 
			 line 2192 return PyObject_CallObject(ScriptHold::Instance()->m_pySetStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetStarLucky", (PyCFunction)SetStarLucky, METH_VARARGS, "设置星运数量 "}, \
	'''

def SetStationID( arg):
	'''
	设置阵位ID
	@param arg : PyObject*
	@return: PyObject* 
			 line 2209 return PyObject_CallObject(ScriptHold::Instance()->m_pySetStationID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetStationID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetStationID", (PyCFunction)SetStationID, METH_VARARGS, "设置阵位ID "}, \
	'''

def SetUnbindRMB_Q( arg):
	'''
	设置非绑定(充值 神石)
	@param arg : PyObject*
	@return: PyObject* 
			 line 2226 return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetUnbindRMB_Q", (PyCFunction)SetUnbindRMB_Q, METH_VARARGS, "设置非绑定(充值 神石) "}, \
	'''

def SetUnbindRMB_S( arg):
	'''
	设置非绑定(系统 神石)
	@param arg : PyObject*
	@return: PyObject* 
			 line 2243 return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetUnbindRMB_S", (PyCFunction)SetUnbindRMB_S, METH_VARARGS, "设置非绑定(系统 神石) "}, \
	'''

def SetUnionID( arg):
	'''
	设置公会ID
	@param arg : PyObject*
	@return: PyObject* 
			 line 2260 return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnionID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnionID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetUnionID", (PyCFunction)SetUnionID, METH_VARARGS, "设置公会ID "}, \
	'''

def SetVIP( arg):
	'''
	设置VIP
	@param arg : PyObject*
	@return: PyObject* 
			 line 2277 return PyObject_CallObject(ScriptHold::Instance()->m_pySetVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetVIP", (PyCFunction)SetVIP, METH_VARARGS, "设置VIP "}, \
	'''

def SetWeek( arg):
	'''
	设置当前周数
	@param arg : PyObject*
	@return: PyObject* 
			 line 2294 return PyObject_CallObject(ScriptHold::Instance()->m_pySetWeek.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetWeek.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetWeek", (PyCFunction)SetWeek, METH_VARARGS, "设置当前周数 "}, \
	'''

def SetWingID( arg):
	'''
	设置翅膀ID
	@param arg : PyObject*
	@return: PyObject* 
			 line 2311 return PyObject_CallObject(ScriptHold::Instance()->m_pySetWingID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetWingID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetWingID", (PyCFunction)SetWingID, METH_VARARGS, "设置翅膀ID "}, \
	'''

def SetZDL( arg):
	'''
	设置战斗力
	@param arg : PyObject*
	@return: PyObject* 
			 line 2328 return PyObject_CallObject(ScriptHold::Instance()->m_pySetZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetZDL", (PyCFunction)SetZDL, METH_VARARGS, "设置战斗力 "}, \
	'''

def SetZhuanShengHaloLevel( arg):
	'''
	设置角色转生光环等级
	@param arg : PyObject*
	@return: PyObject* 
			 line 2345 return PyObject_CallObject(ScriptHold::Instance()->m_pySetZhuanShengHaloLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetZhuanShengHaloLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetZhuanShengHaloLevel", (PyCFunction)SetZhuanShengHaloLevel, METH_VARARGS, "设置角色转生光环等级 "}, \
	'''

def SetZhuanShengLevel( arg):
	'''
	设置角色转生等级
	@param arg : PyObject*
	@return: PyObject* 
			 line 2362 return PyObject_CallObject(ScriptHold::Instance()->m_pySetZhuanShengLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySetZhuanShengLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SetZhuanShengLevel", (PyCFunction)SetZhuanShengLevel, METH_VARARGS, "设置角色转生等级 "}, \
	'''

def UpdateAndSyncMFZSkillPassive( ):
	'''
	更新当前魔法阵技能携带状态
	@return: PyObject* 
			 line 2370 return PyObject_CallObject(ScriptHold::Instance()->m_pyUpdateAndSyncMFZSkillPassive.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyUpdateAndSyncMFZSkillPassive.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"UpdateAndSyncMFZSkillPassive", (PyCFunction)UpdateAndSyncMFZSkillPassive, METH_NOARGS, "更新当前魔法阵技能携带状态 "}, \
	'''

def CreateHeroProperty( arg):
	'''
	创建一个英雄属性集合
	@param arg : PyObject*
	@return: PyObject* 
			 line 2387 return PyObject_CallObject(ScriptHold::Instance()->m_pyCreateHeroProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyCreateHeroProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"CreateHeroProperty", (PyCFunction)CreateHeroProperty, METH_VARARGS, "创建一个英雄属性集合 "}, \
	'''

def GetPropertyGather( ):
	'''
	获取主角属性集合
	@return: PyObject* 
			 line 2395 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPropertyGather.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPropertyGather.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetPropertyGather", (PyCFunction)GetPropertyGather, METH_NOARGS, "获取主角属性集合 "}, \
	'''

def GetPropertyMgr( ):
	'''
	获取角色属性管理器
	@return: PyObject* 
			 line 2403 return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPropertyMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPropertyMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"GetPropertyMgr", (PyCFunction)GetPropertyMgr, METH_NOARGS, "获取角色属性管理器 "}, \
	'''

def PropertyIsValid( ):
	'''
	属性是否已经生效了
	@return: PyObject* 
			 line 2411 return PyObject_CallObject(ScriptHold::Instance()->m_pyPropertyIsValid.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyPropertyIsValid.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"PropertyIsValid", (PyCFunction)PropertyIsValid, METH_NOARGS, "属性是否已经生效了 "}, \
	'''

def RemoveHeroProperty( arg):
	'''
	移除一个英雄的属性集合
	@param arg : PyObject*
	@return: PyObject* 
			 line 2428 return PyObject_CallObject(ScriptHold::Instance()->m_pyRemoveHeroProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: if (!PyTuple_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
	@warning: tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyRemoveHeroProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"RemoveHeroProperty", (PyCFunction)RemoveHeroProperty, METH_VARARGS, "移除一个英雄的属性集合 "}, \
	'''

def ResetAllTarotProperty( ):
	'''
	设置所有的占卜属性重算(特殊)
	@return: PyObject* 
			 line 2436 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetAllTarotProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetAllTarotProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetAllTarotProperty", (PyCFunction)ResetAllTarotProperty, METH_NOARGS, "设置所有的占卜属性重算(特殊) "}, \
	'''

def ResetElementBrandBaseProperty( ):
	'''
	设置元素印记基本属性重算
	@return: PyObject* 
			 line 2444 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetElementBrandBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetElementBrandBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetElementBrandBaseProperty", (PyCFunction)ResetElementBrandBaseProperty, METH_NOARGS, "设置元素印记基本属性重算 "}, \
	'''

def ResetElementSpiritProperty( ):
	'''
	设置元素之灵属性重算
	@return: PyObject* 
			 line 2452 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetElementSpiritProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetElementSpiritProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetElementSpiritProperty", (PyCFunction)ResetElementSpiritProperty, METH_NOARGS, "设置元素之灵属性重算 "}, \
	'''

def ResetGlobalCardAtlasProperty( ):
	'''
	重算卡牌图鉴属性
	@return: PyObject* 
			 line 2460 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalCardAtlasProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalCardAtlasProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalCardAtlasProperty", (PyCFunction)ResetGlobalCardAtlasProperty, METH_NOARGS, "重算卡牌图鉴属性 "}, \
	'''

def ResetGlobalDragonProperty( ):
	'''
	设置全局神龙属性重算
	@return: PyObject* 
			 line 2468 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalDragonProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalDragonProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalDragonProperty", (PyCFunction)ResetGlobalDragonProperty, METH_NOARGS, "设置全局神龙属性重算 "}, \
	'''

def ResetGlobalFashionProperty( ):
	'''
	设置全局时装鉴定属性重算
	@return: PyObject* 
			 line 2476 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalFashionProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalFashionProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalFashionProperty", (PyCFunction)ResetGlobalFashionProperty, METH_NOARGS, "设置全局时装鉴定属性重算 "}, \
	'''

def ResetGlobalHelpStationProperty( ):
	'''
	设置全局助阵属性重算
	@return: PyObject* 
			 line 2484 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalHelpStationProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalHelpStationProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalHelpStationProperty", (PyCFunction)ResetGlobalHelpStationProperty, METH_NOARGS, "设置全局助阵属性重算 "}, \
	'''

def ResetGlobalMountAppProperty( ):
	'''
	设置全局坐骑外形品质属性重算
	@return: PyObject* 
			 line 2492 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalMountAppProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalMountAppProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalMountAppProperty", (PyCFunction)ResetGlobalMountAppProperty, METH_NOARGS, "设置全局坐骑外形品质属性重算 "}, \
	'''

def ResetGlobalMountProperty( ):
	'''
	设置全局坐骑属性重算
	@return: PyObject* 
			 line 2500 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalMountProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalMountProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalMountProperty", (PyCFunction)ResetGlobalMountProperty, METH_NOARGS, "设置全局坐骑属性重算 "}, \
	'''

def ResetGlobalQinmiGradeProperty( ):
	'''
	设置全局亲密品阶属性重算
	@return: PyObject* 
			 line 2508 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalQinmiGradeProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalQinmiGradeProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalQinmiGradeProperty", (PyCFunction)ResetGlobalQinmiGradeProperty, METH_NOARGS, "设置全局亲密品阶属性重算 "}, \
	'''

def ResetGlobalQinmiProperty( ):
	'''
	设置全局亲密等级属性重算
	@return: PyObject* 
			 line 2516 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalQinmiProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalQinmiProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalQinmiProperty", (PyCFunction)ResetGlobalQinmiProperty, METH_NOARGS, "设置全局亲密等级属性重算 "}, \
	'''

def ResetGlobalStationSoulItemProperty( ):
	'''
	设置重算阵灵强化石属性
	@return: PyObject* 
			 line 2524 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalStationSoulItemProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalStationSoulItemProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalStationSoulItemProperty", (PyCFunction)ResetGlobalStationSoulItemProperty, METH_NOARGS, "设置重算阵灵强化石属性 "}, \
	'''

def ResetGlobalWStationBaseProperty( ):
	'''
	重算战阵基础属性
	@return: PyObject* 
			 line 2532 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalWStationBaseProperty", (PyCFunction)ResetGlobalWStationBaseProperty, METH_NOARGS, "重算战阵基础属性 "}, \
	'''

def ResetGlobalWStationItemProperty( ):
	'''
	重算战阵战魂石属性
	@return: PyObject* 
			 line 2540 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationItemProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationItemProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalWStationItemProperty", (PyCFunction)ResetGlobalWStationItemProperty, METH_NOARGS, "重算战阵战魂石属性 "}, \
	'''

def ResetGlobalWStationThousandProperty( ):
	'''
	重算战阵万分比属性
	@return: PyObject* 
			 line 2548 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationThousandProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationThousandProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalWStationThousandProperty", (PyCFunction)ResetGlobalWStationThousandProperty, METH_NOARGS, "重算战阵万分比属性 "}, \
	'''

def ResetGlobalWeddingRingProperty( ):
	'''
	设置全局婚戒属性重算
	@return: PyObject* 
			 line 2556 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalWeddingRingProperty", (PyCFunction)ResetGlobalWeddingRingProperty, METH_NOARGS, "设置全局婚戒属性重算 "}, \
	'''

def ResetGlobalWeddingRingSProperty( ):
	'''
	设置全局婚戒戒灵属性重算
	@return: PyObject* 
			 line 2564 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingSProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingSProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalWeddingRingSProperty", (PyCFunction)ResetGlobalWeddingRingSProperty, METH_NOARGS, "设置全局婚戒戒灵属性重算 "}, \
	'''

def ResetGlobalWeddingRingSkillProperty( ):
	'''
	设置全局夫妻技能属性重算
	@return: PyObject* 
			 line 2572 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingSkillProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingSkillProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalWeddingRingSkillProperty", (PyCFunction)ResetGlobalWeddingRingSkillProperty, METH_NOARGS, "设置全局夫妻技能属性重算 "}, \
	'''

def ResetGlobalWingProperty( ):
	'''
	设置全局翅膀属性重算
	@return: PyObject* 
			 line 2580 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalWingProperty", (PyCFunction)ResetGlobalWingProperty, METH_NOARGS, "设置全局翅膀属性重算 "}, \
	'''

def ResetGlobalZhuanShengHaloBaseProperty( ):
	'''
	重算转身光环基础 属性
	@return: PyObject* 
			 line 2588 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalZhuanShengHaloBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalZhuanShengHaloBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetGlobalZhuanShengHaloBaseProperty", (PyCFunction)ResetGlobalZhuanShengHaloBaseProperty, METH_NOARGS, "重算转身光环基础 属性 "}, \
	'''

def ResetMarryRingProperty( ):
	'''
	设置订婚戒指属性重算
	@return: PyObject* 
			 line 2596 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetMarryRingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetMarryRingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetMarryRingProperty", (PyCFunction)ResetMarryRingProperty, METH_NOARGS, "设置订婚戒指属性重算 "}, \
	'''

def ResetSealProperty( ):
	'''
	设置圣印属性重算
	@return: PyObject* 
			 line 2604 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetSealProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetSealProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetSealProperty", (PyCFunction)ResetSealProperty, METH_NOARGS, "设置圣印属性重算 "}, \
	'''

def ResetStationSoulProperty( ):
	'''
	设置阵灵属性重算
	@return: PyObject* 
			 line 2612 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetStationSoulProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetStationSoulProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetStationSoulProperty", (PyCFunction)ResetStationSoulProperty, METH_NOARGS, "设置阵灵属性重算 "}, \
	'''

def ResetTitleProperty( ):
	'''
	设置称号属性重算
	@return: PyObject* 
			 line 2620 return PyObject_CallObject(ScriptHold::Instance()->m_pyResetTitleProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pyResetTitleProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"ResetTitleProperty", (PyCFunction)ResetTitleProperty, METH_NOARGS, "设置称号属性重算 "}, \
	'''

def SyncAllProperty( ):
	'''
	同步所有的属性
	@return: PyObject* 
			 line 2628 return PyObject_CallObject(ScriptHold::Instance()->m_pySyncAllProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@warning: return PyObject_CallObject(ScriptHold::Instance()->m_pySyncAllProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	@see : {"SyncAllProperty", (PyCFunction)SyncAllProperty, METH_NOARGS, "同步所有的属性 "}, \
	'''

# 有35个Py函数定义

def SetCareer( nValue):
	'''
	设置角色职业
	@param nValue : I32
	@return: None 
			 line 17 Py_RETURN_NONE;
	@see : {"SetCareer", (PyCFunction)SetCareer, METH_O, "设置角色职业   "},	\
	'''

def GetCareer( ):
	'''
	获取角色职业
	@return: I32 
			 line 23 return GEPython::PyObjFromI32(self->cptr->GetCareer());
	@see : {"GetCareer", (PyCFunction)GetCareer, METH_NOARGS, "获取角色职业   "},	\
	'''

def SetFly( uValue):
	'''
	设置角色飞行状态走路状态
	@param uValue : UI8
	@return: None 
			 line 36 Py_RETURN_NONE;
	@see : {"SetFly", (PyCFunction)SetFly, METH_O, "设置角色飞行状态走路状态   "},	\
	'''

def IsFlying( ):
	'''
	获取角色飞行允许状态走路状态
	@see : {"IsFlying", (PyCFunction)IsFlying, METH_NOARGS, "获取角色飞行允许状态走路状态   "},	\
	'''

def IncTiLi( nValue):
	'''
	增加体力
	@param nValue : UI16
	@return: None 
			 line 55 Py_RETURN_NONE;
	@see : {"IncTiLi", (PyCFunction)IncTiLi, METH_O, "增加体力   "},	\
	'''

def DecTiLi( nValue):
	'''
	减少体力
	@param nValue : UI16
	@return: None 
			 line 68 Py_RETURN_NONE;
	@see : {"DecTiLi", (PyCFunction)DecTiLi, METH_O, "减少体力   "},	\
	'''

def SetTiLi( nValue):
	'''
	设置体力
	@param nValue : UI16
	@return: None 
			 line 81 Py_RETURN_NONE;
	@see : {"SetTiLi", (PyCFunction)SetTiLi, METH_O, "设置体力   "},	\
	'''

def GetTiLi( ):
	'''
	获取体力
	@return: I32 
			 line 87 return GEPython::PyObjFromI32(self->cptr->GetTiLi());
	@see : {"GetTiLi", (PyCFunction)GetTiLi, METH_NOARGS, "获取体力   "},	\
	'''

def GetNowSpeed( ):
	'''
	获取当前移动速度
	@return: I32 
			 line 93 return GEPython::PyObjFromI32(self->cptr->GetNowSpeed());
	@see : {"GetNowSpeed", (PyCFunction)GetNowSpeed, METH_NOARGS, "获取当前移动速度   "},	\
	'''

def SetMoveSpeed( nValue):
	'''
	设置移动速度
	@param nValue : UI16
	@return: None 
			 line 107 Py_RETURN_NONE;
	@see : {"SetMoveSpeed", (PyCFunction)SetMoveSpeed, METH_O, "设置移动速度   "},	\
	'''

def GetMoveSpeed( ):
	'''
	获取移动速度
	@return: I32 
			 line 113 return GEPython::PyObjFromI32(self->cptr->GetMoveSpeed());
	@see : {"GetMoveSpeed", (PyCFunction)GetMoveSpeed, METH_NOARGS, "获取移动速度   "},	\
	'''

def SetMountSpeed( nValue):
	'''
	设置坐骑移动速度
	@param nValue : UI16
	@return: None 
			 line 126 Py_RETURN_NONE;
	@see : {"SetMountSpeed", (PyCFunction)SetMountSpeed, METH_O, "设置坐骑移动速度   "},	\
	'''

def GetMountSpeed( ):
	'''
	获取坐骑移动速度
	@return: I32 
			 line 132 return GEPython::PyObjFromI32(self->cptr->GetMountSpeed());
	@see : {"GetMountSpeed", (PyCFunction)GetMountSpeed, METH_NOARGS, "获取坐骑移动速度   "},	\
	'''

def SetTempSpeed( nValue):
	'''
	设置临时移动速度
	@param nValue : UI16
	@return: None 
			 line 147 Py_RETURN_NONE;
	@see : {"SetTempSpeed", (PyCFunction)SetTempSpeed, METH_O, "设置临时移动速度   "},	\
	'''

def GetTempSpeed( ):
	'''
	获取临时移动速度
	@return: I32 
			 line 153 return GEPython::PyObjFromI32(self->cptr->GetTempSpeed());
	@see : {"GetTempSpeed", (PyCFunction)GetTempSpeed, METH_NOARGS, "获取临时移动速度   "},	\
	'''

def CancleTempSpeed( ):
	'''
	取消临时移动速度
	@return: None 
			 line 160 Py_RETURN_NONE;
	@see : {"CancleTempSpeed", (PyCFunction)CancleTempSpeed, METH_NOARGS, "取消临时移动速度   "},	\
	'''

def GetTempFly( ):
	'''
	获取临时飞行状态
	@return: I32 
			 line 166 return GEPython::PyObjFromI32(self->cptr->GetTempFly());
	@see : {"GetTempFly", (PyCFunction)GetTempFly, METH_NOARGS, "获取临时飞行状态   "},	\
	'''

def SetTempFly( nValue):
	'''
	设置临时移动速度
	@param nValue : UI16
	@return: None 
			 line 179 Py_RETURN_NONE;
	@see : {"SetTempFly", (PyCFunction)SetTempFly, METH_O, "设置临时移动速度   "},	\
	'''

def CancleTempFly( ):
	'''
	取消临时飞行
	@return: None 
			 line 187 Py_RETURN_NONE;
	@see : {"CancleTempFly", (PyCFunction)CancleTempFly, METH_NOARGS, "取消临时飞行   "},	\
	'''

def SetAppStatus( uValue):
	'''
	设置角色外观状态
	@param uValue : UI16
	@return: None 
			 line 202 Py_RETURN_NONE;
	@see : {"SetAppStatus", (PyCFunction)SetAppStatus, METH_O, "设置角色外观状态   "},	\
	'''

def GetAppStatus( ):
	'''
	获取角色外观状态
	@return: I64 
			 line 208 return GEPython::PyObjFromI64(self->cptr->GetTI64(RoleDataMgr::Instance()->uRoleAppStatusIndex));
	@see : {"GetAppStatus", (PyCFunction)GetAppStatus, METH_NOARGS, "获取角色外观状态   "},	\
	'''

def MustFlying( ):
	'''
	当前所在点是否必须飞行才可以移动
	@see : {"MustFlying", (PyCFunction)MustFlying, METH_NOARGS, "当前所在点是否必须飞行才可以移动   "},	\
	'''

def GetRoleSyncAppearanceObj( ):
	'''
	获取角色的外观打包数据
	@return: PyObject* 
			 line 220 return self->cptr->GetRoleSyncAppearanceObj();
	@warning: return self->cptr->GetRoleSyncAppearanceObj();
	@see : {"GetRoleSyncAppearanceObj", (PyCFunction)GetRoleSyncAppearanceObj, METH_NOARGS, "获取角色的外观打包数据   "},	\
	'''

def SetQQHZ( uValue):
	'''
	设置黄钻等级
	@param uValue : UI16
	@return: None 
			 line 235 Py_RETURN_NONE;
	@return: None 
			 line 240 Py_RETURN_NONE;
	@see : {"SetQQHZ", (PyCFunction)SetQQHZ, METH_O, "设置黄钻等级   "},	\
	'''

def GetQQHZ( ):
	'''
	获取黄钻等级
	@return: I32 
			 line 247 return GEPython::PyObjFromI32(tempHZ.I16_0());
	@see : {"GetQQHZ", (PyCFunction)GetQQHZ, METH_NOARGS, "获取黄钻等级   "},	\
	'''

def SetQQYHZ( uValue):
	'''
	设置年费黄钻
	@param uValue : UI8
	@return: None 
			 line 262 Py_RETURN_NONE;
	@return: None 
			 line 267 Py_RETURN_NONE;
	@see : {"SetQQYHZ", (PyCFunction)SetQQYHZ, METH_O, "设置年费黄钻   "},	\
	'''

def GetQQYHZ( ):
	'''
	获取年费黄钻
	@return: I32 
			 line 274 return GEPython::PyObjFromI32(tempHZ.UI8_2());
	@see : {"GetQQYHZ", (PyCFunction)GetQQYHZ, METH_NOARGS, "获取年费黄钻   "},	\
	'''

def SetQQHHHZ( uValue):
	'''
	设置豪华黄钻
	@param uValue : UI8
	@return: None 
			 line 290 Py_RETURN_NONE;
	@return: None 
			 line 295 Py_RETURN_NONE;
	@see : {"SetQQHHHZ", (PyCFunction)SetQQHHHZ, METH_O, "设置豪华黄钻   "},	\
	'''

def GetQQHHHZ( ):
	'''
	获取豪华黄钻
	@return: I32 
			 line 302 return GEPython::PyObjFromI32(tempHZ.UI8_3());
	@see : {"GetQQHHHZ", (PyCFunction)GetQQHHHZ, METH_NOARGS, "获取豪华黄钻   "},	\
	'''

def SetQQLZ( uValue):
	'''
	设置蓝钻等级
	@param uValue : UI16
	@return: None 
			 line 318 Py_RETURN_NONE;
	@return: None 
			 line 323 Py_RETURN_NONE;
	@see : {"SetQQLZ", (PyCFunction)SetQQLZ, METH_O, "设置蓝钻等级   "},	\
	'''

def GetQQLZ( ):
	'''
	获取蓝钻等级
	@return: I32 
			 line 330 return GEPython::PyObjFromI32(tempHZ.I16_0());
	@see : {"GetQQLZ", (PyCFunction)GetQQLZ, METH_NOARGS, "获取蓝钻等级   "},	\
	'''

def SetQQYLZ( uValue):
	'''
	设置年费蓝钻
	@param uValue : UI8
	@return: None 
			 line 345 Py_RETURN_NONE;
	@return: None 
			 line 350 Py_RETURN_NONE;
	@see : {"SetQQYLZ", (PyCFunction)SetQQYLZ, METH_O, "设置年费蓝钻   "},	\
	'''

def GetQQYLZ( ):
	'''
	获取年费蓝钻
	@return: I32 
			 line 357 return GEPython::PyObjFromI32(tempHZ.UI8_2());
	@see : {"GetQQYLZ", (PyCFunction)GetQQYLZ, METH_NOARGS, "获取年费蓝钻   "},	\
	'''

def SetQQHHLZ( uValue):
	'''
	设置豪华蓝钻
	@param uValue : UI8
	@return: None 
			 line 373 Py_RETURN_NONE;
	@return: None 
			 line 378 Py_RETURN_NONE;
	@see : {"SetQQHHLZ", (PyCFunction)SetQQHHLZ, METH_O, "设置豪华蓝钻   "},	\
	'''

def GetQQHHLZ( ):
	'''
	获取豪华蓝钻
	@return: I32 
			 line 385 return GEPython::PyObjFromI32(tempHZ.UI8_3());
	@see : {"GetQQHHLZ", (PyCFunction)GetQQHHLZ, METH_NOARGS, "获取豪华蓝钻   "},	\
	'''

#automatic_end
def _AddItem(p1, p2):
	pass


AddItem = _AddItem