/*我是UTF8编码文件 */
#include "PyRole.h"
#include "Role.h"
#include "PyRoleArray.h"
#include "PyRoleGather.h"
#include "PyRoleContain.h"
#include "PublicScene.h"
#include "RoleMgr.h"
#include "ComplexServer.h"

namespace ServerPython
{
	void PyRole_Dealloc(PyRoleObject* self)
	{
		Py_DECREF(self->role_id);
		self->role_id = NULL;
		PyObject_DEL(self);
	}

	PyObject* IsKick(PyRoleObject* self, PyObject* arg)
	{
		if (NULL == self->cptr)
		{
			Py_RETURN_TRUE;
		}
		else
		{
			Py_RETURN_FALSE;
		}
	}

	PyObject* Kick(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		PyObject* isSave = Py_None;
		PyObject* res = Py_None;
		if (!PyArg_ParseTuple(arg, "OO", &isSave, &res))
		{
			return NULL;
		}
		self->cptr->Kick(isSave, res);
		Py_RETURN_NONE;
	}

	PyObject* Save(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->Save();
		Py_RETURN_NONE;
	}

	PyObject* IsLost(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		PY_RETURN_BOOL(self->cptr->IsLost());
	}

	PyObject* Lost(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->Lost();
		Py_RETURN_NONE;
	}


	PyObject* ReLogin(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint64 uClientKey = 0;
		if (!GEPython::PyObjToUI64(arg, uClientKey))
		{
			PY_PARAM_ERROR("param must be GE::Uint64.");
		}

		PY_RETURN_BOOL(self->cptr->ReLogin(uClientKey));
	}

	PyObject* SyncByReLogin(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->SyncByReLogin();
		Py_RETURN_NONE;
	}
	
	PyObject* ClearPerDay(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->ClearPerDay();
		Py_RETURN_NONE;
	}

	PyObject* CountTiLi(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->CountTiLi();
		Py_RETURN_NONE;
	}
	
	PyObject* GetRoleID(PyRoleObject* self, PyObject* arg)
	{
		Py_INCREF(self->role_id);
		return self->role_id;
	}

	PyObject* GetClientKey(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI64(self->cptr->GetClientKey());
	}
	
	PyObject* RemoteEndPoint(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		std::string sIp;
		GE::Uint32 uPort = 0;
		GE::Uint64 uClientKey = self->cptr->GetClientKey();
		GE::B8& ClientKey = GE_AS_B8(uClientKey);
		if(ComplexServer::Instance()->RemoteEndPoint(ClientKey.UI32_0(), sIp, uPort))
		{
			return PyString_FromString(sIp.c_str());
		}
		Py_RETURN_NONE;
	}


	PyObject* GetScene(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		SceneBase* pScene = self->cptr->GetScene();
		if (NULL == pScene)
		{
			Py_RETURN_NONE;
		}
		return pScene->PySelf().GetObj_NewRef();
	}

	PyObject* GetSceneID(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetSceneID());
	}

	PyObject* GetLastSceneID(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromUI32(self->cptr->GetLastSceneID());
	}
	
	PyObject* GetPos(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return Py_BuildValue("HH", self->cptr->GetPosX(), self->cptr->GetPosY());
	}

	PyObject* GetLastPos(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return Py_BuildValue("HH", self->cptr->GetLastPosX(), self->cptr->GetLastPosY());
	}

	PyObject* DoIdle(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->DoIdle();
		Py_RETURN_NONE;
	}
	
	PyObject* SyncDataBase(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->SyncDataBase();
		Py_RETURN_NONE;
	}
	PyObject* SyncOK(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->SyncOK();
		Py_RETURN_NONE;
	}
	
	PyObject* GetRoleName(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return PyString_FromStringAndSize(self->cptr->GetRoleName().data(), self->cptr->GetRoleName().length());
	}

	PyObject* SetRoleName(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		char* sRoleName = NULL;
		if (!GEPython::PyObjToStr(arg, &sRoleName))
		{
			return NULL;
		}
		self->cptr->SetRoleName(sRoleName);
		Py_RETURN_NONE;
	}

	PyObject* GetVersion1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return  GEPython::PyObjFromUI32(self->cptr->GetVersion1());
	}

	PyObject* SetApperance(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN
		PyObject* pyKey = Py_None;
		PyObject* pyValue = Py_None;
		if (!PyArg_ParseTuple(arg, "OO", &pyKey, &pyValue))
		{
			return NULL;
		}
		self->cptr->SetApperance(pyKey, pyValue);
		Py_RETURN_NONE;
	}

	PyObject* DoCommand(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32 uIndex = 0;
		if (!GEPython::PyObjToUI32(arg, uIndex))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		PY_RETURN_BOOL(self->cptr->DoCommand(uIndex));
	}

	PyObject* GetCommand(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return Py_BuildValue("II", self->cptr->GetCommandSize(), self->cptr->GetCommandIndex());
	}

	PyObject* SendObj(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uMsgType = 0;
		PyObject* pyObj = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uMsgType, &pyObj))
		{
			return NULL;
		}
		self->cptr->SendPyMsg(uMsgType, pyObj);
		Py_RETURN_NONE;
	}

	PyObject* SendObj_NoExcept(PyRoleObject* self, PyObject* arg)
	{
		if (NULL != self->cptr)
		{
			GE::Uint16 uMsgType = 0;
			PyObject* pyObj = Py_None;
			if (!PyArg_ParseTuple(arg, "HO", &uMsgType, &pyObj))
			{
				return NULL;
			}
			self->cptr->SendPyMsg(uMsgType, pyObj);
		}
		Py_RETURN_NONE;
	}

	PyObject* SendObjAndBack(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uMsgType = 0;
		PyObject* pyObj = Py_None;
		GE::Uint16 uSec = 60;
		PyObject* pyFun = Py_None;
		PyObject* pyParam = Py_None;
		if (!PyArg_ParseTuple(arg, "HOHO|O", &uMsgType, &pyObj, &uSec, &pyFun, &pyParam))
		{
			return NULL;
		}
		self->cptr->SendPyMsgAndBack(uMsgType, pyObj, uSec, pyFun, pyParam);
		Py_RETURN_NONE;
	}

	PyObject* SendObjAndBack_NoExcept(PyRoleObject* self, PyObject* arg)
	{
		if (NULL != self->cptr)
		{
			GE::Uint16 uMsgType = 0;
			PyObject* pyObj = Py_None;
			GE::Uint16 uSec = 60;
			PyObject* pyFun = Py_None;
			PyObject* pyParam = Py_None;
			if (!PyArg_ParseTuple(arg, "HOHO|O", &uMsgType, &pyObj, &uSec, &pyFun, &pyParam))
			{
				return NULL;
			}
			self->cptr->SendPyMsgAndBack(uMsgType, pyObj, uSec, pyFun, pyParam);
		}
		Py_RETURN_NONE;
	}

	PyObject* CallBackFunction(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32 uFunID = 0;
		PyObject* pyObj = Py_None;
		if (!PyArg_ParseTuple(arg, "I|O", &uFunID, &pyObj))
		{
			return NULL;
		}
		self->cptr->CallBackFunction(uFunID, pyObj);
		Py_RETURN_NONE;
	}

	PyObject* BroadMsg(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->BroadMsg();
		Py_RETURN_NONE;
	}

	PyObject* BroadMsg_NoExcept(PyRoleObject* self, PyObject* arg)
	{
		if (self->cptr)
		{
			self->cptr->BroadMsg();
		}
		Py_RETURN_NONE;
	}

	PyObject* Msg(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
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
		self->cptr->BroadMsg();
		Py_RETURN_NONE;
	}

	PyObject* WPE(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uCnt = 1;
		if (!PyArg_ParseTuple(arg, "|H", &uCnt))
		{
			return NULL;
		}
		self->cptr->IncTI64(RoleDataMgr::Instance()->uWPEIndex, uCnt);
		Py_RETURN_NONE;
	}

	PyObject* RegTick(PyRoleObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32 uSec = 0;
		PyObject* fun_BorrowRef = NULL;
		PyObject* regparam_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(args, "IO|O", &uSec, &fun_BorrowRef, &regparam_BorrowRef))
		{
			return NULL;
		}
		GE::Int32 ID = self->cptr->Tick().RegTick(uSec, fun_BorrowRef, regparam_BorrowRef);
		if (0 == ID)
		{
			self->cptr->Kick();
			PY_PARAM_ERROR("role reg kick error.")
		}
		return GEPython::PyObjFromI32(ID);
	}

	PyObject* UnregTick(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Int32 ID = 0;
		if (!GEPython::PyObjToI32(arg, ID))
		{
			PY_PARAM_ERROR("param must be GE::Int32.")
		}
		self->cptr->Tick().UnregTick(ID);
		Py_RETURN_NONE;
	}

	PyObject* TiggerTick(PyRoleObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Int32 ID = 0;
		PyObject* param_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(args, "i|O", &ID, &param_BorrowRef))
		{
			return NULL;
		}
		self->cptr->Tick().TriggerTick(ID, param_BorrowRef);
		Py_RETURN_NONE;
	}

	PyObject* SetChatInfo(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		PyObject* pyKey = Py_None;
		PyObject* pyValue = Py_None;
		if (!PyArg_ParseTuple(arg, "OO", &pyKey, &pyValue))
		{
			return NULL;
		}
		self->cptr->SetChatInfo(pyKey, pyValue);
		Py_RETURN_NONE;
	}

	PyObject* BroadChat(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uParam = 0;
		PyObject* pyObj = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uParam, &pyObj))
		{
			return NULL;
		}
		const std::string& pinfo = self->cptr->GetRoleChatInfoMsg();
		GE::B8 param(uParam,0);
		PackMessage::Instance()->Reset();
		PackMessage::Instance()->PackMsg(enClientCharMsg);
		PackMessage::Instance()->PackStream(static_cast<const void*>(pinfo.data()), static_cast<GE::Uint16>(pinfo.size()));
		PackMessage::Instance()->PackUi64(param);
		PackMessage::Instance()->PackPyObj(pyObj);
		//不判断CD,次数限制
		RoleMgr::Instance()->BroadMsg();
		Py_RETURN_NONE;
	}



	PyObject* Revive(PyRoleObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint32	uSceneID = 0;
		GE::Uint16	uX = 0;
		GE::Uint16	uY = 0;

		if (!PyArg_ParseTuple(args, "IHH", &uSceneID, &uX, &uY))
		{
			return NULL;
		}
		PublicScene* pScene = SceneMgr::Instance()->SearchPublicScene(uSceneID);
		if(NULL == pScene)
		{
			GE_EXC<<"role, Revive，can't find scene("<<uSceneID<<")."<<GE_END;
			Py_RETURN_NONE;
		}
		if (uSceneID == self->cptr->GetSceneID())
		{
			PY_RETURN_BOOL(pScene->JumpRole(self->cptr, uX, uY));
		}
		else
		{
			PY_RETURN_BOOL(pScene->JoinRole(self->cptr, uX, uY));
		}
	}

	PyObject* BackPublicScene(PyRoleObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;

		if (self->cptr->GetLastSceneID() == self->cptr->GetSceneID())
		{
			Py_RETURN_NONE;
		}

		PublicScene* pScene = SceneMgr::Instance()->SearchPublicScene(self->cptr->GetLastSceneID());
		if (pScene == NULL)
		{
			GE_EXC<<"can't find scene(BackScene)."<<GE_END;
			Py_RETURN_NONE;
		}

		PY_RETURN_BOOL(pScene->JoinRole(self->cptr, self->cptr->GetLastPosX(), self->cptr->GetLastPosY()));
	}

	PyObject* JumpPos(PyRoleObject* self, PyObject* args)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16	uX = 0;
		GE::Uint16	uY = 0;

		if (!PyArg_ParseTuple(args, "HH", &uX, &uY))
		{
			return NULL;
		}
		SceneBase* pScene = self->cptr->GetScene();
		if(NULL == pScene)
		{
			GE_EXC<<"can't find scene(JumpPos)."<<GE_END;
			Py_RETURN_NONE;
		}
		PY_RETURN_BOOL(pScene->JumpRole(self->cptr, uX, uY));
	}


	PyObject* ForceRecountProperty(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->CheckRecountProperty();
		Py_RETURN_NONE;
	}

	PyObject* SetNeedRecount(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->SetNeedRecount();
		Py_RETURN_NONE;
	}

	PyObject* FinishRecount(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->FinishRecount();
		Py_RETURN_NONE;
	}
	

	static PyMethodDef PyRole_Methods[] = {
		{"IsKick", (PyCFunction)IsKick, METH_NOARGS, "角色是否已经被T掉   "},
		{"Kick", (PyCFunction)Kick, METH_VARARGS, "T掉角色   "},
		{"Save", (PyCFunction)Save, METH_VARARGS, "保存角色数据   "},
		{"IsLost", (PyCFunction)IsLost, METH_NOARGS, "角色是否已经被T掉   "},
		{"Lost", (PyCFunction)Lost, METH_NOARGS, "角色暂时断开连接   "},
		{"ReLogin", (PyCFunction)ReLogin, METH_O, "断开连接的角色重新连接上   "},
		{"ClearPerDay", (PyCFunction)ClearPerDay, METH_NOARGS, "角色每日清理   "},
		{"CountTiLi", (PyCFunction)CountTiLi, METH_NOARGS, "角色登录计算体力   "},
		{"SyncByReLogin", (PyCFunction)SyncByReLogin, METH_NOARGS, "角色重新连接，同步数组数据   "},
		{"SyncDataBase", (PyCFunction)SyncDataBase, METH_NOARGS, "同步角色基础数据   "},
		{"SyncOK", (PyCFunction)SyncOK, METH_NOARGS, "同步角色基础数据OK   "},
		{"RemoteEndPoint", (PyCFunction)RemoteEndPoint, METH_NOARGS, "获取角色连接IP   "},
		{"GetClientKey", (PyCFunction)GetClientKey, METH_NOARGS, "获取角色ClientKey   "},
		{"GetRoleID", (PyCFunction)GetRoleID, METH_NOARGS, "获取角色ID   "},
		{"GetRoleName", (PyCFunction)GetRoleName, METH_NOARGS, "获取角色名   "},
		{"SetRoleName", (PyCFunction)SetRoleName, METH_O, "设置角色名   "},
		{"GetScene", (PyCFunction)GetScene, METH_NOARGS, "获取场景   "},
		{"GetSceneID", (PyCFunction)GetSceneID, METH_NOARGS, "获取场景ID   "},
		{"GetLastSceneID", (PyCFunction)GetLastSceneID, METH_NOARGS, "获取最后所在场景ID   "},
		{"GetPos", (PyCFunction)GetPos, METH_NOARGS, "获取角色位置   "},
		{"GetLastPos", (PyCFunction)GetLastPos, METH_NOARGS, "获取角色最后所在位置   "},
		{"DoIdle", (PyCFunction)DoIdle, METH_NOARGS, "服务器强制玩家静止   "},
		{"GetVersion1", (PyCFunction)GetVersion1, METH_NOARGS, "获取角色版本号   "},
		{"SetApperance", (PyCFunction)SetApperance, METH_VARARGS, "设置一个外观信息   "},
		{"DoCommand", (PyCFunction)DoCommand, METH_O, "执行了一个离线命令   "},
		{"GetCommand", (PyCFunction)GetCommand, METH_NOARGS, "获取最后执行的离线命令   "},
		{"SendObj", (PyCFunction)SendObj, METH_VARARGS, "发送一个消息   "},
		{"SendObj_NoExcept", (PyCFunction)SendObj_NoExcept, METH_VARARGS, "发送一个消息（不抛异常）   "},
		{"SendObjAndBack", (PyCFunction)SendObjAndBack, METH_VARARGS, "发送一个消息，并等待回调   "},
		{"SendObjAndBack_NoExcept", (PyCFunction)SendObjAndBack_NoExcept, METH_VARARGS, "发送一个消息，并等待回调（不抛异常）   "},
		{"CallBackFunction", (PyCFunction)CallBackFunction, METH_VARARGS, "回调一个消息   "},
		{"BroadMsg", (PyCFunction)BroadMsg, METH_NOARGS, "发送一个广播消息给客户端   "},
		{"BroadMsg_NoExcept", (PyCFunction)BroadMsg_NoExcept, METH_NOARGS, "发送一个广播消息给客户端   "},
		{"Msg", (PyCFunction)Msg, METH_VARARGS, "发送一个字符串给客户端   "},
		{"WPE", (PyCFunction)WPE, METH_VARARGS, "该角色可能在发网络封包   "},
		{"RegTick", (PyCFunction)RegTick, METH_VARARGS, "注册一个Tick   "},
		{"UnregTick", (PyCFunction)UnregTick, METH_O, "注销一个Tick   "},
		{"TiggerTick", (PyCFunction)TiggerTick, METH_VARARGS, "触发一个Tick   "},
		{"SetChatInfo", (PyCFunction)SetChatInfo, METH_VARARGS, "设置聊天角色信息   "},
		{"BroadChat", (PyCFunction)BroadChat, METH_VARARGS, "py广播一个世界聊天信息   "},
		{"Revive", (PyCFunction)Revive, METH_VARARGS, "角色传送   "},
		{"JumpPos", (PyCFunction)JumpPos, METH_VARARGS, "角色传送   "},
		{"BackPublicScene", (PyCFunction)BackPublicScene, METH_NOARGS, "角色传送回去上一个保存坐标的场景   "},
		{"ForceRecountProperty", (PyCFunction)ForceRecountProperty, METH_NOARGS, "强制重算一下角色属性   "},
		{"SetNeedRecount", (PyCFunction)SetNeedRecount, METH_NOARGS, "设置需要重算   "},
		{"FinishRecount", (PyCFunction)FinishRecount, METH_NOARGS, "完成一次重算   "},
		RoleArray_Methods
		RoleContain_Methods
		RoleGather_Methods
		{ NULL },
	};

	PyDoc_STRVAR(PyRole_Doc, "PyRole_Doc/nPyRole Object");

	PyTypeObject PyRoleType = {
		PyVarObject_HEAD_INIT(&PyType_Type, 0)
		"PyRole",
		sizeof(PyRoleObject),
		0,
		(destructor)PyRole_Dealloc,					/* tp_dealloc */
		0,											/* tp_print */
		0,											/* tp_getattr */
		0,											/* tp_setattr */
		0,											/* tp_compare */
		0,											/* tp_repr */
		0,											/* tp_as_number */
		0,											/* tp_as_sequence */
		0,											/* tp_as_mapping */
		0,											/* tp_hash */
		0,											/* tp_call */
		0,											/* tp_str */
		0,											/* tp_getattro */
		0,											/* tp_setattro */
		0,											/* tp_as_buffer */
		0,											/* tp_flags */
		PyRole_Doc,									/* tp_doc */
		0,											/* tp_traverse */
		0,											/* tp_clear */
		0,											/* tp_richcompare */
		0,											/* tp_weaklistoffset */
		0,											/* tp_iter */
		0,											/* tp_iternext */
		PyRole_Methods,								/* tp_methods */
		0,											/* tp_members */
		0,											/* tp_getset */
		0,											/* tp_base */
		0,											/* tp_dict */
		0,											/* tp_descr_get */
		0,											/* tp_descr_set */
		0,											/* tp_dictoffset */
		0,											/* tp_init */
		0,											/* tp_alloc */
		0,											/* tp_new */
		0,											/* tp_free */
	};

	void PyRole_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());

		PyType_Ready(&PyRoleType);
		// 根据模块名，查找模块并加入到模块身上
		GEPython::Object spModule = PyImport_ImportModule("cComplexServer");
		if (spModule.PyHasExcept())
		{
			spModule.PyPrintAndClearExcept();
		}
		else
		{
			PyModule_AddObject(spModule.GetObj_BorrowRef(), "cRole", (PyObject*)&PyRoleType);
		}
	}

	PyRoleObject* PyRole_FromObj( PyObject* pObj )
	{
		if (pObj->ob_type == &PyRoleType)
		{
			return (PyRoleObject*)pObj;
		}
		return NULL;
	}

	PyRoleObject* PyRole_New( Role* pRole )
	{
		PyRoleObject* obj = PyObject_NEW(PyRoleObject, &PyRoleType);
		obj->cptr = pRole;
		obj->role_id = GEPython::PyObjFromUI64(pRole->GetRoleID());
		return obj;
	}

	void PyRole_Del( PyObject* pObj )
	{
		if (pObj->ob_type != &PyRoleType)
		{
			GE_EXC<<"del obj error "<<__FUNCTION__<<GE_END;
			return;
		}
		PyRoleObject* pPO = (PyRoleObject*)(pObj);
		pPO->cptr = NULL;
	}
}

