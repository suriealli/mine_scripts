/************************************************************************
实现Tick系统的Python接口
************************************************************************/
#pragma once
#include "GEPython.h"

class GETick;
class GESmallTick;

namespace GEPython
{
	struct PyTickObject
	{
		PyObject_HEAD;
		GETick*			cptr;
	};

	struct PySmallTickObject
	{
		PyObject_HEAD;
		GESmallTick*	cptr;
	};

	PyTickObject*		PyTick_FromObj( PyObject* pObj );
	PyTickObject*		PyTick_New(GETick* pCPtr);
	void				PyTick_Del(PyObject* pObj);
	void				PyTick_Init( void );

	PySmallTickObject*	PySmallTick_FromObj( PyObject* pObj );
	PySmallTickObject*	PySmallTick_New(GESmallTick* pCPtr);
	void				PySmallTick_Del(PyObject* pObj);
	void				PySmallTick_Init( void );
}

