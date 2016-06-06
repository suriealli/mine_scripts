/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "../GameEngine/GEPython.h"

class NPC;

namespace ServerPython
{
	struct PyNPCObject
	{
		PyObject_HEAD;
		NPC*				cptr;
	};

	void							PyNPC_Init(void);
	PyNPCObject*					PyNPC_FromObj(PyObject* pObj);
	PyNPCObject*					PyNPC_New(NPC* pNPC);
	void							PyNPC_Del(PyObject* pObj);
}

