/*RoleDataMgr的Python接口*/
#include "PyRoleDataMgr.h"
#include "RoleDataMgr.h"
#include "ComplexServer.h"
//////////////////////////////////////////////////////////////////////////
// PyRoleDataMgr模块
//////////////////////////////////////////////////////////////////////////
namespace ServerPython
{
	PyObject* SetInt64Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|LHLHOO", &uIdx, &DR.nMinValue, &DR.nMinAction, &DR.nMaxValue, &DR.nMaxAction, &pySyncClient, &pyLogEvent))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetInt64Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetInt64Rule(uIdx, DR);
		Py_RETURN_NONE;
	}
	
	PyObject* SetDisperseInt32Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|LHLHOO", &uIdx,  &DR.nMinValue, &DR.nMinAction, &DR.nMaxValue, &DR.nMaxAction, &pySyncClient, &pyLogEvent))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetDisperseInt32Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetDisperseInt32Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetInt32Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|LHLHOO", &uIdx, &DR.nMinValue, &DR.nMinAction, &DR.nMaxValue, &DR.nMaxAction, &pySyncClient, &pyLogEvent))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetInt32Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetInt32Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetInt16Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|LHLHOO", &uIdx, &DR.nMinValue, &DR.nMinAction, &DR.nMaxValue, &DR.nMaxAction, &pySyncClient, &pyLogEvent))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetInt16Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetInt16Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetInt8Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|LHLHOO", &uIdx, &DR.nMinValue, &DR.nMinAction, &DR.nMaxValue, &DR.nMaxAction, &pySyncClient, &pyLogEvent))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetInt8Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetInt8Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetDayInt8Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|LHLHOO", &uIdx, &DR.nMinValue, &DR.nMinAction, &DR.nMaxValue, &DR.nMaxAction, &pySyncClient, &pyLogEvent))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetDayInt8Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetDayInt8Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetInt1Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|OO", &uIdx, &pySyncClient, &pyLogEvent))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetInt1Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetInt1Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetDayInt1Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|OO", &uIdx, &pySyncClient, &pyLogEvent))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetDayInt1Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetDayInt1Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetDynamicInt64Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		PyObject* pyLogEvent = Py_False;
		if (!PyArg_ParseTuple(arg, "H|LHLHOOI", &uIdx, &DR.nMinValue, &DR.nMinAction, &DR.nMaxValue, &DR.nMaxAction, &pySyncClient, &pyLogEvent, &DR.uOverTime))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetDynamicInt64Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		DR.bLogEvent = static_cast<GE::Uint8>(PyObject_IsTrue(pyLogEvent));
		RoleDataMgr::Instance()->SetDynamicInt64Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetFlagRule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		if (!PyArg_ParseTuple(arg, "H", &uIdx))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetFlagRule(uIdx).uCoding;
		RoleDataMgr::Instance()->SetFlagRule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetTempInt64Rule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		if (!PyArg_ParseTuple(arg, "H|LHLHO", &uIdx, &DR.nMinValue, &DR.nMinAction, &DR.nMaxValue, &DR.nMaxAction, &pySyncClient))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetTempInt64Rule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		RoleDataMgr::Instance()->SetTempInt64Rule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetCDRule(PyObject* self, PyObject* arg)
	{
		DataRule DR;
		GE::Uint16 uIdx = 0;
		PyObject* pySyncClient = Py_False;
		if (!PyArg_ParseTuple(arg, "H|O", &uIdx, &pySyncClient))
		{
			return NULL;
		}
		DR.uCoding = RoleDataMgr::Instance()->GetCDRule(uIdx).uCoding;
		DR.bSyncClient = static_cast<GE::Uint8>(PyObject_IsTrue(pySyncClient));
		RoleDataMgr::Instance()->SetCDRule(uIdx, DR);
		Py_RETURN_NONE;
	}

	PyObject* SetInt64Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif

		RoleDataMgr::Instance()->GetInt64Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetDisperseInt32Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif

		RoleDataMgr::Instance()->GetDisperseInt32Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetInt32Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif

		RoleDataMgr::Instance()->GetInt32Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetInt16Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif

		RoleDataMgr::Instance()->GetInt16Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetInt8Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif
		RoleDataMgr::Instance()->GetInt8Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetDayInt8Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif
		RoleDataMgr::Instance()->GetDayInt8Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetInt1Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif
		RoleDataMgr::Instance()->GetInt1Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetDayInt1Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif
		RoleDataMgr::Instance()->GetDayInt1Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetDynamicInt64Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif
		RoleDataMgr::Instance()->GetDynamicInt64Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetFlagFun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif
		RoleDataMgr::Instance()->GetFlagRule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetTempInt64Fun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif
		RoleDataMgr::Instance()->GetTempInt64Rule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}

	PyObject* SetCDFun(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uIdx = 0;
		PyObject* pFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pFun))
		{
			return NULL;
		}
#ifdef WIN
		GE_WARN(PyCallable_Check(pFun));
#endif
		RoleDataMgr::Instance()->GetCDRule(uIdx).SetChangeFun(pFun);
		Py_RETURN_NONE;
	}



	// PyRoleDataMgr_Methods[]
	static PyMethodDef PyRoleDataMgr_Methods[] = {
		{ "SetInt64Rule", SetInt64Rule, METH_VARARGS, "设置角色Int64数组的规则 "},
		{ "SetDisperseInt32Rule", SetDisperseInt32Rule, METH_VARARGS, "设置角色DisperseInt32数组的规则 "},
		{ "SetInt32Rule", SetInt32Rule, METH_VARARGS, "设置角色Int32数组的规则 "},
		{ "SetInt16Rule", SetInt16Rule, METH_VARARGS, "设置角色Int16数组的规则 "},
		{ "SetInt8Rule", SetInt8Rule, METH_VARARGS, "设置角色Int8数组的规则 "},
		{ "SetDayInt8Rule", SetDayInt8Rule, METH_VARARGS, "设置角色DayInt8数组的规则 "},
		{ "SetInt1Rule", SetInt1Rule, METH_VARARGS, "设置角色Int1数组的规则 "},
		{ "SetDayInt1Rule", SetDayInt1Rule, METH_VARARGS, "设置角色DayInt8数组的规则 "},
		{ "SetDynamicInt64Rule", SetDynamicInt64Rule, METH_VARARGS, "设置角色DynamicInt64数组的规则 "},
		{ "SetFlagRule", SetFlagRule, METH_VARARGS, "设置角色Python对象版本号数组的规则 "},
		{ "SetTempInt64Rule", SetTempInt64Rule, METH_VARARGS, "设置角色Tempnt64数组的规则 "},
		{ "SetCDRule", SetCDRule, METH_VARARGS, "设置角色CD数组的规则 "},
		{ "SetInt64Fun", SetInt64Fun, METH_VARARGS, "设置角色Int64数组的回调函数 "},
		{ "SetDisperseInt32Fun", SetDisperseInt32Fun, METH_VARARGS, "设置角色DisperseInt32数组的回调函数 "},
		{ "SetInt32Fun", SetInt32Fun, METH_VARARGS, "设置角色Int32数组的回调函数 "},
		{ "SetInt16Fun", SetInt16Fun, METH_VARARGS, "设置角色Int16数组的回调函数 "},
		{ "SetInt8Fun", SetInt8Fun, METH_VARARGS, "设置角色Int8数组的回调函数 "},
		{ "SetDayInt8Fun", SetDayInt8Fun, METH_VARARGS, "设置角色DayInt8数组的回调函数 "},
		{ "SetInt1Fun", SetInt1Fun, METH_VARARGS, "设置角色Int1数组的回调函数 "},
		{ "SetDayInt1Fun", SetDayInt1Fun, METH_VARARGS, "设置角色DayInt1数组的回调函数 "},
		{ "SetDynamicInt64Fun", SetDynamicInt64Fun, METH_VARARGS, "设置角色DynamicInt64数组的回调函数 "},
		{ "SetFlagFun", SetFlagFun, METH_VARARGS, "设置角色Flag数组的回调函数 "},
		{ "SetTempInt64Fun", SetTempInt64Fun, METH_VARARGS, "设置角色TempInt64数组的回调函数 "},
		{ "SetCDFun", SetCDFun, METH_VARARGS, "设置角色CD数组的回调函数 "},

		{ NULL }
	};

	// PyRoleDataMgr_Init
	void PyRoleDataMgr_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* pRoleDataMgr = Py_InitModule("cRoleDataMgr", PyRoleDataMgr_Methods);
		if (NULL == pRoleDataMgr)
		{
			PyErr_Print();
		}
	}
}

