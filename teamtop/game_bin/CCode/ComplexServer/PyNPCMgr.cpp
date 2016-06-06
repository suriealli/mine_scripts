#include "PyNPCMgr.h"
#include "NPCMgr.h"
#include "Role.h"
#include "NPC.h"
//////////////////////////////////////////////////////////////////////////
// PyNPCMgr模块
//////////////////////////////////////////////////////////////////////////
namespace ServerPython
{

	PyObject* CreateNPCTemplate(PyObject* self, PyObject* args)
	{
		GE::Uint16		uType = 0;
		GE::Uint16		uLen = 0;
		char*			name = NULL;
		GE::Uint8		uClickType = 0;
		GE::Uint8		uIsMovingNPC = 0;
		if (!PyArg_ParseTuple(args, "HsHBB", &uType, &name, &uLen, &uClickType, &uIsMovingNPC))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be 'HsHBB'.");
			return NULL;
		}
		NPCMgr::Instance()->CreateNPCTemplate(uType, name, uLen, uClickType, uIsMovingNPC);
		Py_RETURN_NONE;
	}

	PyObject* SearchNPC(PyObject* self, PyObject* args)
	{
		GE::Uint32		uNPCID = 0;
		if(!GEPython::PyObjToUI32(args, uNPCID))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be GE::Uint32.");
			return NULL;
		}
		NPC* pNPC = NPCMgr::Instance()->SearchNPC(uNPCID);
		if(pNPC == NULL)
		{
			Py_RETURN_NONE;
		}
		else
		{
			return pNPC->GetPySelf().GetObj_NewRef();
		}
	}

	PyObject* CreateNPCConfigObj(PyObject* self, PyObject* args)
	{
		GE::Uint32		uID = 0;
		GE::Uint32		uSceneID = 0;
		GE::Uint16		uType = 0;
		GE::Uint16		uX = 0;
		GE::Uint16		uY = 0;

		if (!PyArg_ParseTuple(args, "IIHHH", &uID, &uSceneID, &uType, &uX, &uY))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be 'IIHHH'.");
			return NULL;
		}
		NPCMgr::Instance()->CreateNPCConfigObj(uID, uType, uSceneID, uX, uY);
		Py_RETURN_NONE;
	}

	PyObject* AllotGlobalID(PyObject* self, PyObject* args)
	{
		return GEPython::PyObjFromUI32(NPCMgr::Instance()->AllotGlobalID());
	}

	PyObject* LoadNPCClickFun(PyObject* self, PyObject* args)
	{
		GE::Uint16		uType = 0;
		PyObject*		pyClickFun = NULL;

		if (!PyArg_ParseTuple(args, "HO", &uType, &pyClickFun))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be 'HO'.");
			return NULL;
		}
		NPCMgr::Instance()->LoadNPCClickFun(uType, pyClickFun);
		Py_RETURN_NONE;
	}
	
	PyObject* GetFlyNPCPos(PyObject* self, PyObject* arg)
	{
		GE::Uint32 nNPCID = 0;
		if (!GEPython::PyObjToUI32(arg, nNPCID))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}

		GE::Uint32 uSceneId = 0;
		GE::Uint16 uX = 0;
		GE::Uint16 uY = 0;
		if(nNPCID < MAX_CFG_NPC_ID)
		{
			if(NPCMgr::Instance()->GetFlyNPCPos(nNPCID, uSceneId, uX, uY) == false)
			{
				Py_RETURN_NONE;
			}
		}
		else
		{

			NPC* pNPC = NPCMgr::Instance()->SearchNPC(nNPCID);
			if (NULL == pNPC)
			{
				Py_RETURN_NONE;
			}
			uSceneId = pNPC->GetSceneID();
			uX = pNPC->GetPosX();
			uY = pNPC->GetPosY();

		}
		return Py_BuildValue("IHH", uSceneId, uX, uY);
	}
	
	// PyNPCMgr_Methods[]
	static PyMethodDef PyNPCMgr_Methods[] = {
		{ "CreateNPCTemplate", CreateNPCTemplate, METH_VARARGS, "创建一个NPC模板  "},
		{ "CreateNPCConfigObj", CreateNPCConfigObj, METH_VARARGS, "创建一个NPC模板  "},
		{ "SearchNPC", SearchNPC, METH_O, "搜索一个NPC  "},
		{ "AllotGlobalID", AllotGlobalID, METH_NOARGS, "分配一个ID  "},
		{ "LoadNPCClickFun", LoadNPCClickFun, METH_VARARGS, "载入点击函数  "},
		{ "GetFlyNPCPos", GetFlyNPCPos, METH_O, "获取一个传送NPC信息  "},
		{ NULL }
	};

	// PyNPCMgr_Init
	void PyNPCMgr_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* pNPCMgr = Py_InitModule("cNPCMgr", PyNPCMgr_Methods);
		if (NULL == pNPCMgr)
		{
			PyErr_Print();
		}
	}
}

