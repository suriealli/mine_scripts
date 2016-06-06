/*我是UTF8编码文件 */
#include "PySingleMirrorScene.h"
#include "Mirror.h"
#include "Role.h"
#include "PyRole.h"
#include "NPC.h"
namespace ServerPython
{
	void PySingleMirrorScene_Dealloc(PySingleMirrorSceneObject* self)
	{
		PyObject_DEL(self);
	}

	PyObject* IsDestroy(PySingleMirrorSceneObject* self, PyObject* arg)
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

	PyObject* GetSceneID(PySingleMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetSceneID());
	}

	PyObject* GetSceneName(PySingleMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return PyString_FromString(self->cptr->SceneName().c_str());
	}


	PyObject* GetSceneType(PySingleMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetSceneType());
	}

	PyObject* Destroy(PySingleMirrorSceneObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->Destroy();
		Py_RETURN_NONE;
	}

	PyObject* JoinRole(PySingleMirrorSceneObject* self, PyObject* args)
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

	PyObject* LeaveRole(PySingleMirrorSceneObject* self, PyObject* arg)
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

	PyObject* RestoreRole(PySingleMirrorSceneObject* self, PyObject* arg)
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

	

	static PyMethodDef PySingleMirrorScene_Methods[] = {
		{"GetSceneID", (PyCFunction)GetSceneID, METH_NOARGS, "场景ID  "},
		{"GetSceneName", (PyCFunction)GetSceneName, METH_NOARGS, "场景名字  "},
		{"GetSceneType", (PyCFunction)GetSceneType, METH_NOARGS, "场景类型  "},
		{"Destroy", (PyCFunction)Destroy, METH_NOARGS, "销毁场景  "},
		{"JoinRole", (PyCFunction)JoinRole, METH_VARARGS, "玩家进入场景  "},
		{"LeaveRole", (PyCFunction)LeaveRole, METH_O, "玩家离开场景  "},
		{"IsDestroy", (PyCFunction)IsDestroy, METH_NOARGS, "是否已经销毁了  "},
		{"RestoreRole", (PyCFunction)RestoreRole, METH_O, "玩家恢复场景  "},
		{ NULL },
	};

	PyDoc_STRVAR(PySingleMirrorScene_Doc, "PySingleMirrorScene_Doc/nPySingleMirrorScene Object");

	PyTypeObject PySingleMirrorSceneType = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"PySingleMirrorScene",
		sizeof(PySingleMirrorSceneObject),
		0,
		(destructor)PySingleMirrorScene_Dealloc,					/* tp_dealloc */
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
		PySingleMirrorScene_Doc,									/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		PySingleMirrorScene_Methods,								/* tp_methods */
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

	void PySingleMirrorScene_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());

		PyType_Ready(&PySingleMirrorSceneType);
		// 根据模块名，查找模块并加入到模块身上
		GEPython::Object spModule = PyImport_ImportModule("cComplexServer");
		if (spModule.PyHasExcept())
		{
			spModule.PyPrintAndClearExcept();
		}
		else
		{
			PyModule_AddObject(spModule.GetObj_BorrowRef(), "cSingleMirrorScene", (PyObject*)&PySingleMirrorSceneType);
		}
	}

	PySingleMirrorSceneObject* PySingleMirrorScene_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &PySingleMirrorSceneType)
		{
			return (PySingleMirrorSceneObject*)pObj;
		}
		return NULL;
	}

	PySingleMirrorSceneObject* PySingleMirrorScene_New( SingleMirrorScene* pSingleMirrorScene )
	{
		PySingleMirrorSceneObject* obj = PyObject_NEW(PySingleMirrorSceneObject, &PySingleMirrorSceneType);
		obj->cptr = pSingleMirrorScene;
		return obj;
	}

	void PySingleMirrorScene_Del( PyObject* pObj )
	{
		if (pObj->ob_type != &PySingleMirrorSceneType)
		{
			GE_EXC<<"del obj error "<<__FUNCTION__<<GE_END;
			return;
		}
		PySingleMirrorSceneObject* pPO = (PySingleMirrorSceneObject*)(pObj);
		pPO->cptr = NULL;
	}
}

