/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "../GameEngine/GEPython.h"

class MultiMirrorScene;

namespace ServerPython
{
	struct PyMultiMirrorSceneObject
	{
		PyObject_HEAD;
		MultiMirrorScene*				cptr;
	};

	void							PyMultiMirrorScene_Init(void);
	PyMultiMirrorSceneObject*		PyMultiMirrorScene_FromObj(PyObject* pObj);
	PyMultiMirrorSceneObject*		PyMultiMirrorScene_New(MultiMirrorScene* pScene);
	void							PyMultiMirrorScene_Del(PyObject* pObj);
}

