/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "../GameEngine/GEPython.h"

class PublicScene;

namespace ServerPython
{
	struct PyPublicSceneObject
	{
		PyObject_HEAD;
		PublicScene*				cptr;
	};

	void							PyPublicScene_Init(void);
	PyPublicSceneObject*			PyPublicScene_FromObj(PyObject* pObj);
	PyPublicSceneObject*			PyPublicScene_New(PublicScene* pPublicScene);
	void							PyPublicScene_Del(PyObject* pObj);
}

