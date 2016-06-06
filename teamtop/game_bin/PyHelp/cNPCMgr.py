#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有6个Py函数定义

def CreateNPCTemplate( uType, name, uLen, uClickType, uIsMovingNPC):
	'''
	创建一个NPC模板
	@param uType : UI16
	@param name : string
	@param uLen : UI16
	@param uClickType : UI8
	@param uIsMovingNPC : UI8
	@return: None 
			 line 23 Py_RETURN_NONE;
	@see : { "CreateNPCTemplate", CreateNPCTemplate, METH_VARARGS, "创建一个NPC模板  "},
	'''

def SearchNPC( uNPCID):
	'''
	搜索一个NPC
	@param uNPCID : UI32
	@return: None 
			 line 37 Py_RETURN_NONE;
	@return: PyObject* 
			 line 41 return pNPC->GetPySelf().GetObj_NewRef();
	@warning: return pNPC->GetPySelf().GetObj_NewRef();
	@see : { "SearchNPC", SearchNPC, METH_O, "搜索一个NPC  "},
	'''

def CreateNPCConfigObj( uID, uSceneID, uType, uX, uY):
	'''
	创建一个NPC模板
	@param uID : UI32
	@param uSceneID : UI32
	@param uType : UI16
	@param uX : UI16
	@param uY : UI16
	@return: None 
			 line 59 Py_RETURN_NONE;
	@see : { "CreateNPCConfigObj", CreateNPCConfigObj, METH_VARARGS, "创建一个NPC模板  "},
	'''

def AllotGlobalID( ):
	'''
	分配一个ID
	@return: UI32 
			 line 64 return GEPython::PyObjFromUI32(NPCMgr::Instance()->AllotGlobalID());
	@see : { "AllotGlobalID", AllotGlobalID, METH_NOARGS, "分配一个ID  "},
	'''

def LoadNPCClickFun( uType, pyClickFun):
	'''
	载入点击函数
	@param uType : UI16
	@param pyClickFun : PyObject*
	@return: None 
			 line 78 Py_RETURN_NONE;
	@see : { "LoadNPCClickFun", LoadNPCClickFun, METH_VARARGS, "载入点击函数  "},
	'''

def GetFlyNPCPos( nNPCID):
	'''
	获取一个传送NPC信息
	@param nNPCID : UI32
	@return: None 
			 line 96 Py_RETURN_NONE;
	@return: None 
			 line 105 Py_RETURN_NONE;
	@return: UI32,UI16,UI16 
			 line 112 return Py_BuildValue("IHH", uSceneId, uX, uY);
	@see : { "GetFlyNPCPos", GetFlyNPCPos, METH_O, "获取一个传送NPC信息  "},
	'''

#automatic_end
