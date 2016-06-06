#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 构建C写的Python模块
#===============================================================================
import DynamicPath

ComplexServerFolder = DynamicPath.DynamicFolder(DynamicPath.CFloderPath)
ComplexServerFolder.AppendPath("ComplexServer")

H = '''/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once

namespace %(namespace)s
{
	void				Py%(modulename)s_Init(void);
}

'''

CPP = '''/*××的Python接口*/
#include "Py%(modulename)s.h"
#include "%(modulename)s.h"
//////////////////////////////////////////////////////////////////////////
// Py%(modulename)s模块
//////////////////////////////////////////////////////////////////////////
namespace %(namespace)s
{
	// Py%(modulename)s_Methods[]
	static PyMethodDef Py%(modulename)s_Methods[] = {
		{ NULL }
	};

	// Py%(modulename)s_Init
	void Py%(modulename)s_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* p%(modulename)s = Py_InitModule("c%(modulename)s", Py%(modulename)s_Methods);
		if (NULL == p%(modulename)s)
		{
			PyErr_Print();
		}
	}
}

'''

def BuildCModule(namespace, modulename):
	d = {"namespace": namespace, "modulename": modulename}
	with open(ComplexServerFolder.FilePath("Py%(modulename)s.h" % d), "w") as fh:
		fh.write(H % d)
	with open(ComplexServerFolder.FilePath("Py%(modulename)s.cpp" % d), "w") as fcpp:
		fcpp.write(CPP % d)
	print "--> Build", namespace, modulename

if __name__ == "__main__":
	BuildCModule("ServerPython", "ScriptMgr")
	

