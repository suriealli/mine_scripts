/*我是UTF8编码文件 */
#include "PyNPC.h"
#include "NPC.h"
#include "Role.h"
#include "PyRole.h"
#include "NPCMgr.h"

namespace ServerPython
{
	void PyNPC_Dealloc(PyNPCObject* self)
	{
		PyObject_DEL(self);
	}

	PyObject* GetNPCID(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetNPCID());
	}

	PyObject* GetNPCName(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return PyString_FromString(self->cptr->GetNPCName().c_str());
	}


	PyObject* GetNPCType(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetNPCType());
	}


	PyObject* GetPos(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return Py_BuildValue("HH", self->cptr->GetPosX(), self->cptr->GetPosY());
	}

	PyObject* SetPyDict(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN
		PyObject* pyKey = Py_None;
		PyObject* pyValue = Py_None;
		if (!PyArg_ParseTuple(arg, "OO", &pyKey, &pyValue))
		{
			return NULL;
		}
		self->cptr->SetPyDict(pyKey, pyValue);
		Py_RETURN_NONE;
	}

	PyObject* GetPyDict(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->GetPyDict();
	}

	PyObject* SetPySyncDict(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN
			PyObject* pyKey = Py_None;
		PyObject* pyValue = Py_None;
		if (!PyArg_ParseTuple(arg, "OO", &pyKey, &pyValue))
		{
			return NULL;
		}
		self->cptr->SetPySyncDict(pyKey, pyValue);
		Py_RETURN_NONE;
	}

	PyObject* GetPySyncDict(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->GetPySyncDict();
	}

	PyObject* AfterChange(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->AfterChange();
		Py_RETURN_NONE;
	}

	PyObject* Destroy(PyNPCObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		NPCMgr::Instance()->DestroyNPC(self->cptr->GetNPCID());
		Py_RETURN_NONE;
	}

	static PyMethodDef PyNPC_Methods[] = {
		{"GetNPCID", (PyCFunction)GetNPCID, METH_NOARGS, "NPCID  "},
		{"GetNPCName", (PyCFunction)GetNPCName, METH_NOARGS, "NPC名字  "},
		{"GetNPCType", (PyCFunction)GetNPCType, METH_NOARGS, "获取NPC类型  "},
		{"GetPos", (PyCFunction)GetPos, METH_NOARGS, "获取NPC坐标  "},
		{"SetPyDict", (PyCFunction)SetPyDict, METH_VARARGS, "设置NPCpython字典  "},
		{"GetPyDict", (PyCFunction)GetPyDict, METH_NOARGS, "获取NPCpython字典  "},
		{"SetPySyncDict", (PyCFunction)SetPySyncDict, METH_VARARGS, "设置NPCpython同步客户端的字典  "},
		{"GetPySyncDict", (PyCFunction)GetPySyncDict, METH_NOARGS, "获取NPCpython同步客户端的字典  "},
		{"AfterChange", (PyCFunction)AfterChange, METH_NOARGS, "NPC发生了改变，再次同步周围的客户端  "},
		{"Destroy", (PyCFunction)Destroy, METH_NOARGS, "NPC删除接口  "},
		{ NULL },
	};

	PyDoc_STRVAR(PyNPC_Doc, "PyNPC_Doc/nPyNPC Object");

	PyTypeObject PyNPCType = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"PyNPC",
		sizeof(PyNPCObject),
		0,
		(destructor)PyNPC_Dealloc,					/* tp_dealloc */
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
		PyNPC_Doc,									/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		PyNPC_Methods,								/* tp_methods */
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

	void PyNPC_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());

		PyType_Ready(&PyNPCType);
		// 根据模块名，查找模块并加入到模块身上
		GEPython::Object spModule = PyImport_ImportModule("cComplexServer");
		if (spModule.PyHasExcept())
		{
			spModule.PyPrintAndClearExcept();
		}
		else
		{
			PyModule_AddObject(spModule.GetObj_BorrowRef(), "cNPC", (PyObject*)&PyNPCType);
		}
	}

	PyNPCObject* PyNPC_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &PyNPCType)
		{
			return (PyNPCObject*)pObj;
		}
		return NULL;
	}

	PyNPCObject* PyNPC_New( NPC* pNPC )
	{
		PyNPCObject* obj = PyObject_NEW(PyNPCObject, &PyNPCType);
		obj->cptr = pNPC;
		return obj;
	}

	void PyNPC_Del( PyObject* pObj )
	{
		if (pObj->ob_type != &PyNPCType)
		{
			GE_EXC<<"del obj error "<<__FUNCTION__<<GE_END;
			return;
		}
		PyNPCObject* pPO = (PyNPCObject*)(pObj);
		pPO->cptr = NULL;
	}
}

