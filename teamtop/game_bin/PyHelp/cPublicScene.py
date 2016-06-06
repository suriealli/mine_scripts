#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有19个Py函数定义

def GetSceneID( ):
	'''
	场景ID
	@return: UI32 
			 line 17 return GEPython::PyObjFromUI32(self->cptr->GetSceneID());
	@see : {"GetSceneID", (PyCFunction)GetSceneID, METH_NOARGS, "场景ID  "},
	'''

def GetSceneName( ):
	'''
	场景名字
	@return: String 
			 line 23 return PyString_FromString(self->cptr->SceneName().c_str());
	@see : {"GetSceneName", (PyCFunction)GetSceneName, METH_NOARGS, "场景名字  "},
	'''

def GetSceneType( ):
	'''
	场景类型
	@return: UI32 
			 line 30 return GEPython::PyObjFromUI32(self->cptr->GetSceneType());
	@see : {"GetSceneType", (PyCFunction)GetSceneType, METH_NOARGS, "场景类型  "},
	'''

def CanSeeOther( ):
	'''
	设置可以看到其他玩家
	@return: None 
			 line 38 Py_RETURN_NONE;
	@see : {"CanSeeOther", (PyCFunction)CanSeeOther, METH_NOARGS, "设置可以看到其他玩家  "},
	'''

def CannotSeeOther( ):
	'''
	设置看不到其他玩家
	@return: None 
			 line 45 Py_RETURN_NONE;
	@see : {"CannotSeeOther", (PyCFunction)CannotSeeOther, METH_NOARGS, "设置看不到其他玩家  "},
	'''

def SetMoveTimeJap( ujap):
	'''
	设置移动时间忽视参数
	@param ujap : UI16
	@return: None 
			 line 57 Py_RETURN_NONE;
	@see : {"SetMoveTimeJap", (PyCFunction)SetMoveTimeJap, METH_O, "设置移动时间忽视参数  " },
	'''

def SetMoveDistanceJap( ujap):
	'''
	设置移动距离忽视参数
	@param ujap : UI16
	@return: None 
			 line 69 Py_RETURN_NONE;
	@see : {"SetMoveDistanceJap", (PyCFunction)SetMoveDistanceJap, METH_O, "设置移动距离忽视参数  " },
	'''

def JoinRole( pyObj, uX, uY):
	'''
	玩家进入场景
	@param pyObj : PyObject*
	@param uX : UI16
	@param uY : UI16
	@see : {"JoinRole", (PyCFunction)JoinRole, METH_VARARGS, "玩家进入场景  "},
	'''

def LeaveRole( arg):
	'''
	玩家离开场景
	@param arg : PyObject*
	@return: None 
			 line 109 Py_RETURN_NONE;
	@warning: ServerPython::PyRoleObject *pPyRole = ServerPython::PyRole_FromObj(arg);
	@see : {"LeaveRole", (PyCFunction)LeaveRole, METH_O, "玩家离开场景  "},
	'''

def RestoreRole( arg):
	'''
	玩家重登录同步消息恢复场景信息
	@param arg : PyObject*
	@return: None 
			 line 125 Py_RETURN_NONE;
	@warning: ServerPython::PyRoleObject *pPyRole = ServerPython::PyRole_FromObj(arg);
	@see : {"RestoreRole", (PyCFunction)RestoreRole, METH_O, "玩家重登录同步消息恢复场景信息  "},
	'''

def GetAllRole( ):
	'''
	当前场景玩家
	@return: PyObject* 
			 line 147 return lis.GetList_NewRef();
	@warning: return lis.GetList_NewRef();
	@see : {"GetAllRole", (PyCFunction)GetAllRole, METH_NOARGS, "当前场景玩家  "},
	'''

def SearchRole( uRoleID):
	'''
	在场景中查找玩家
	@param uRoleID : UI64
	@return: None 
			 line 162 Py_RETURN_NONE;
	@return: PyObject* 
			 line 164 return pRole->GetPySelf().GetObj_NewRef();
	@warning: return pRole->GetPySelf().GetObj_NewRef();
	@see : {"SearchRole", (PyCFunction)SearchRole, METH_O, "在场景中查找玩家  "},
	'''

def CreateNPC( uTypeID, uX, uY, uDirection=None , uBroadCast=None , pObj=None ):
	'''
	在场景中创建NPC
	@param uTypeID : UI16
	@param uX : UI16
	@param uY : UI16
	@param uDirection : UI8
	@param uBroadCast : UI8
	@param pObj : PyObject*
	@return: None 
			 line 190 Py_RETURN_NONE;
	@return: PyObject* 
			 line 192 return pNPC->GetPySelf().GetObj_NewRef();
	@warning: return pNPC->GetPySelf().GetObj_NewRef();
	@see : {"CreateNPC", (PyCFunction)CreateNPC, METH_VARARGS, "在场景中创建NPC  "},
	'''

def DestroyNPC( uGlobalID):
	'''
	在场景中销毁NPC
	@param uGlobalID : UI32
	@return: None 
			 line 205 Py_RETURN_NONE;
	@see : {"DestroyNPC", (PyCFunction)DestroyNPC, METH_O, "在场景中销毁NPC  "},
	'''

def SearchNPC( uNPCID):
	'''
	在场景中查找一个NPC
	@param uNPCID : UI32
	@return: None 
			 line 220 Py_RETURN_NONE;
	@return: PyObject* 
			 line 224 return pNPC->GetPySelf().GetObj_NewRef();
	@warning: return pNPC->GetPySelf().GetObj_NewRef();
	@see : {"SearchNPC", (PyCFunction)SearchNPC, METH_O, "在场景中查找一个NPC  "},
	'''

def GetAllNPC( ):
	'''
	获取当前场景的所以服务器创建的NPC
	@return: PyObject* 
			 line 239 return lis.GetList_NewRef();
	@warning: return lis.GetList_NewRef();
	@see : {"GetAllNPC", (PyCFunction)GetAllNPC, METH_NOARGS, "获取当前场景的所以服务器创建的NPC  "},
	'''

def BroadMsg( ):
	'''
	广播消息给该场景内所有角色
	@return: None 
			 line 247 Py_RETURN_NONE;
	@see : {"BroadMsg", (PyCFunction)BroadMsg, METH_VARARGS, "广播消息给该场景内所有角色  "},
	'''

def RectBroadMsg( arg):
	'''
	广播消息给区域内所有角色
	@param arg : PyObject*
	@return: None 
			 line 263 Py_RETURN_NONE;
	@warning: ServerPython::PyRoleObject *pPyRole = ServerPython::PyRole_FromObj(arg);
	@see : {"RectBroadMsg", (PyCFunction)RectBroadMsg, METH_O, "广播消息给区域内所有角色  "},
	'''

def Msg( msg_b8_UI32_1, msg_b8_UI32_0, pObj):
	'''
	广播消息给该场景内所有角色
	@param msg_b8_UI32_1 : I32
	@param msg_b8_UI32_0 : I32
	@param pObj : PyObject*
	@return: None 
			 line 279 Py_RETURN_NONE;
	@see : {"Msg", (PyCFunction)Msg, METH_VARARGS, "广播消息给该场景内所有角色  " },
	'''

#automatic_end
