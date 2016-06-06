/*我是UTF8编码文件 */
#include "PyMultiMirrorScene.h"
#include "Mirror.h"
#include "Role.h"
#include "PyRole.h"
#include "NPC.h"


namespace ServerPython
{
	void PyMultiMirrorScene_Dealloc(PyMultiMirrorSceneObject* self)
	{
		PyObject_DEL(self);
	}

	PyObject* IsDestroy(PyMultiMirrorSceneObject* self, PyObject* arg)
	{
		if (NULL == self->cptr)
		{
			Py_RETURN_TRUE;
		}
		else
		{
			Py_RETURN_FALSE;
		}
	}
	PyObject* GetSceneID(PyMultiMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetSceneID());
	}

	PyObject* GetSceneName(PyMultiMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return PyString_FromString(self->cptr->SceneName().c_str());
	}


	PyObject* GetSceneType(PyMultiMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetSceneType());
	}


	PyObject* JoinRole(PyMultiMirrorSceneObject* self, PyObject* args)
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

	PyObject* LeaveRole(PyMultiMirrorSceneObject* self, PyObject* arg)
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


	PyObject* SearchRole(PyMultiMirrorSceneObject* self, PyObject* arg)
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
	
	
	PyObject* Destroy(PyMultiMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->Destroy();
		Py_RETURN_NONE;
	}

	PyObject* ReadyToDestroy(PyMultiMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->ReadyToDestroy();
		Py_RETURN_NONE;
	}
	
	PyObject* RestoreRole(PyMultiMirrorSceneObject* self, PyObject* arg)
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

	static PyMethodDef PyMultiMirrorScene_Methods[] = {
		{"GetSceneID", (PyCFunction)GetSceneID, METH_NOARGS, "场景ID  "},
		{"GetSceneName", (PyCFunction)GetSceneName, METH_NOARGS, "场景名字  "},
		{"GetSceneType", (PyCFunction)GetSceneType, METH_NOARGS, "场景类型  "},
		{"JoinRole", (PyCFunction)JoinRole, METH_VARARGS, "玩家进入场景  "},
		{"LeaveRole", (PyCFunction)LeaveRole, METH_O, "玩家离开场景  "},
		{"SearchRole", (PyCFunction)SearchRole, METH_O, "在场景中查找玩家  "},
		{"Destroy", (PyCFunction)Destroy, METH_NOARGS, "销毁场景  "},
		{"ReadyToDestroy", (PyCFunction)ReadyToDestroy, METH_NOARGS, "设置为准备销毁  "},
		{"IsDestroy", (PyCFunction)IsDestroy, METH_NOARGS, "是否已经销毁了  "},
		{"RestoreRole", (PyCFunction)RestoreRole, METH_O, "玩家恢复场景  "},
		{ NULL },
	};

	PyDoc_STRVAR(PyMultiMirrorScene_Doc, "PyMultiMirrorScene_Doc/nPyMultiMirrorScene Object");

	PyTypeObject PyMultiMirrorSceneType = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"PyMultiMirrorScene",
		sizeof(PyMultiMirrorSceneObject),
		0,
		(destructor)PyMultiMirrorScene_Dealloc,					/* tp_dealloc */
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
		PyMultiMirrorScene_Doc,									/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		PyMultiMirrorScene_Methods,								/* tp_methods */
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

	void PyMultiMirrorScene_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());

		PyType_Ready(&PyMultiMirrorSceneType);
		// 根据模块名，查找模块并加入到模块身上
		GEPython::Object spModule = PyImport_ImportModule("cComplexServer");
		if (spModule.PyHasExcept())
		{
			spModule.PyPrintAndClearExcept();
		}
		else
		{
			PyModule_AddObject(spModule.GetObj_BorrowRef(), "cMultiMirrorScene", (PyObject*)&PyMultiMirrorSceneType);
		}
	}

	PyMultiMirrorSceneObject* PyMultiMirrorScene_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &PyMultiMirrorSceneType)
		{
			return (PyMultiMirrorSceneObject*)pObj;
		}
		return NULL;
	}

	PyMultiMirrorSceneObject* PyMultiMirrorScene_New( MultiMirrorScene* pMultiMirrorScene )
	{
		PyMultiMirrorSceneObject* obj = PyObject_NEW(PyMultiMirrorSceneObject, &PyMultiMirrorSceneType);
		obj->cptr = pMultiMirrorScene;
		return obj;
	}

	void PyMultiMirrorScene_Del( PyObject* pObj )
	{
		if (pObj->ob_type != &PyMultiMirrorSceneType)
		{
			GE_EXC<<"del obj error "<<__FUNCTION__<<GE_END;
			return;
		}
		PyMultiMirrorSceneObject* pPO = (PyMultiMirrorSceneObject*)(pObj);
		pPO->cptr = NULL;
	}
}

