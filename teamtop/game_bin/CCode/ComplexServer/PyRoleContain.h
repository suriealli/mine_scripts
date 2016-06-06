/************************************************************************
角色数组Python接口
************************************************************************/
#pragma once
#include "PyRole.h"

#define RoleContain_Methods \
	{"SetCareer", (PyCFunction)SetCareer, METH_O, "设置角色职业   "},	\
	{"GetCareer", (PyCFunction)GetCareer, METH_NOARGS, "获取角色职业   "},	\
	{"SetFly", (PyCFunction)SetFly, METH_O, "设置角色飞行状态走路状态   "},	\
	{"IsFlying", (PyCFunction)IsFlying, METH_NOARGS, "获取角色飞行允许状态走路状态   "},	\
	{"IncTiLi", (PyCFunction)IncTiLi, METH_O, "增加体力   "},	\
	{"DecTiLi", (PyCFunction)DecTiLi, METH_O, "减少体力   "},	\
	{"SetTiLi", (PyCFunction)SetTiLi, METH_O, "设置体力   "},	\
	{"GetTiLi", (PyCFunction)GetTiLi, METH_NOARGS, "获取体力   "},	\
	{"GetNowSpeed", (PyCFunction)GetNowSpeed, METH_NOARGS, "获取当前移动速度   "},	\
	{"SetMoveSpeed", (PyCFunction)SetMoveSpeed, METH_O, "设置移动速度   "},	\
	{"GetMoveSpeed", (PyCFunction)GetMoveSpeed, METH_NOARGS, "获取移动速度   "},	\
	{"SetMountSpeed", (PyCFunction)SetMountSpeed, METH_O, "设置坐骑移动速度   "},	\
	{"GetMountSpeed", (PyCFunction)GetMountSpeed, METH_NOARGS, "获取坐骑移动速度   "},	\
	{"SetTempSpeed", (PyCFunction)SetTempSpeed, METH_O, "设置临时移动速度   "},	\
	{"GetTempSpeed", (PyCFunction)GetTempSpeed, METH_NOARGS, "获取临时移动速度   "},	\
	{"SetTempFly", (PyCFunction)SetTempFly, METH_O, "设置临时移动速度   "},	\
	{"GetTempFly", (PyCFunction)GetTempFly, METH_NOARGS, "获取临时飞行状态   "},	\
	{"CancleTempFly", (PyCFunction)CancleTempFly, METH_NOARGS, "取消临时飞行   "},	\
	{"CancleTempSpeed", (PyCFunction)CancleTempSpeed, METH_NOARGS, "取消临时移动速度   "},	\
	{"SetAppStatus", (PyCFunction)SetAppStatus, METH_O, "设置角色外观状态   "},	\
	{"GetAppStatus", (PyCFunction)GetAppStatus, METH_NOARGS, "获取角色外观状态   "},	\
	{"MustFlying", (PyCFunction)MustFlying, METH_NOARGS, "当前所在点是否必须飞行才可以移动   "},	\
	{"GetRoleSyncAppearanceObj", (PyCFunction)GetRoleSyncAppearanceObj, METH_NOARGS, "获取角色的外观打包数据   "},	\
	{"SetQQHZ", (PyCFunction)SetQQHZ, METH_O, "设置黄钻等级   "},	\
	{"GetQQHZ", (PyCFunction)GetQQHZ, METH_NOARGS, "获取黄钻等级   "},	\
	{"SetQQYHZ", (PyCFunction)SetQQYHZ, METH_O, "设置年费黄钻   "},	\
	{"GetQQYHZ", (PyCFunction)GetQQYHZ, METH_NOARGS, "获取年费黄钻   "},	\
	{"SetQQHHHZ", (PyCFunction)SetQQHHHZ, METH_O, "设置豪华黄钻   "},	\
	{"GetQQHHHZ", (PyCFunction)GetQQHHHZ, METH_NOARGS, "获取豪华黄钻   "},	\
	{"SetQQLZ", (PyCFunction)SetQQLZ, METH_O, "设置蓝钻等级   "},	\
	{"GetQQLZ", (PyCFunction)GetQQLZ, METH_NOARGS, "获取蓝钻等级   "},	\
	{"SetQQYLZ", (PyCFunction)SetQQYLZ, METH_O, "设置年费蓝钻   "},	\
	{"GetQQYLZ", (PyCFunction)GetQQYLZ, METH_NOARGS, "获取年费蓝钻   "},	\
	{"SetQQHHLZ", (PyCFunction)SetQQHHLZ, METH_O, "设置豪华蓝钻   "},	\
	{"GetQQHHLZ", (PyCFunction)GetQQHHLZ, METH_NOARGS, "获取豪华蓝钻   "},	\

namespace ServerPython
{
	PyObject*  SetCareer(PyRoleObject* self, PyObject* arg);
	PyObject*  GetCareer(PyRoleObject* self, PyObject* arg);

	PyObject*  SetFly(PyRoleObject* self, PyObject* arg);
	PyObject*  IsFlying(PyRoleObject* self, PyObject* arg);

	PyObject*  IncTiLi(PyRoleObject* self, PyObject* arg);
	PyObject*  DecTiLi(PyRoleObject* self, PyObject* arg);
	PyObject*  SetTiLi(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTiLi(PyRoleObject* self, PyObject* arg);

	PyObject*  GetNowSpeed(PyRoleObject* self, PyObject* arg);

	PyObject*  SetMoveSpeed(PyRoleObject* self, PyObject* arg);
	PyObject*  GetMoveSpeed(PyRoleObject* self, PyObject* arg);

	PyObject*  SetMountSpeed(PyRoleObject* self, PyObject* arg);
	PyObject*  GetMountSpeed(PyRoleObject* self, PyObject* arg);

	PyObject*  CancleTempSpeed(PyRoleObject* self, PyObject* arg);
	PyObject*  SetTempSpeed(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTempSpeed(PyRoleObject* self, PyObject* arg);
	
	PyObject*  MustFlying(PyRoleObject* self, PyObject* arg);

	PyObject*  CancleTempFly(PyRoleObject* self, PyObject* arg);
	PyObject*  SetTempFly(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTempFly(PyRoleObject* self, PyObject* arg);

	PyObject*  SetAppStatus(PyRoleObject* self, PyObject* arg);
	PyObject*  GetAppStatus(PyRoleObject* self, PyObject* arg);
	
	PyObject*  GetRoleSyncAppearanceObj(PyRoleObject* self, PyObject* arg);


	PyObject*  SetQQHZ(PyRoleObject* self, PyObject* arg);
	PyObject*  GetQQHZ(PyRoleObject* self, PyObject* arg);

	PyObject*  SetQQYHZ(PyRoleObject* self, PyObject* arg);
	PyObject*  GetQQYHZ(PyRoleObject* self, PyObject* arg);

	PyObject*  SetQQHHHZ(PyRoleObject* self, PyObject* arg);
	PyObject*  GetQQHHHZ(PyRoleObject* self, PyObject* arg);

	PyObject*  SetQQLZ(PyRoleObject* self, PyObject* arg);
	PyObject*  GetQQLZ(PyRoleObject* self, PyObject* arg);

	PyObject*  SetQQYLZ(PyRoleObject* self, PyObject* arg);
	PyObject*  GetQQYLZ(PyRoleObject* self, PyObject* arg);

	PyObject*  SetQQHHLZ(PyRoleObject* self, PyObject* arg);
	PyObject*  GetQQHHLZ(PyRoleObject* self, PyObject* arg);

}



