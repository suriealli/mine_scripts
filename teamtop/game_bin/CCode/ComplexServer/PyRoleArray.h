/************************************************************************
角色数组Python接口
************************************************************************/
#pragma once
#include "PyRole.h"

#define RoleArray_Methods \
	{"InitI64", (PyCFunction)InitI64, METH_O, "初始化I64数组   "},	\
	{"SeriI64", (PyCFunction)SeriI64, METH_NOARGS, "序列化I64数组   "},	\
	{"GetI64", (PyCFunction)GetI64, METH_O, "获取I64数组值   "},	\
	{"SetI64", (PyCFunction)SetI64, METH_VARARGS, "设置I64数组值   "},	\
	{"IncI64", (PyCFunction)IncI64, METH_VARARGS, "增加I64数组值   "},	\
	{"DecI64", (PyCFunction)DecI64, METH_VARARGS, "减少I64数组值   "},	\
	{"InitDI32", (PyCFunction)InitDI32, METH_O, "初始化DI32数组   "},	\
	{"SeriDI32", (PyCFunction)SeriDI32, METH_NOARGS, "序列化DI32数组   "},	\
	{"GetDI32", (PyCFunction)GetDI32, METH_O, "获取DI32数组值   "},	\
	{"SetDI32", (PyCFunction)SetDI32, METH_VARARGS, "设置DI32数组值   "},	\
	{"IncDI32", (PyCFunction)IncDI32, METH_VARARGS, "增加DI32数组值   "},	\
	{"DecDI32", (PyCFunction)DecDI32, METH_VARARGS, "减少DI32数组值   "},	\
	{"InitI32", (PyCFunction)InitI32, METH_O, "初始化I32数组   "},	\
	{"SeriI32", (PyCFunction)SeriI32, METH_NOARGS, "序列化I32数组   "},	\
	{"GetI32", (PyCFunction)GetI32, METH_O, "获取I32数组值   "},	\
	{"SetI32", (PyCFunction)SetI32, METH_VARARGS, "设置I32数组值   "},	\
	{"IncI32", (PyCFunction)IncI32, METH_VARARGS, "增加I32数组值   "},	\
	{"DecI32", (PyCFunction)DecI32, METH_VARARGS, "减少I32数组值   "},	\
	{"InitI16", (PyCFunction)InitI16, METH_O, "初始化I16数组   "},	\
	{"SeriI16", (PyCFunction)SeriI16, METH_NOARGS, "序列化I16数组   "},	\
	{"GetI16", (PyCFunction)GetI16, METH_O, "获取I16数组值   "},	\
	{"SetI16", (PyCFunction)SetI16, METH_VARARGS, "设置I16数组值   "},	\
	{"IncI16", (PyCFunction)IncI16, METH_VARARGS, "增加I16数组值   "},	\
	{"DecI16", (PyCFunction)DecI16, METH_VARARGS, "减少I16数组值   "},	\
	{"InitI8", (PyCFunction)InitI8, METH_O, "初始化I8数组   "},	\
	{"SeriI8", (PyCFunction)SeriI8, METH_NOARGS, "序列化I8数组   "},	\
	{"GetI8", (PyCFunction)GetI8, METH_O, "获取I8数组值   "},	\
	{"SetI8", (PyCFunction)SetI8, METH_VARARGS, "设置I8数组值   "},	\
	{"IncI8", (PyCFunction)IncI8, METH_VARARGS, "增加I8数组值   "},	\
	{"DecI8", (PyCFunction)DecI8, METH_VARARGS, "减少I8数组值   "},	\
	{"InitDI8", (PyCFunction)InitDI8, METH_O, "初始化DI8数组   "},	\
	{"SeriDI8", (PyCFunction)SeriDI8, METH_NOARGS, "序列化DI8数组   "},	\
	{"GetDI8", (PyCFunction)GetDI8, METH_O, "获取DI8数组值   "},	\
	{"SetDI8", (PyCFunction)SetDI8, METH_VARARGS, "设置DI8数组值   "},	\
	{"IncDI8", (PyCFunction)IncDI8, METH_VARARGS, "增加DI8数组值   "},	\
	{"DecDI8", (PyCFunction)DecDI8, METH_VARARGS, "减少DI8数组值   "},	\
	{"InitI1", (PyCFunction)InitI1, METH_O, "初始化I1数组   "},	\
	{"SeriI1", (PyCFunction)SeriI1, METH_NOARGS, "序列化I1数组   "},	\
	{"GetI1", (PyCFunction)GetI1, METH_O, "获取I1数组值   "},	\
	{"SetI1", (PyCFunction)SetI1, METH_VARARGS, "设置I1数组值   "},	\
	{"InitDI1", (PyCFunction)InitDI1, METH_O, "初始化DI1数组   "},	\
	{"SeriDI1", (PyCFunction)SeriDI1, METH_NOARGS, "序列化DI1数组   "},	\
	{"GetDI1", (PyCFunction)GetDI1, METH_O, "获取DI1数组值   "},	\
	{"SetDI1", (PyCFunction)SetDI1, METH_VARARGS, "设置DI1数组值   "},	\
	{"InitDI64", (PyCFunction)InitDI64, METH_O, "初始化DI64数组   "},	\
	{"SeriDI64", (PyCFunction)SeriDI64, METH_NOARGS, "序列化DI64数组   "},	\
	{"GetDI64", (PyCFunction)GetDI64, METH_O, "获取DI64数组值   "},	\
	{"SetDI64", (PyCFunction)SetDI64, METH_VARARGS, "设置DI64数组值   "},	\
	{"IncDI64", (PyCFunction)IncDI64, METH_VARARGS, "增加DI64数组值   "},	\
	{"DecDI64", (PyCFunction)DecDI64, METH_VARARGS, "减少DI64数组值   "},	\
	{"InitCI8", (PyCFunction)InitCI8, METH_O, "初始化CI8数组   "},	\
	{"SeriCI8", (PyCFunction)SeriCI8, METH_NOARGS, "序列化CI8数组   "},	\
	{"GetCI8", (PyCFunction)GetCI8, METH_O, "获取CI8数组值   "},	\
	{"SetCI8", (PyCFunction)SetCI8, METH_VARARGS, "设置CI8数组值   "},	\
	{"GetTI64", (PyCFunction)GetTI64, METH_O, "获取TI64数组值   "},	\
	{"SetTI64", (PyCFunction)SetTI64, METH_VARARGS, "设置TI64数组值   "},	\
	{"IncTI64", (PyCFunction)IncTI64, METH_VARARGS, "增加TI64数组值   "},	\
	{"DecTI64", (PyCFunction)DecTI64, METH_VARARGS, "减少TI64数组值   "},	\
	{"InitObj", (PyCFunction)InitObj, METH_O, "初始化Obj数组   "},	\
	{"SeriObj", (PyCFunction)SeriObj, METH_NOARGS, "序列化Obj数组   "},	\
	{"GetObj", (PyCFunction)GetObj, METH_O, "获取Obj   "},	\
	{"GetObj_ReadOnly", (PyCFunction)GetObj_ReadOnly, METH_O, "获取Obj（只读）   "},	\
	{"SetObj", (PyCFunction)SetObj, METH_VARARGS, "设置Obj   "},	\
	{"GetObjVersion", (PyCFunction)GetObjVersion, METH_O, "获取Obj版本号   "},	\
	{"InitCD", (PyCFunction)InitCD, METH_O, "初始化TI64数组   "},	\
	{"SeriCD", (PyCFunction)SeriCD, METH_NOARGS, "序列化TI64数组   "},	\
	{"GetCD", (PyCFunction)GetCD, METH_O, "获取CI8数组值   "},	\
	{"SetCD", (PyCFunction)SetCD, METH_VARARGS, "设置CI8数组值   "},	\
	{"GetTempObj", (PyCFunction)GetTempObj, METH_O, "获取TempObj数组值   "},	\
	{"SetTempObj", (PyCFunction)SetTempObj, METH_VARARGS, "设置TempObj数组值   "},	\

namespace ServerPython
{
	PyObject*  InitI64(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriI64(PyRoleObject* self, PyObject* arg);
	PyObject*  GetI64(PyRoleObject* self, PyObject* arg);
	PyObject*  SetI64(PyRoleObject* self, PyObject* arg);
	PyObject*  IncI64(PyRoleObject* self, PyObject* arg);
	PyObject*  DecI64(PyRoleObject* self, PyObject* arg);

	PyObject*  InitDI32(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriDI32(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDI32(PyRoleObject* self, PyObject* arg);
	PyObject*  SetDI32(PyRoleObject* self, PyObject* arg);
	PyObject*  IncDI32(PyRoleObject* self, PyObject* arg);
	PyObject*  DecDI32(PyRoleObject* self, PyObject* arg);

	PyObject*  InitI32(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriI32(PyRoleObject* self, PyObject* arg);
	PyObject*  GetI32(PyRoleObject* self, PyObject* arg);
	PyObject*  SetI32(PyRoleObject* self, PyObject* arg);
	PyObject*  IncI32(PyRoleObject* self, PyObject* arg);
	PyObject*  DecI32(PyRoleObject* self, PyObject* arg);

	PyObject*  InitI16(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriI16(PyRoleObject* self, PyObject* arg);
	PyObject*  GetI16(PyRoleObject* self, PyObject* arg);
	PyObject*  SetI16(PyRoleObject* self, PyObject* arg);
	PyObject*  IncI16(PyRoleObject* self, PyObject* arg);
	PyObject*  DecI16(PyRoleObject* self, PyObject* arg);

	PyObject*  InitI8(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriI8(PyRoleObject* self, PyObject* arg);
	PyObject*  GetI8(PyRoleObject* self, PyObject* arg);
	PyObject*  SetI8(PyRoleObject* self, PyObject* arg);
	PyObject*  IncI8(PyRoleObject* self, PyObject* arg);
	PyObject*  DecI8(PyRoleObject* self, PyObject* arg);

	PyObject*  InitDI8(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriDI8(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDI8(PyRoleObject* self, PyObject* arg);
	PyObject*  SetDI8(PyRoleObject* self, PyObject* arg);
	PyObject*  IncDI8(PyRoleObject* self, PyObject* arg);
	PyObject*  DecDI8(PyRoleObject* self, PyObject* arg);

	PyObject*  InitI1(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriI1(PyRoleObject* self, PyObject* arg);
	PyObject*  GetI1(PyRoleObject* self, PyObject* arg);
	PyObject*  SetI1(PyRoleObject* self, PyObject* arg);

	PyObject*  InitDI1(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriDI1(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDI1(PyRoleObject* self, PyObject* arg);
	PyObject*  SetDI1(PyRoleObject* self, PyObject* arg);

	PyObject*  InitDI64(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriDI64(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDI64(PyRoleObject* self, PyObject* arg);
	PyObject*  SetDI64(PyRoleObject* self, PyObject* arg);
	PyObject*  IncDI64(PyRoleObject* self, PyObject* arg);
	PyObject*  DecDI64(PyRoleObject* self, PyObject* arg);

	PyObject*  InitCI8(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriCI8(PyRoleObject* self, PyObject* arg);
	PyObject*  GetCI8(PyRoleObject* self, PyObject* arg);
	PyObject*  SetCI8(PyRoleObject* self, PyObject* arg);

	PyObject*  GetTI64(PyRoleObject* self, PyObject* arg);
	PyObject*  SetTI64(PyRoleObject* self, PyObject* arg);
	PyObject*  IncTI64(PyRoleObject* self, PyObject* arg);
	PyObject*  DecTI64(PyRoleObject* self, PyObject* arg);

	PyObject*  InitObj(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriObj(PyRoleObject* self, PyObject* arg);
	PyObject*  GetObj(PyRoleObject* self, PyObject* arg);
	PyObject*  GetObj_ReadOnly(PyRoleObject* self, PyObject* arg);
	PyObject*  SetObj(PyRoleObject* self, PyObject* arg);
	PyObject*  GetObjVersion(PyRoleObject* self, PyObject* arg);

	PyObject*  InitCD(PyRoleObject* self, PyObject* arg);
	PyObject*  SeriCD(PyRoleObject* self, PyObject* arg);
	PyObject*  GetCD(PyRoleObject* self, PyObject* arg);
	PyObject*  SetCD(PyRoleObject* self, PyObject* arg);

	PyObject*  GetTempObj(PyRoleObject* self, PyObject* arg);
	PyObject*  SetTempObj(PyRoleObject* self, PyObject* arg);
}

