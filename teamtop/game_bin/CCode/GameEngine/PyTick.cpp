/*我是UTF8无签名编码 */
#include "PyTick.h"
#include "GETick.h"
#include "GEIO.h"

namespace GEPython
{
	//////////////////////////////////////////////////////////////////////////
	// PyTick
	//////////////////////////////////////////////////////////////////////////
	void PyTick_Dealloc( PyTickObject *self )
	{
		PyObject_DEL( self );
	};

	PyObject* CPtr(PyTickObject* self, PyObject* arg)
	{
		PY_RETURN_BOOL(self->cptr != NULL);
	};

	PyObject* RegTick(PyTickObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32 uSec = 0;
		PyObject* pCallback_BorrowRef = NULL;
		PyObject* pParam_BorrowRef = NULL;
		if (!PyArg_ParseTuple(args, "IOO", &uSec, &pCallback_BorrowRef, &pParam_BorrowRef))
		{
			return NULL;
		}
#ifdef WIN
		if (!PyCallable_Check(pCallback_BorrowRef))
		{
			PY_PARAM_ERROR("the 2nd param must a callable pyobj.");
		}
#endif
		return GEPython::PyObjFromUI64(self->cptr->RegTick(uSec, pCallback_BorrowRef, pParam_BorrowRef));
	};

	PyObject* UnregTick(PyTickObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint64 uID = 0;
		if (!GEPython::PyObjToUI64(arg, uID))
		{
			PY_PARAM_ERROR("param need GE::Uint64.")
		}
		PY_RETURN_BOOL(self->cptr->UnregTick(uID));
	};

	PyObject* TriggerTick(PyTickObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint64 uID = 0;
		if (!GEPython::PyObjToUI64(arg, uID))
		{
			PY_PARAM_ERROR("param need GE::Uint64.")
		}
		PY_RETURN_BOOL(self->cptr->TriggerTick(uID));
	};

	static PyMethodDef PyTick_Methods[] = {
		{"CPtr", (PyCFunction)CPtr, METH_NOARGS, "CPtr是否有效  "},
		{"RegTick", (PyCFunction)RegTick, METH_VARARGS, "注册一个Tick  "},
		{"UnregTick", (PyCFunction)UnregTick, METH_O, "取消一个Tick  "},
		{"TriggerTick", (PyCFunction)TriggerTick, METH_O, "强制触发一个Tick  "},
		{ NULL },
	};

	PyDoc_STRVAR(PyTick_Doc, "Tick\nProcess.Tick Object");

	PyTypeObject PyTick_Type = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"PyTick",
		sizeof(PyTickObject),
		0,
		(destructor)PyTick_Dealloc,					/* tp_dealloc */
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
		PyTick_Doc,									/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		PyTick_Methods,								/* tp_methods */
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

	PyTickObject* PyTick_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &PyTick_Type)
		{
			return (PyTickObject*)pObj;
		}
		return NULL;
	}

	PyTickObject* PyTick_New( GETick* pCPtr )
	{
		PyTickObject* ret = PyObject_NEW(PyTickObject, &PyTick_Type);
		ret->cptr = pCPtr;
		return ret;
	}

	void PyTick_Del( PyObject* pObj)
	{
		if (pObj->ob_type != &PyTick_Type)
		{
			GE_EXC<<"error on PyTick_Del function."<<GE_END;
			return;
		}
		PyTickObject* pPTO = (PyTickObject*)pObj;
		pPTO->cptr = NULL;
	}

	void PyTick_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyType_Ready( &PyTick_Type );
	}


	//////////////////////////////////////////////////////////////////////////
	// PySmallTick
	//////////////////////////////////////////////////////////////////////////
	void PySmallTick_Dealloc( PySmallTickObject *self )
	{
		PyObject_DEL( self );
	};

	PyObject* CPtr_small(PySmallTickObject* self, PyObject* arg)
	{
		PY_RETURN_BOOL(self->cptr != NULL);
	};

	PyObject* RegTick_small(PySmallTickObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32 uSec = 0;
		PyObject* pCallback_BorrowRef = NULL;
		PyObject* pParam_BorrowRef = NULL;
		if (!PyArg_ParseTuple(args, "IOO", &uSec, &pCallback_BorrowRef, &pParam_BorrowRef))
		{
			return NULL;
		}
#ifdef WIN
		if (!PyCallable_Check(pCallback_BorrowRef))
		{
			PY_PARAM_ERROR("the 2nd param must a callable pyobj.");
		}
#endif
		return GEPython::PyObjFromI32(self->cptr->RegTick(uSec, pCallback_BorrowRef, pParam_BorrowRef));
	};

	PyObject* UnregTick_small(PySmallTickObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Int32 ID = 0;
		if (!GEPython::PyObjToI32(arg, ID))
		{
			PY_PARAM_ERROR("param need GE::Int32.")
		}
		PY_RETURN_BOOL(self->cptr->UnregTick(ID));
	};

	PyObject* TriggerTick_small(PySmallTickObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Int32 ID = 0;
		if (!GEPython::PyObjToI32(arg, ID))
		{
			PY_PARAM_ERROR("param need GE::Int32.")
		}
		PY_RETURN_BOOL(self->cptr->TriggerTick(ID));
	};

	static PyMethodDef PySmallTick_Methods[] = {
		{"CPtr", (PyCFunction)CPtr_small, METH_NOARGS, "CPtr是否有效  "},
		{"RegTick", (PyCFunction)RegTick_small, METH_VARARGS, "注册一个Tick  "},
		{"UnregTick", (PyCFunction)UnregTick_small, METH_O, "取消一个Tick  "},
		{"TriggerTick", (PyCFunction)TriggerTick_small, METH_O, "强制触发一个Tick  "},
		{ NULL },
	};

	PyDoc_STRVAR(PySmallTick_Doc, "SmallTick\nSmallTick Object");

	PyTypeObject PySmallTick_Type = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"PySmallTick",
		sizeof(PySmallTickObject),
		0,
		(destructor)PySmallTick_Dealloc,			/* tp_dealloc */
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
		PySmallTick_Doc,							/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		PySmallTick_Methods,						/* tp_methods */
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

	PySmallTickObject* PySmallTick_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &PySmallTick_Type)
		{
			return (PySmallTickObject*)pObj;
		}
		return NULL;
	}

	PySmallTickObject* PySmallTick_New( GESmallTick* pCPtr )
	{
		PySmallTickObject* ret = PyObject_NEW(PySmallTickObject, &PySmallTick_Type);
		ret->cptr = pCPtr;
		return ret;
	}

	void PySmallTick_Del( PyObject* pObj)
	{
		if (pObj->ob_type != &PySmallTick_Type)
		{
			GE_EXC<<"error on PySmallTick_Del function."<<GE_END;
			return;
		}
		PySmallTickObject* pPTO = (PySmallTickObject*)pObj;
		pPTO->cptr = NULL;
	}

	void PySmallTick_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyType_Ready( &PySmallTick_Type );
	}
}

