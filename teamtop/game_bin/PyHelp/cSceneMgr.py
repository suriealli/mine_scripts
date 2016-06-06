#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有7个Py函数定义

def CreateMapTemplate( uMapId, sFilePath):
	'''
	创建一个地图模板
	@param uMapId : UI16
	@param sFilePath : string
	@return: None 
			 line 22 Py_RETURN_NONE;
	@see : { "CreateMapTemplate", CreateMapTemplate, METH_VARARGS, "创建一个地图模板  "},
	'''

def CreatePublicScene( uSceneID, name, uMapID, uAreaSize, uIsSave, uCanSeeOther, pyAfterCreateFun=None , pyAfterJoinRoleFun=None , pyBeforeLeaveFun=None , pyAfterRestoreFun=None ):
	'''
	创建一个场景
	@param uSceneID : UI32
	@param name : string
	@param uMapID : UI32
	@param uAreaSize : UI8
	@param uIsSave : UI8
	@param uCanSeeOther : UI8
	@param pyAfterCreateFun : PyObject*
	@param pyAfterJoinRoleFun : PyObject*
	@param pyBeforeLeaveFun : PyObject*
	@param pyAfterRestoreFun : PyObject*
	@return: PyObject* 
			 line 48 return pScene->PySelf().GetObj_NewRef();
	@return: None 
			 line 50 Py_RETURN_NONE;
	@warning: return pScene->PySelf().GetObj_NewRef();
	@see : { "CreatePublicScene", CreatePublicScene, METH_VARARGS, "创建一个场景  "},
	'''

def SearchPublicScene( uSceneID):
	'''
	根据场景ID查找场景对象
	@param uSceneID : UI32
	@return: None 
			 line 64 Py_RETURN_NONE;
	@return: PyObject* 
			 line 68 return pScene->PySelf().GetObj_NewRef();
	@warning: return pScene->PySelf().GetObj_NewRef();
	@see : { "SearchPublicScene", SearchPublicScene, METH_O, "根据场景ID查找场景对象  "},
	'''

def CreateSingleMirrorScene( uGlobalID, uSceneID, name, uMapID, pyBeforeLeaveFun=None ):
	'''
	创建一个单人关卡场景
	@param uGlobalID : UI32
	@param uSceneID : UI32
	@param name : string
	@param uMapID : UI16
	@param pyBeforeLeaveFun : PyObject*
	@return: PyObject* 
			 line 88 return pScene->PySelf().GetObj_NewRef();
	@return: None 
			 line 90 Py_RETURN_NONE;
	@warning: return pScene->PySelf().GetObj_NewRef();
	@see : { "CreateSingleMirrorScene", CreateSingleMirrorScene, METH_VARARGS, "创建一个单人关卡场景  "},
	'''

def CreateMultiMirrorScene( uGlobalID, uSceneID, name, uMapID, pyBeforeLeaveFun=None , pyIsAlive=None ):
	'''
	创建一个多人关卡场景
	@param uGlobalID : UI32
	@param uSceneID : UI32
	@param name : string
	@param uMapID : UI16
	@param pyBeforeLeaveFun : PyObject*
	@param pyIsAlive : PyObject*
	@return: PyObject* 
			 line 114 return pScene->PySelf().GetObj_NewRef();
	@return: None 
			 line 118 Py_RETURN_NONE;
	@warning: return pScene->PySelf().GetObj_NewRef();
	@see : { "CreateMultiMirrorScene", CreateMultiMirrorScene, METH_VARARGS, "创建一个多人关卡场景  "},
	'''

def LoadMapSafePos( uMapID, uX, uY):
	'''
	读取安全坐标配置
	@param uMapID : UI16
	@param uX : UI16
	@param uY : UI16
	@return: None 
			 line 133 Py_RETURN_NONE;
	@see : { "LoadMapSafePos", LoadMapSafePos, METH_VARARGS, "读取安全坐标配置  "},
	'''

def BroadMsg( uSceneID):
	'''
	根据场景ID发送一个广播消息给该场景内所有角色
	@param uSceneID : UI32
	@return: None 
			 line 149 Py_RETURN_NONE;
	@see : { "BroadMsg", SceneBroadMsg, METH_O, "根据场景ID发送一个广播消息给该场景内所有角色  "},
	'''

#automatic_end
