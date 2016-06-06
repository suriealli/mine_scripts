/*我是UTF8无签名编码 */
#include "PyFunction.h"
#include "GEIO.h"

PyFunctionCall_Vector::PyFunctionCall_Vector()
	: m_bIsCallState(false)
{

}

PyFunctionCall_Vector::~PyFunctionCall_Vector()
{
	FunctionVector::iterator iter = this->m_FunctionVector.begin();
	for(; iter != this->m_FunctionVector.end(); ++iter)
	{
		Py_DECREF(*iter);
	}
	this->m_FunctionVector.clear();
}

void PyFunctionCall_Vector::AppendFunction( PyObject* pyFun_BorrowRef, GE::Int32 idx /*= -1*/ )
{
	if (this->m_bIsCallState)
	{
		GE_EXC<<"PyFunctionCall_Vector in call state can't append function."<<GE_END;
		return;
	}
	/*
	Determine if the object o is callable. Return 1 if the object is callable and 0 otherwise.
	*/
	if (0 == PyCallable_Check(pyFun_BorrowRef))
	{
		GE_EXC<<"PyFunctionCall_Vector append a un callable object"<<GE_END;
		return;
	}
	// 保存了引用，增加计数
	Py_INCREF(pyFun_BorrowRef);
	// 指定了位置，尝试插入之
	if (idx >= 0)
	{
		GE::Int32 pos = 0;
		FunctionVector::iterator iter = this->m_FunctionVector.begin();
		for(; iter != this->m_FunctionVector.end(); ++iter)
		{
			if (pos == idx)
			{
				this->m_FunctionVector.insert(iter, pyFun_BorrowRef);
				return;
			}
			++pos;
		}
	}
	// 追加之
	this->m_FunctionVector.push_back(pyFun_BorrowRef);
}

void PyFunctionCall_Vector::RemoveFunction( PyObject* pyFun_BorrowRef )
{
	if (this->m_bIsCallState)
	{
		GE_EXC<<"PyFunctionCall_Vector in call state can't remove function."<<GE_END;
		return;
	}
	FunctionVector::iterator iter = this->m_FunctionVector.begin();
	for(; iter != this->m_FunctionVector.end(); ++iter)
	{
		if (*iter == pyFun_BorrowRef)
		{
			// 释放引用，减少计数
			Py_DECREF(*iter);
			this->m_FunctionVector.erase(iter);
			return;
		}
	}
}

void PyFunctionCall_Vector::CallFunctions()
{
	this->m_bIsCallState = true;
	FunctionVector::iterator iter = this->m_FunctionVector.begin();
	while(iter != this->m_FunctionVector.end())
	{
		/*
		Return value: New reference.
		Call a callable Python object callable_object, with arguments given by the tuple args.
		If no arguments are needed, then args may be NULL. Returns the result of the call on success, or NULL on failure.
		*/
		PyObject* pyResult_NewRef = PyObject_CallObject(*iter, NULL);
		// 如果发生的Python异常，要移除这个时间回调函数
		if (NULL == pyResult_NewRef)
		{
			PyErr_Print();
		}
		else
		{
			Py_DECREF(pyResult_NewRef);
		}
		++iter;
		
	}
	this->m_bIsCallState = false;
}

