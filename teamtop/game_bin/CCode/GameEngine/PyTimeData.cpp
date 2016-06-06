/*我是UTF8无签名编码 */
#include "PyTimeData.h"
#include "GETimeData.h"
#include "GEIO.h"

namespace GEPython
{
	void PyTimeData_Dealloc( PyTimeDataObject *self )
	{
		PyObject_DEL( self );
	};

	PyObject* CPtr(PyTimeDataObject* self, PyObject* arg)
	{
		PY_RETURN_BOOL(self->cptr != NULL);
	};

	PyObject* HoldData(PyTimeDataObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32 uSec = 0;
		PyObject* pyData_BorrowRef = NULL;
		if (!PyArg_ParseTuple(args, "IO", &uSec, &pyData_BorrowRef))
		{
			return NULL;
		}
		return GEPython::PyObjFromUI64(self->cptr->HoldData(uSec, pyData_BorrowRef));
	}

	PyObject* RemoveData(PyTimeDataObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint64 uID = 0;
		if (!GEPython::PyObjToUI64(arg, uID))
		{
			PY_PARAM_ERROR("param must be GE::Uint64");
		}
		self->cptr->RemoveData(uID);
		Py_RETURN_NONE;
	}

	PyObject* FindData(PyTimeDataObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint64 uID = 0;
		if (!GEPython::PyObjToUI64(arg, uID))
		{
			PY_PARAM_ERROR("param must be GE::Uint64");
		}
		return self->cptr->FindData_NewRef(uID);
	}

	PyObject* FindRemoveData(PyTimeDataObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint64 uID = 0;
		if (!GEPython::PyObjToUI64(arg, uID))
		{
			PY_PARAM_ERROR("param must be GE::Uint64");
		}
		return self->cptr->FindAndRemoveData_NewRef(uID);
	}

	static PyMethodDef PyTimeData_Methods[] = {
		{"CPtr", (PyCFunction)CPtr, METH_NOARGS, "CPtr是否有效  "},
		{"HoldData", (PyCFunction)HoldData, METH_VARARGS, "委托一个Python数据  "},
		{"RemoveData", (PyCFunction)RemoveData, METH_O, "删除一个委托的Python数据  "},
		{"FindData", (PyCFunction)FindData, METH_O, "查找一个委托的Python数据  "},
		{"FindRemoveData", (PyCFunction)FindRemoveData, METH_O, "查找并删除一个委托的Python数据  "},
		{ NULL },
	};

	PyDoc_STRVAR(PyTimeData_Doc, "CPPTick\nProcess.CPPTick Object");

	PyTypeObject PyTimeData_Type = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"PyTimeData",
		sizeof(PyTimeDataObject),
		0,
		(destructor)PyTimeData_Dealloc,				/* tp_dealloc */
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
		PyTimeData_Doc,								/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		PyTimeData_Methods,							/* tp_methods */
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

	PyTimeDataObject* PyTimeData_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &PyTimeData_Type)
		{
			return (PyTimeDataObject*)pObj;
		}
		return NULL;
	}

	PyTimeDataObject* PyTimeData_New( GETimeData* pCPtr )
	{
		PyTimeDataObject* ret = PyObject_NEW(PyTimeDataObject, &PyTimeData_Type);
		ret->cptr = pCPtr;
		return ret;
	}

	void PyTimeData_Del( PyObject* pObj )
	{
		if (pObj->ob_type != &PyTimeData_Type)
		{
			GE_EXC<<"error on PyTimeData_Del function."<<GE_END;
			return;
		}
		PyTimeDataObject* pPTO = (PyTimeDataObject*)pObj;
		pPTO->cptr = NULL;
	}

	void PyTimeData_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyType_Ready( &PyTimeData_Type );
	}

}

