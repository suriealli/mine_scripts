/*我是UTF8无签名编码 */
#include "ScriptMgr.h"

ScriptMgr::ScriptMgr()
	: m_nMaxIdx(-1)
	, m_pyObjVector(MAX_FLAG_SIZE)
	, m_FlagVector(MAX_FLAG_SIZE, false)
{
	
}

ScriptMgr::~ScriptMgr()
{

}

void ScriptMgr::StackWarn( const char* pWarn /*= NULL*/ )
{
	if (NULL == pWarn)
	{
		this->m_pyTraceback.Call();
	}
	else
	{
		this->m_pyTraceback.Call("(s)", pWarn);
	}
}

GE::Uint16 ScriptMgr::AllotFlagIndex()
{
	++m_nMaxIdx;
	if (this->m_nMaxIdx < MAX_FLAG_SIZE)
	{
		return static_cast<GE::Uint16>(this->m_nMaxIdx);
	}
	else
	{
		return MAX_FLAG_SIZE;
	}
}

void ScriptMgr::DirtyFlag( GE::Uint16 uIdx )
{
	this->m_FlagVector.at(uIdx) = true;
}

void ScriptMgr::SetClearFun( GE::Uint16 uIdx, PyObject* callable_BorrowRef )
{
	this->m_pyObjVector.at(uIdx).SetObj_BorrowRef(callable_BorrowRef);
}

void ScriptMgr::CallPerSecond()
{
	for (GE::Int16 idx = 0; idx <= this->m_nMaxIdx; ++idx)
	{
		if (this->m_FlagVector.at(idx))
		{
			/*
			Return value: New reference.
			Call a callable Python object callable, with a variable number of PyObject* arguments. The arguments are provided as a variable number of parameters followed by NULL.
			Returns the result of the call on success, or NULL on failure.
			*/
			PyObject* pyResult_NewRef = PyObject_CallFunctionObjArgs(this->m_pyObjVector.at(idx).GetObj_BorrowRef(), NULL);
			if (NULL == pyResult_NewRef)
			{
				PyErr_Print();
			}
			else
			{
				Py_DECREF(pyResult_NewRef);
			}
			this->m_FlagVector.at(idx) = false;
		}
	}
}

void ScriptMgr::LoadPyData()
{
	this->m_pyTraceback.Load("Util.Trace", "StackWarn");
	this->m_pyDebugOnDistriubte.Load("Game.Role.Debug", "OnDistribute");
	this->m_pyDebugDoSendObj.Load("Game.Role.Debug", "DoSendObj");
	this->m_pyDebugOnCallback.Load("Game.Role.Debug", "OnCallback");
	this->m_pyDebugDoCallback.Load("Game.Role.Debug", "DoCallback");
	this->m_pyWatchRoleDistribute.Load("Game.Role.Debug", "WatchRole");
}

