/*××的Python接口*/
#include "PyRoleMgr.h"
#include "RoleMgr.h"
#include "Role.h"
#include "ComplexServer.h"
//////////////////////////////////////////////////////////////////////////
// PyRoleMgr模块
//////////////////////////////////////////////////////////////////////////
namespace ServerPython
{
	PyObject* CreateRole(PyObject* self, PyObject* arg)
	{
		GE::Uint64 uRoleID = 0;
		const char* sRoleName = NULL;
		const char* sOpenID = NULL;
		GE::Uint64 uClientKey = 0;
		GE::Uint32 uCommandSize = 0;
		GE::Uint32 uCommandIndex = 0;
		if (!PyArg_ParseTuple(arg, "KssKII", &uRoleID, &sRoleName, &sOpenID, &uClientKey, &uCommandSize, &uCommandIndex))
		{
			return NULL;
		}
		Role* pRole = RoleMgr::Instance()->CreateRole(uRoleID, sRoleName, sOpenID, uClientKey, uCommandSize, uCommandIndex);
		if (NULL == pRole)
		{
			Py_RETURN_NONE;
		}
		else
		{
			return pRole->GetPySelf().GetObj_NewRef();
		}
	}

	PyObject* FindRoleByRoleID(PyObject* self, PyObject* arg)
	{
		GE::Uint64 uRoleID = 0;
		if (!GEPython::PyObjToUI64(arg, uRoleID))
		{
			PY_PARAM_ERROR("param must be GE::Uint64");
		}
		Role* pRole = RoleMgr::Instance()->FindRoleByRoleID(uRoleID);
		if (NULL == pRole)
		{
			Py_RETURN_NONE;
		}
		else
		{
			return pRole->GetPySelf().GetObj_NewRef();
		}
	}

	PyObject* FindRoleByClientKey(PyObject* self, PyObject* arg)
	{
		GE::Uint64 uClientKey = 0;
		if (!GEPython::PyObjToUI64(arg, uClientKey))
		{
			PY_PARAM_ERROR("param must be GE::Uint64");
		}
		Role* pRole = RoleMgr::Instance()->FindRoleByClientKey(uClientKey);
		if (NULL == pRole)
		{
			Py_RETURN_NONE;
		}
		else
		{
			return pRole->GetPySelf().GetObj_NewRef();
		}
	}

	PyObject* RegRoleDistribute(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uMsgType = 0;
		PyObject* pyFun = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uMsgType, &pyFun))
		{
			return NULL;
		}

		RoleMgr::Instance()->RegDistribute(uMsgType, pyFun);
		Py_RETURN_NONE;
	}

	PyObject* UnregRoleDistribute(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uMsgType = 0;
		if (!GEPython::PyObjToUI16(arg, uMsgType))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		RoleMgr::Instance()->UnregDistribute(uMsgType);
		Py_RETURN_NONE;
	}

	PyObject* BroadMsg(PyObject* self, PyObject* arg)
	{
		RoleMgr::Instance()->BroadMsg();
		Py_RETURN_NONE;
	}

	PyObject* Msg(PyObject* self, PyObject* arg)
	{
		MsgCharMsg msg;
		msg.Type(enServerCharMsg);
		PyObject* pObj = Py_None;
		if (!PyArg_ParseTuple(arg, "iiO", &msg.b8.UI32_1(), &msg.b8.UI32_0(), &pObj))
		{
			return NULL;
		}
		PackMessage::Instance()->Reset();
		PackMessage::Instance()->PackMsg(&msg, msg.Size());
		PackMessage::Instance()->PackPyObj(pObj);
		RoleMgr::Instance()->BroadMsg();
		Py_RETURN_NONE;
	}

	PyObject* MsgPack(PyObject* self, PyObject* arg)
	{
		MsgCharMsg msg;
		msg.Type(enServerCharMsg);
		PyObject* pObj = Py_None;
		if (!PyArg_ParseTuple(arg, "iiO", &msg.b8.UI32_1(), &msg.b8.UI32_0(), &pObj))
		{
			return NULL;
		}
		PackMessage::Instance()->Reset();
		PackMessage::Instance()->PackMsg(&msg, msg.Size());
		PackMessage::Instance()->PackPyObj(pObj);
		Py_RETURN_NONE;
	}

	PyObject* GetAllRole(PyObject* self, PyObject* arg)
	{
		RoleMgr::RoleMap& roleMap = RoleMgr::Instance()->GetRoleMap();
		RoleMgr::RoleMap::iterator iter = roleMap.begin();
		
		GEPython::List lis;
		while(iter != roleMap.end())
		{
			if (iter->second->IsKick())
			{
				++iter;
				continue;
			}
			lis.AppendObj_BorrowRef(iter->second->GetPySelf().GetObj_BorrowRef());
			++iter;
		}
		return lis.GetList_NewRef();
	}

	PyObject* AddWatchRole(PyObject* self, PyObject* arg)
	{
		GE::Uint64 uRoleID = 0;
		if (!GEPython::PyObjToUI64(arg, uRoleID))
		{
			PY_PARAM_ERROR("param must GE::Uint64.")
		}
		RoleMgr::Instance()->GetWatchRole().insert(uRoleID);
		Py_RETURN_NONE;
	}

	PyObject* ClearWatchRole(PyObject* self, PyObject* arg)
	{
		RoleMgr::Instance()->GetWatchRole().clear();
		Py_RETURN_NONE;
	}

	PyObject* SetStatistics(PyObject* self, PyObject* arg)
	{
		if (PyObject_IsTrue(arg))
		{
			RoleMgr::Instance()->SetStatistics(true);
		}
		else
		{
			RoleMgr::Instance()->SetStatistics(false);
		}
		Py_RETURN_NONE;
	}

	PyObject* GetRoleMessage(PyObject* self, PyObject* arg)
	{
		RoleMgr::RoleMap& roleMap = RoleMgr::Instance()->GetRoleMap();
		RoleMgr::RoleMap::iterator role_iter = roleMap.begin();
		GEPython::Dict rold_dict;
		for (; role_iter != roleMap.end(); ++role_iter)
		{
			Role* pRole = role_iter->second;
			Role::MessageMap& sendMap = pRole->GetSendMessage();
			Role::MessageMap::iterator send_iter = sendMap.begin();
			GEPython::Dict send_dict;
			for(; send_iter != sendMap.end(); ++send_iter)
			{
				send_dict.SetObj_NewRef(GEPython::PyObjFromUI32(send_iter->first), GEPython::PyObjFromUI32(send_iter->second));
			}
			Role::MessageMap& recvMap = pRole->GetRecvMessage();
			Role::MessageMap::iterator recv_iter = recvMap.begin();
			GEPython::Dict recv_dict;
			for(; recv_iter != recvMap.end(); ++recv_iter)
			{
				recv_dict.SetObj_NewRef(GEPython::PyObjFromUI32(recv_iter->first), GEPython::PyObjFromUI32(recv_iter->second));
			}
			GEPython::Tuple tup(2);
			tup.AppendObj_BorrowRef(send_dict.GetDict_BorrowRef());
			tup.AppendObj_BorrowRef(recv_dict.GetDict_BorrowRef());
			rold_dict.SetObj_NewRef(GEPython::PyObjFromUI64(pRole->GetRoleID()), tup.GetTuple_NewRef());
		}
		return rold_dict.GetDict_NewRef();
	}

	PyObject* SetEchoLevel(PyObject* self, PyObject* arg)
	{
		GE::Int32 nLevel = 0;
		if (!GEPython::PyObjToI32(arg, nLevel))
		{
			PY_PARAM_ERROR("param must be GE::Int32.");
		}
		RoleMgr::Instance()->SetEchoLevel(nLevel);
		Py_RETURN_NONE;
	}

	// PyRoleMgr_Methods[]
	static PyMethodDef PyRoleMgr_Methods[] = {
		{ "CreateRole", CreateRole, METH_VARARGS, "创建一个角色  "},
		{ "FindRoleByRoleID", FindRoleByRoleID, METH_O, "根据角色ID查找角色  "},
		{ "FindRoleByClientKey", FindRoleByClientKey, METH_O, "根据ClientKey查找角色  "},
		{ "RegDistribute", RegRoleDistribute, METH_VARARGS, "注册一个角色消息  "},
		{ "UnregDistribute", UnregRoleDistribute, METH_O, "取消一个角色消息  "},
		{ "Msg", Msg, METH_VARARGS, "给所有角色广播消息  "},
		{ "MsgPack", MsgPack, METH_VARARGS, "打包一条广播的提示消息  " },
		{ "BroadMsg", BroadMsg, METH_NOARGS, "给所有角色广播消息  "},
		{ "GetAllRole", GetAllRole, METH_NOARGS, "获取所有在线角色  "},
		{ "AddWatchRole", AddWatchRole, METH_O, "增加一个观察角色  "},
		{ "ClearWatchRole", ClearWatchRole, METH_NOARGS, "清空观察角色  "},
		{ "SetStatistics", SetStatistics, METH_O, "设置角色消息统计开关  "},
		{ "GetRoleMessage", GetRoleMessage, METH_NOARGS, "获取角色消息统计结果  "},
		{ "SetEchoLevel", SetEchoLevel, METH_O, "设置角色消息统计开关  "},
		{ NULL }
	};

	// PyRoleMgr_Init
	void PyRoleMgr_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* pRoleMgr = Py_InitModule("cRoleMgr", PyRoleMgr_Methods);
		if (NULL == pRoleMgr)
		{
			PyErr_Print();
		}
	}
}

