#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 构建C写的Python普通类
#===============================================================================
import DynamicPath

ComplexServerFolder = DynamicPath.DynamicFolder(DynamicPath.CFloderPath)
ComplexServerFolder.AppendPath("ComplexServer")

H = '''/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "../GameEngine/GEPython.h"

namespace %(namespace)s
{
	struct Py%(classname)sObject
	{
		PyObject_HEAD;
		%(classname)s*				cptr;
	};

	void						Py%(classname)s_Init(void);
	Py%(classname)sObject*			Py%(classname)s_FromObj(PyObject* pObj);
}'''

CPP = '''/*我是UTF8编码文件*/
#include "Py%(classname)s.h"

namespace %(namespace)s
{
	void Py%(classname)s_Dealloc(Py%(classname)sObject* self)
	{
		//TODO
		PyObject_Del(self);
	}

	int Py%(classname)s_init(Py%(classname)sObject* self, PyObject* args, PyObject* kw)
	{
		if (!true)
		{
			return -1;
		}
		return 1;
	}

	static PyMethodDef Py%(classname)s_Methods[] = {
		{ NULL },
	};

	PyDoc_STRVAR(Py%(classname)s_Doc, "Py%(classname)s_Doc/nPy%(classname)s Object");

	PyTypeObject Py%(classname)sType = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"Py%(classname)s",
		sizeof(Py%(classname)sObject),
		0,
		(destructor)Py%(classname)s_Dealloc,		/* tp_dealloc */
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
		Py_TPFLAGS_HAVE_CLASS,						/* tp_flags */
		Py%(classname)s_Doc,						/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		Py%(classname)s_Methods,					/* tp_methods */
		0,											/* tp_members */
		0,											/* tp_getset */
		0,											/* tp_base */
		0,											/* tp_dict */
		0,											/* tp_descr_get */
		0,											/* tp_descr_set */
		0,											/* tp_dictoffset */
		(initproc)Py%(classname)s_init,				/* tp_init */
		PyType_GenericAlloc,						/* tp_alloc */
		PyType_GenericNew,							/* tp_new */
		0,											/* tp_free */
	};

	void Py%(classname)s_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());

		PyType_Ready(&Py%(classname)sType);
		// 根据模块名，查找模块并加入到模块身上
		GEPython::Object spModule = PyImport_ImportModule("cComplexServer");
		if (spModule.PyHasExcept())
		{
			spModule.PyPrintAndClearExcept();
		}
		else
		{
			PyModule_AddObject(spModule.GetObj_BorrowRef(), "c%(classname)s", (PyObject*)&Py%(classname)sType);
		}
	}

	Py%(classname)sObject* Py%(classname)s_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &Py%(classname)sType)
		{
			return (Py%(classname)sObject*)pObj;
		}
		return NULL;
	}
}
'''

def BuildCClass(namespace, modulename, classname):
	d = {"namespace": namespace, "modulename": modulename, "classname": classname}
	with open(ComplexServerFolder.FilePath("Py%(classname)s.h" % d), "w") as fh:
		fh.write(H % d)
	with open(ComplexServerFolder.FilePath("Py%(classname)s.cpp" % d), "w") as fcpp:
		fcpp.write(CPP % d)
	print "--> Build", namespace, modulename, classname

if __name__ == "__main__":
	BuildCClass("ServerPython", "cComplexServer", "")

