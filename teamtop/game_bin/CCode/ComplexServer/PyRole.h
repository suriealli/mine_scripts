/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "../GameEngine/GEPython.h"

class Role;

namespace ServerPython
{
	struct PyRoleObject
	{
		PyObject_HEAD;
		Role*				cptr;
		/*
		缓存角色ID，因为有些时候还是要拿到离线玩家的角色ID
		是引用
		*/
		PyObject*			role_id;
		//int					block[10240000];
	};

	void					PyRole_Init(void);
	PyRoleObject*			PyRole_FromObj(PyObject* pObj);
	PyRoleObject*			PyRole_New(Role* pRole);
	void					PyRole_Del(PyObject* pObj);
}

