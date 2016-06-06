/*××的Python接口*/
#include "PyScriptMgr.h"
#include "ScriptMgr.h"
//////////////////////////////////////////////////////////////////////////
// PyScriptMgr模块
//////////////////////////////////////////////////////////////////////////
namespace ServerPython
{

	PyObject* AllotFlagIndex(PyObject* self, PyObject* arg)
	{
		return GEPython::PyObjFromUI32(ScriptMgr::Instance()->AllotFlagIndex());
	}

	PyObject* DirtyFlag(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= MAX_FLAG_SIZE)
		{
			PY_PARAM_ERROR("index out of range.");
		}
		ScriptMgr::Instance()->DirtyFlag(uIdx);
		Py_RETURN_NONE;
	}

	PyObject* SetClearFun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pyCallable = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pyCallable))
		{
			return NULL;
		}
		if (uIdx >= MAX_FLAG_SIZE)
		{
			PY_PARAM_ERROR("index out of range.");
		}
		ScriptMgr::Instance()->SetClearFun(uIdx, pyCallable);
		Py_RETURN_NONE;
	}

	// PyScriptMgr_Methods[]
	static PyMethodDef PyScriptMgr_Methods[] = {
		{ "AllotFlagIndex", AllotFlagIndex, METH_NOARGS, "分配一个标识标识 " },
		{ "DirtyFlag", DirtyFlag, METH_O, "弄脏一个标识 " },
		{ "SetClearFun", SetClearFun, METH_VARARGS, "设置清理一个标识的函数 " },
		{ NULL }
	};

	// PyScriptMgr_Init
	void PyScriptMgr_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* pScriptMgr = Py_InitModule("cScriptMgr", PyScriptMgr_Methods);
		if (NULL == pScriptMgr)
		{
			PyErr_Print();
		}
	}
}

