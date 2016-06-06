/*我是UTF8编码文件 */
#include "PyPublicScene.h"
#include "PublicScene.h"
#include "Role.h"
#include "PyRole.h"
#include "NPC.h"

namespace ServerPython
{
	void PyPublicScene_Dealloc(PyPublicSceneObject* self)
	{
		PyObject_DEL(self);
	}

	PyObject* GetSceneID(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetSceneID());
	}

	PyObject* GetSceneName(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return PyString_FromString(self->cptr->SceneName().c_str());
	}


	PyObject* GetSceneType(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetSceneType());
	}


	PyObject* CanSeeOther(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->SetCanSeeOther(true);
		Py_RETURN_NONE;
	}

	PyObject* CannotSeeOther(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->SetCanSeeOther(false);
		Py_RETURN_NONE;
	} 

	PyObject* SetMoveTimeJap(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 ujap;
		if (!GEPython::PyObjToUI16(arg, ujap))
		{
			PY_PARAM_ERROR("SetMoveTimeJap param most be 'GE::Uint16'");
		}
		self->cptr->SetMoveTimeJap(ujap);
		Py_RETURN_NONE;
	}

	PyObject* SetMoveDistanceJap(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 ujap;
		if (!GEPython::PyObjToUI16(arg, ujap))
		{
			PY_PARAM_ERROR("SetMoveDistanceJap param most be 'GE::Uint16'");
		}
		self->cptr->SetMoveDistanceJap(ujap);
		Py_RETURN_NONE;
	}



	PyObject* JoinRole(PyPublicSceneObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16	uX = 0;
		GE::Uint16	uY = 0;
		PyObject* pyObj = NULL;
		if (!PyArg_ParseTuple(args, "OHH", &pyObj, &uX, &uY))
		{
			PY_PARAM_ERROR("param most be 'OHH'");
		}
		ServerPython::PyRoleObject* pPyRole = ServerPython::PyRole_FromObj(pyObj);
		if (NULL == pPyRole)
		{
			PY_PARAM_ERROR("1st param must role.");
		}
		if (NULL == pPyRole->cptr)
		{
			PY_PARAM_ERROR("pyrole's cptr is NULL");
		}
		PY_RETURN_BOOL(self->cptr->JoinRole(pPyRole->cptr, uX, uY));
	}

	PyObject* LeaveRole(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		ServerPython::PyRoleObject *pPyRole = ServerPython::PyRole_FromObj(arg);
		if(NULL == pPyRole)
		{
			PY_PARAM_ERROR("param is null");
		}
		if (NULL == pPyRole->cptr)
		{
			PY_PARAM_ERROR("pyrole's cptr is NULL");
		}
		self->cptr->LeaveRole(pPyRole->cptr);
		Py_RETURN_NONE;
	}

	PyObject* RestoreRole(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		ServerPython::PyRoleObject *pPyRole = ServerPython::PyRole_FromObj(arg);
		if(NULL == pPyRole)
		{
			PY_PARAM_ERROR("param is null");
		}
		if (NULL == pPyRole->cptr)
		{
			PY_PARAM_ERROR("pyrole's cptr is NULL");
		}
		self->cptr->RestoreRole(pPyRole->cptr);
		Py_RETURN_NONE;
	}

	


	PyObject* GetAllRole(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		PublicScene::SceneRoleMap& roleMap = self->cptr->GetSceneRoleMap();
		PublicScene::SceneRoleMap::iterator iter = roleMap.begin();
		GEPython::List lis;
		while(iter != roleMap.end())
		{
			if (iter->second->IsKick())
			{
				++iter;
				continue;
			}
			lis.AppendObj_BorrowRef(iter->second->GetPySelf().GetObj_BorrowRef());
			++iter;
		}
		return lis.GetList_NewRef();
	}


	PyObject* SearchRole(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint64 uRoleID;
		if(!GEPython::PyObjToUI64(arg, uRoleID))
		{
			PY_PARAM_ERROR("SearchRole param most be 'GE::ui64'");
		}
		Role* pRole = self->cptr->SearchRole(uRoleID);
		if(NULL == pRole)
		{
			Py_RETURN_NONE;
		}
		return pRole->GetPySelf().GetObj_NewRef();

	}


	PyObject* CreateNPC(PyPublicSceneObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uTypeID = 0;
		GE::Uint16	uX = 0;
		GE::Uint16	uY = 0;
		GE::Uint8 uDirection = 1;
		GE::Uint8	uBroadCast = 0;
		PyObject* pObj = Py_None;
		if (!PyArg_ParseTuple(args, "HHH|BBO", &uTypeID, &uX, &uY, &uDirection, &uBroadCast, &pObj))
		{
			PY_PARAM_ERROR("param most be 'HHH|BBO'");
		}
		bool bBroadCast = false;
		if (uBroadCast > 0)
		{
			bBroadCast = true;
		}
		NPC* pNPC = self->cptr->CreateNPC(uTypeID, uX, uY, uDirection, bBroadCast, pObj);
		if(NULL == pNPC)
		{
			Py_RETURN_NONE;
		}
		return pNPC->GetPySelf().GetObj_NewRef();
	}

	PyObject* DestroyNPC(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32 uGlobalID;

		if(!GEPython::PyObjToUI32(arg, uGlobalID))
		{
			PY_PARAM_ERROR("DestroyNPC param most be 'GE::Uint32'");
		}
		self->cptr->DestroyNPC(uGlobalID);
		Py_RETURN_NONE;
	}

	PyObject* SearchNPC(PyPublicSceneObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32		uNPCID = 0;
		if(!GEPython::PyObjToUI32(args, uNPCID))
		{
			PyErr_SetString(PyExc_RuntimeError, "params must be GE::Uint32.");
			return NULL;
		}
		NPC* pNPC = self->cptr->SearchNPC(uNPCID);
		if(pNPC == NULL)
		{
			Py_RETURN_NONE;
		}
		else
		{
			return pNPC->GetPySelf().GetObj_NewRef();
		}
	}

	PyObject* GetAllNPC(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		PublicScene::SceneNPCMap& npcMap = self->cptr->GetSceneNPCMap();
		PublicScene::SceneNPCMap::iterator iter = npcMap.begin();
		GEPython::List lis;
		while(iter != npcMap.end())
		{
			lis.AppendObj_BorrowRef(iter->second->GetPySelf().GetObj_BorrowRef());
			++iter;
		}
		return lis.GetList_NewRef();
	}


	PyObject* BroadMsg(PyPublicSceneObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->BroadMsg();
		Py_RETURN_NONE;
	}

	PyObject* RectBroadMsg(PyPublicSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		ServerPython::PyRoleObject *pPyRole = ServerPython::PyRole_FromObj(arg);
		if(NULL == pPyRole)
		{
			PY_PARAM_ERROR("param is null");
		}
		if (NULL == pPyRole->cptr)
		{
			PY_PARAM_ERROR("pyrole's cptr is NULL");
		}
		self->cptr->BroadToRect(pPyRole->cptr);
		Py_RETURN_NONE;
	}

	PyObject* Msg(PyPublicSceneObject* self, PyObject* arg)
	{
		MsgCharMsg msg;
		msg.Type(enServerCharMsg);
		PyObject* pObj = Py_None;
		if (!PyArg_ParseTuple(arg, "iiO", &msg.b8.UI32_1(), &msg.b8.UI32_0(), &pObj))
		{
			return NULL;
		}
		PackMessage::Instance()->Reset();
		PackMessage::Instance()->PackMsg(&msg, msg.Size());
		PackMessage::Instance()->PackPyObj(pObj);
		self->cptr->BroadMsg();
		Py_RETURN_NONE;
	}

	static PyMethodDef PyPublicScene_Methods[] = {
		{"GetSceneID", (PyCFunction)GetSceneID, METH_NOARGS, "场景ID  "},
		{"GetSceneName", (PyCFunction)GetSceneName, METH_NOARGS, "场景名字  "},
		{"GetSceneType", (PyCFunction)GetSceneType, METH_NOARGS, "场景类型  "},
		{"CanSeeOther", (PyCFunction)CanSeeOther, METH_NOARGS, "设置可以看到其他玩家  "},
		{"CannotSeeOther", (PyCFunction)CannotSeeOther, METH_NOARGS, "设置看不到其他玩家  "},
		{"SetMoveTimeJap", (PyCFunction)SetMoveTimeJap, METH_O, "设置移动时间忽视参数  " },
		{"SetMoveDistanceJap", (PyCFunction)SetMoveDistanceJap, METH_O, "设置移动距离忽视参数  " },
		{"JoinRole", (PyCFunction)JoinRole, METH_VARARGS, "玩家进入场景  "},
		{"LeaveRole", (PyCFunction)LeaveRole, METH_O, "玩家离开场景  "},
		{"RestoreRole", (PyCFunction)RestoreRole, METH_O, "玩家重登录同步消息恢复场景信息  "},
		{"GetAllRole", (PyCFunction)GetAllRole, METH_NOARGS, "当前场景玩家  "},
		{"SearchRole", (PyCFunction)SearchRole, METH_O, "在场景中查找玩家  "},
		{"CreateNPC", (PyCFunction)CreateNPC, METH_VARARGS, "在场景中创建NPC  "},
		{"DestroyNPC", (PyCFunction)DestroyNPC, METH_O, "在场景中销毁NPC  "},
		{"SearchNPC", (PyCFunction)SearchNPC, METH_O, "在场景中查找一个NPC  "},
		{"GetAllNPC", (PyCFunction)GetAllNPC, METH_NOARGS, "获取当前场景的所以服务器创建的NPC  "},
		{"BroadMsg", (PyCFunction)BroadMsg, METH_VARARGS, "广播消息给该场景内所有角色  "},
		{"Msg", (PyCFunction)Msg, METH_VARARGS, "广播消息给该场景内所有角色  " },
		{"RectBroadMsg", (PyCFunction)RectBroadMsg, METH_O, "广播消息给区域内所有角色  "},
		{ NULL },
	};

	PyDoc_STRVAR(PyPublicScene_Doc, "PyPublicScene_Doc/nPyPublicScene Object");

	PyTypeObject PyPublicSceneType = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"PyPublicScene",
		sizeof(PyPublicSceneObject),
		0,
		(destructor)PyPublicScene_Dealloc,					/* tp_dealloc */
		0,											/* tp_print */
		0,											/* tp_getattr */
		0,											/* tp_setattr */
		0,											/* tp_compare */
		0,											/* tp_repr */
		0,											/* tp_as_number */
		0,											/* tp_as_sequence */
		0,											/* tp_as_mapping */
		0,											/* tp_hash */
		0,											/* tp_call */
		0,											/* tp_str */
		0,											/* tp_getattro */
		0,											/* tp_setattro */
		0,											/* tp_as_buffer */
		0,											/* tp_flags */
		PyPublicScene_Doc,									/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		PyPublicScene_Methods,								/* tp_methods */
		0,											/* tp_members */
		0,											/* tp_getset */
		0,											/* tp_base */
		0,											/* tp_dict */
		0,											/* tp_descr_get */
		0,											/* tp_descr_set */
		0,											/* tp_dictoffset */
		0,											/* tp_init */
		0,											/* tp_alloc */
		0,											/* tp_new */
		0,											/* tp_free */
	};

	void PyPublicScene_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());

		PyType_Ready(&PyPublicSceneType);
		// 根据模块名，查找模块并加入到模块身上
		GEPython::Object spModule = PyImport_ImportModule("cComplexServer");
		if (spModule.PyHasExcept())
		{
			spModule.PyPrintAndClearExcept();
		}
		else
		{
			PyModule_AddObject(spModule.GetObj_BorrowRef(), "cPublicScene", (PyObject*)&PyPublicSceneType);
		}
	}

	PyPublicSceneObject* PyPublicScene_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &PyPublicSceneType)
		{
			return (PyPublicSceneObject*)pObj;
		}
		return NULL;
	}

	PyPublicSceneObject* PyPublicScene_New( PublicScene* pPublicScene )
	{
		PyPublicSceneObject* obj = PyObject_NEW(PyPublicSceneObject, &PyPublicSceneType);
		obj->cptr = pPublicScene;
		return obj;
	}

	void PyPublicScene_Del( PyObject* pObj )
	{
		if (pObj->ob_type != &PyPublicSceneType)
		{
			GE_EXC<<"del obj error "<<__FUNCTION__<<GE_END;
			return;
		}
		PyPublicSceneObject* pPO = (PyPublicSceneObject*)(pObj);
		pPO->cptr = NULL;
	}
}

