/*××的Python接口*/
#include "PyLogTransaction.h"
#include "LogTransaction.h"
//////////////////////////////////////////////////////////////////////////
// PyLogTransaction模块
//////////////////////////////////////////////////////////////////////////
namespace ServerPython
{
	PyObject* StartTransaction(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uTransaction = 0;
		if (!GEPython::PyObjToUI16(arg, uTransaction))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		LogTransaction::Instance()->StartTransaction(uTransaction);
		Py_RETURN_NONE;
	}

	PyObject* EndTransaction(PyObject* self, PyObject* arg)
	{
		LogTransaction::Instance()->EndTransaction();
		Py_RETURN_NONE;
	}

	PyObject* HasTransaction(PyObject* self, PyObject* arg)
	{
		PY_RETURN_BOOL(LogTransaction::Instance()->HasTransaction());
	}

	PyObject* GetTransaction(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uTransaction = 0;
		GE::Int64 nLogID = 0;
		LogTransaction::Instance()->GetTransaction(uTransaction, nLogID);
		return Py_BuildValue("HL", uTransaction, nLogID);
	}

	PyObject* GetTransactionForEvent(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uTransaction = 0;
		GE::Int64 nLogID = 0;
		LogTransaction::Instance()->GetTransactionForEvent(uTransaction, nLogID);
		return Py_BuildValue("HL", uTransaction, nLogID);
	}

	PyObject* GetEvent(PyObject* self, PyObject* arg)
	{
		return GEPython::PyObjFromUI32(LogTransaction::Instance()->GetEvent());
	}

	// PyLogTransaction_Methods[]
	static PyMethodDef PyLogTransaction_Methods[] = {
		{"StartTransaction", (PyCFunction)StartTransaction, METH_O, "开启事务  "},
		{"EndTransaction", (PyCFunction)EndTransaction, METH_NOARGS, "关闭事务  "},
		{"HasTransaction", (PyCFunction)HasTransaction, METH_NOARGS, "是否有事务  "},
		{"GetTransaction", (PyCFunction)GetTransaction, METH_NOARGS, "获取事务  "},
		{"GetTransactionForEvent", (PyCFunction)GetTransactionForEvent, METH_NOARGS, "为事件获取事务  "},
		{"GetEvent", (PyCFunction)GetEvent, METH_NOARGS, "获取事件  "},
		{ NULL }
	};

	// PyLogTransaction_Init
	void PyLogTransaction_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* pLogTransaction = Py_InitModule("cLogTransaction", PyLogTransaction_Methods);
		if (NULL == pLogTransaction)
		{
			PyErr_Print();
		}
	}
}

