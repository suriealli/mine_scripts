/************************************************************************
限时数据的Python接口
************************************************************************/
#pragma once
#include "GEPython.h"

class GETimeData;

namespace GEPython
{
	struct PyTimeDataObject
	{
		PyObject_HEAD;
		GETimeData*			cptr;
	};

	PyTimeDataObject*		PyTimeData_FromObj( PyObject* pObj );
	PyTimeDataObject*		PyTimeData_New(GETimeData* pCPtr);
	void					PyTimeData_Del(PyObject* pObj);
	void					PyTimeData_Init( void );
}

