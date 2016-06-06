#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有10个Py函数定义

def GetNPCID( ):
	'''
	NPCID
	@return: UI32 
			 line 17 return GEPython::PyObjFromUI32(self->cptr->GetNPCID());
	@see : {"GetNPCID", (PyCFunction)GetNPCID, METH_NOARGS, "NPCID  "},
	'''

def GetNPCName( ):
	'''
	NPC名字
	@return: String 
			 line 23 return PyString_FromString(self->cptr->GetNPCName().c_str());
	@see : {"GetNPCName", (PyCFunction)GetNPCName, METH_NOARGS, "NPC名字  "},
	'''

def GetNPCType( ):
	'''
	获取NPC类型
	@return: UI32 
			 line 30 return GEPython::PyObjFromUI32(self->cptr->GetNPCType());
	@see : {"GetNPCType", (PyCFunction)GetNPCType, METH_NOARGS, "获取NPC类型  "},
	'''

def GetPos( ):
	'''
	获取NPC坐标
	@return: UI16,UI16 
			 line 37 return Py_BuildValue("HH", self->cptr->GetPosX(), self->cptr->GetPosY());
	@see : {"GetPos", (PyCFunction)GetPos, METH_NOARGS, "获取NPC坐标  "},
	'''

def SetPyDict( pyKey, pyValue):
	'''
	设置NPCpython字典
	@param pyKey : PyObject*
	@param pyValue : PyObject*
	@return: None 
			 line 50 Py_RETURN_NONE;
	@see : {"SetPyDict", (PyCFunction)SetPyDict, METH_VARARGS, "设置NPCpython字典  "},
	'''

def GetPyDict( ):
	'''
	获取NPCpython字典
	@return: PyObject* 
			 line 56 return self->cptr->GetPyDict();
	@warning: return self->cptr->GetPyDict();
	@see : {"GetPyDict", (PyCFunction)GetPyDict, METH_NOARGS, "获取NPCpython字典  "},
	'''

def SetPySyncDict( pyKey, pyValue):
	'''
	设置NPCpython同步客户端的字典
	@param pyKey : PyObject*
	@param pyValue : PyObject*
	@return: None 
			 line 69 Py_RETURN_NONE;
	@see : {"SetPySyncDict", (PyCFunction)SetPySyncDict, METH_VARARGS, "设置NPCpython同步客户端的字典  "},
	'''

def GetPySyncDict( ):
	'''
	获取NPCpython同步客户端的字典
	@return: PyObject* 
			 line 75 return self->cptr->GetPySyncDict();
	@warning: return self->cptr->GetPySyncDict();
	@see : {"GetPySyncDict", (PyCFunction)GetPySyncDict, METH_NOARGS, "获取NPCpython同步客户端的字典  "},
	'''

def AfterChange( ):
	'''
	NPC发生了改变，再次同步周围的客户端
	@return: None 
			 line 82 Py_RETURN_NONE;
	@see : {"AfterChange", (PyCFunction)AfterChange, METH_NOARGS, "NPC发生了改变，再次同步周围的客户端  "},
	'''

def Destroy( ):
	'''
	NPC删除接口
	@return: None 
			 line 89 Py_RETURN_NONE;
	@see : {"Destroy", (PyCFunction)Destroy, METH_NOARGS, "NPC删除接口  "},
	'''

#automatic_end
