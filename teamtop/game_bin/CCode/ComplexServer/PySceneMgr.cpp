#include "PySceneMgr.h"
#include "SceneMgr.h"
#include "Role.h"
#include "MapMgr.h"
#include "PublicScene.h"
#include "Mirror.h"
//////////////////////////////////////////////////////////////////////////
// PySceneMgr模块
//////////////////////////////////////////////////////////////////////////
namespace ServerPython
{
	PyObject* CreateMapTemplate(PyObject* self, PyObject* args)
	{
		GE::Uint16 uMapId = 0;
		const char* sFilePath;;
		if (!PyArg_ParseTuple(args, "Hs", &uMapId, &sFilePath))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be 'Hs'.");
			return NULL;
		}
		// 创建一个地图模板
		MapMgr::Instance()->CreateMapTemplate(uMapId, sFilePath);
		Py_RETURN_NONE;
	}


	PyObject* CreatePublicScene(PyObject* self, PyObject* args)
	{
		GE::Uint32			uMapID = 0;
		GE::Uint32			uSceneID = 0;
		GE::Uint8			uAreaSize = 0;
		GE::Uint8			uIsSave = 0;
		GE::Uint8			uCanSeeOther = 0;
		char* name = NULL;
		PyObject* pyAfterCreateFun = NULL;
		PyObject* pyAfterJoinRoleFun = NULL;
		PyObject* pyBeforeLeaveFun = NULL;
		PyObject* pyAfterRestoreFun = NULL;
		if (!PyArg_ParseTuple(args, "IsIBBB|OOOO", &uSceneID, &name, &uMapID, &uAreaSize, &uIsSave, &uCanSeeOther, &pyAfterCreateFun, &pyAfterJoinRoleFun, &pyBeforeLeaveFun, &pyAfterRestoreFun))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be 'IsIBBB|OOOO'.");
			return NULL;
		}

		PublicScene* pScene = SceneMgr::Instance()->CreatePublicScene(uMapID, uSceneID, name, uAreaSize, uIsSave, uCanSeeOther, pyAfterCreateFun, pyAfterJoinRoleFun, pyBeforeLeaveFun, pyAfterRestoreFun);
		if(pScene)
		{
			pScene->AfterCreate();
			return pScene->PySelf().GetObj_NewRef();
		}
		Py_RETURN_NONE;
	}

	PyObject* SearchPublicScene(PyObject* self, PyObject* args)
	{
		GE::Uint32		uSceneID = 0;
		if(!GEPython::PyObjToUI32(args, uSceneID))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be GE::Uint32.");
			return NULL;
		}
		PublicScene* pScene = SceneMgr::Instance()->SearchPublicScene(uSceneID);
		if(pScene == NULL)
		{
			Py_RETURN_NONE;
		}
		else
		{
			return pScene->PySelf().GetObj_NewRef();
		}
	}

	PyObject* CreateSingleMirrorScene(PyObject* self, PyObject* args)
	{
		GE::Uint32			uGlobalID = 0;
		GE::Uint16			uMapID = 0;
		GE::Uint32			uSceneID = 0;
		char*				name = NULL;
		PyObject* pyBeforeLeaveFun = NULL;

		if (!PyArg_ParseTuple(args, "IIsH|O", &uGlobalID, &uSceneID, &name, &uMapID, &pyBeforeLeaveFun))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be 'IIsH|O' on CreateSingleMirrorScene");
			return NULL;
		}
		SingleMirrorScene* pScene = SceneMgr::Instance()->CreateSingleMirrorScene(uGlobalID, uMapID, uSceneID, name, pyBeforeLeaveFun);
		if(pScene)
		{
			return pScene->PySelf().GetObj_NewRef();
		}
		Py_RETURN_NONE;
	}

	PyObject* CreateMultiMirrorScene(PyObject* self, PyObject* args)
	{
		GE::Uint32			uGlobalID = 0;
		GE::Uint16			uMapID = 0;
		GE::Uint32			uSceneID = 0;
		char* name = NULL;
		PyObject* pyBeforeLeaveFun = NULL;
		PyObject* pyIsAlive = Py_False;
		if (!PyArg_ParseTuple(args, "IIsH|OO", &uGlobalID, &uSceneID, &name, &uMapID, &pyBeforeLeaveFun, &pyIsAlive))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be 'IIsH|O' on CreateSingleMirrorScene");
			return NULL;
		}
		bool bIsAlive = false;
		if (PyObject_IsTrue(pyIsAlive))
		{
			bIsAlive = true;
		}
		MultiMirrorScene* pScene = SceneMgr::Instance()->CreateMultiMirrorScene(uGlobalID, uMapID, uSceneID, name, pyBeforeLeaveFun, bIsAlive);
		if(pScene)
		{
			return pScene->PySelf().GetObj_NewRef();
		}
		else
		{
			Py_RETURN_NONE;
		}
	}

	PyObject* LoadMapSafePos(PyObject* self, PyObject* args)
	{
		GE::Uint16			uMapID = 0;
		GE::Uint16			uX = 0;
		GE::Uint16			uY = 0;
		if (!PyArg_ParseTuple(args, "HHH", &uMapID, &uX, &uY))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be 'HHH' on LoadMapSafePos");
			return NULL;
		}
		MapMgr::Instance()->SetSafePos(uMapID, uX, uY);
		Py_RETURN_NONE;
	}

	PyObject* SceneBroadMsg(PyObject* self, PyObject* args)
	{
		GE::Uint32		uSceneID = 0;
		if(!GEPython::PyObjToUI32(args, uSceneID))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be GE::Uint32.");
			return NULL;
		}
		PublicScene* pScene = SceneMgr::Instance()->SearchPublicScene(uSceneID);
		if(pScene)
		{
			pScene->BroadMsg();
		}
		Py_RETURN_NONE;
	}


	// PySceneMgr_Methods[]
	static PyMethodDef PySceneMgr_Methods[] = {
		{ "CreateMapTemplate", CreateMapTemplate, METH_VARARGS, "创建一个地图模板  "},
		{ "CreatePublicScene", CreatePublicScene, METH_VARARGS, "创建一个场景  "},
		{ "SearchPublicScene", SearchPublicScene, METH_O, "根据场景ID查找场景对象  "},
		{ "CreateSingleMirrorScene", CreateSingleMirrorScene, METH_VARARGS, "创建一个单人关卡场景  "},
		{ "CreateMultiMirrorScene", CreateMultiMirrorScene, METH_VARARGS, "创建一个多人关卡场景  "},
		{ "LoadMapSafePos", LoadMapSafePos, METH_VARARGS, "读取安全坐标配置  "},
		{ "BroadMsg", SceneBroadMsg, METH_O, "根据场景ID发送一个广播消息给该场景内所有角色  "},
		{ NULL }
	};

	// PySceneMgr_Init
	void PySceneMgr_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* pSceneMgr = Py_InitModule("cSceneMgr", PySceneMgr_Methods);
		if (NULL == pSceneMgr)
		{
			PyErr_Print();
		}
	}
}

