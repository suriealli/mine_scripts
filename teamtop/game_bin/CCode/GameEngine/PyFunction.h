/************************************************************************
Python函数管理相关模块
************************************************************************/
#pragma once
#include <vector>
#include <queue>
#include <boost/thread/mutex.hpp>
#include "GEPython.h"

/*
Python 函数回调注册
*/
class PyFunctionCall_Vector
{
	GE_DISABLE_BOJ_CPY(PyFunctionCall_Vector);
	typedef std::vector<PyObject*>			FunctionVector;
public:
	PyFunctionCall_Vector();
	~PyFunctionCall_Vector();

public:
	void					AppendFunction(PyObject* pyFun_BorrowRef, GE::Int32 idx = -1);
	void					RemoveFunction(PyObject* pyFun_BorrowRef);
	void					CallFunctions();

private:
	FunctionVector			m_FunctionVector;
	/*
	注意，m_bIsCallState用于保证在触发回调函数的时候不会该变vector容器
	*/
	bool					m_bIsCallState;
};

