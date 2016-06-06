/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "../GameEngine/GEPython.h"

class SingleMirrorScene;

namespace ServerPython
{
	struct PySingleMirrorSceneObject
	{
		PyObject_HEAD;
		SingleMirrorScene*				cptr;
	};

	void							PySingleMirrorScene_Init(void);
	PySingleMirrorSceneObject*		PySingleMirrorScene_FromObj(PyObject* pObj);
	PySingleMirrorSceneObject*		PySingleMirrorScene_New(SingleMirrorScene* pScene);
	void							PySingleMirrorScene_Del(PyObject* pObj);
}

