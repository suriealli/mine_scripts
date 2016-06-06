/*引擎基本服务的Python接口*/
#include "PyComplexServer.h"
#include "ComplexServer.h"
#include "ClutterDefine.h"
#include "MessageDefine.h"
#include "ScriptMgr.h"

//////////////////////////////////////////////////////////////////////////
// PyComplexServer模块
//////////////////////////////////////////////////////////////////////////
namespace ServerPython
{
	PyObject* RegBeforeNewDayCallFunction(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}
		ComplexServer::Instance()->GetCallBeforeNewDayFunction().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegBeforeNewHourCallFunction(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}
		ComplexServer::Instance()->GetCallBeforeNewHourFunction().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegBeforeNewMinuteCallFunction(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}

		ComplexServer::Instance()->GetCallBeforeNewMinuteFunction().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegPerSecondCallFunction(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}

		ComplexServer::Instance()->GetCallPerSecondFunction().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegAfterNewMinuteCallFunction(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}

		ComplexServer::Instance()->GetCallAfterNewMinuteFunction().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegAfterNewHourCallFunction(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}

		ComplexServer::Instance()->GetCallAfterNewHourFunction().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegAfterNewDayCallFunction(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}
		ComplexServer::Instance()->GetCallAfterNewDayFunction().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegSaveCallFunction1(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}
		ComplexServer::Instance()->GetCallSaveFunction1().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegSaveCallFunction2(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}
		ComplexServer::Instance()->GetCallSaveFunction2().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegSaveCallFunction3(PyObject* self, PyObject* args)
	{
		PyObject* fun_BorrowRef = NULL;
		GE::Int32 idx = -1;
		if (!PyArg_ParseTuple(args, "O|i", &fun_BorrowRef, &idx))
		{
			return NULL;
		}
		ComplexServer::Instance()->GetCallSaveFunction3().AppendFunction(fun_BorrowRef, idx);
		Py_RETURN_NONE;
	}

	PyObject* RegTick(PyObject* self, PyObject* args)
	{
		GE::Uint32 uSec = 0;
		PyObject* fun_BorrowRef = NULL;
		PyObject* regparam_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(args, "IO|O", &uSec, &fun_BorrowRef, &regparam_BorrowRef))
		{
			return NULL;
		}
		GE::Int64 ID = ComplexServer::Instance()->Tick()->RegTick(uSec, fun_BorrowRef, regparam_BorrowRef);
		return GEPython::PyObjFromI64(ID);
	}

	PyObject* UnregTick(PyObject* self, PyObject* arg)
	{
		GE::Int64 ID = 0;
		if (!GEPython::PyObjToI64(arg, ID))
		{
			PY_PARAM_ERROR("param must be GE::Int64.")
		}
		ComplexServer::Instance()->Tick()->UnregTick(ID);
		Py_RETURN_NONE;
	}

	PyObject* TiggerTick(PyObject* self, PyObject* args)
	{
		GE::Int64 ID = 0;
		PyObject* param_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(args, "K|O", &ID, &param_BorrowRef))
		{
			return NULL;
		}
		ComplexServer::Instance()->Tick()->TriggerTick(ID, param_BorrowRef);
		Py_RETURN_NONE;
	}

	PyObject* RegFastTick(PyObject* self, PyObject* args)
	{
		GE::Uint32 uSec = 0;
		PyObject* fun_BorrowRef = NULL;
		PyObject* regparam_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(args, "IO|O", &uSec, &fun_BorrowRef, &regparam_BorrowRef))
		{
			return NULL;
		}
		// 修正时间
		if (uSec == 0)
		{
			ScriptMgr::Instance()->StackWarn("fast tick second is 0.");
		}
		else if (uSec >= FAST_TICK_ROUND)
		{
			ScriptMgr::Instance()->StackWarn("fast tick second is too long.");
		}
		// 再注册之
		GE::Int64 ID = ComplexServer::Instance()->FastTick()->RegTick(uSec, fun_BorrowRef, regparam_BorrowRef);
		return GEPython::PyObjFromI64(ID);
	}

	PyObject* UnregFastTick(PyObject* self, PyObject* arg)
	{
		GE::Int64 ID = 0;
		if (!GEPython::PyObjToI64(arg, ID))
		{
			PY_PARAM_ERROR("param must be GE::Int64.")
		}
		ComplexServer::Instance()->FastTick()->UnregTick(ID);
		Py_RETURN_NONE;
	}

	PyObject* TriggerFastTick(PyObject* self, PyObject* arg)
	{
		GE::Int64 ID = 0;
		if (!GEPython::PyObjToI64(arg, ID))
		{
			PY_PARAM_ERROR("param must be GE::Int64.")
		}
		ComplexServer::Instance()->FastTick()->TriggerTick(ID);
		Py_RETURN_NONE;
	}

	PyObject* CreateNetwork(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uMaxConnect = 0;
		GE::Uint16 uThread = 1;
		GE::Uint16 uTGWMaxSize = 0;
		if (!PyArg_ParseTuple(arg, "I|HH", &uMaxConnect, &uThread, &uTGWMaxSize))
		{
			return NULL;
		}
		ComplexServer::Instance()->CreateNetwork(uMaxConnect, uThread);
		GENetEnv::Instance()->SetTGWMaxSize(uTGWMaxSize);
		Py_RETURN_NONE;
	}

	PyObject* Listen(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uPort = 0;
		if (!GEPython::PyObjToUI32(arg, uPort))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		ComplexServer::Instance()->Listen(uPort);
		Py_RETURN_NONE;
	}

	PyObject* SetConnectParam(PyObject* self, PyObject* args)
	{
		ConnectParam CP;
		if (!PyArg_ParseTuple(args, "HHHH", &CP.uRecvBlockNum, &CP.uRecvBlockSize, &CP.uSendBlockNum, &CP.uSendBlockSize))
		{
			return NULL;
		}
		ComplexServer::Instance()->SetConnectParam(CP);
		Py_RETURN_NONE;
	}

	PyObject* SetPyThread(PyObject* self, PyObject* arg)
	{
		/*
		Returns 1 if the object o is considered to be true, and 0 otherwise.
		*/
		int ret = PyObject_IsTrue(arg);
		ComplexServer::Instance()->SetPyThread(ret ? true : false);
		Py_RETURN_NONE;
	}

	PyObject* InitMySQLdb(PyObject* self, PyObject* arg)
	{
		ComplexServer::Instance()->InitMySQLdb();
		Py_RETURN_NONE;
	}

	PyObject* Stop(PyObject* self, PyObject* arg)
	{
		ComplexServer::Instance()->StopNetwork();
		Py_RETURN_NONE;
	}

	PyObject* Connect(PyObject* self, PyObject* args)
	{
		char* sIP = NULL;
		GE::Uint32 uPort = 0;
		GE::Uint16 uWho = enWho_None;
		ConnectParam CP;
		if (!PyArg_ParseTuple(args, "sIH|HHHH", &sIP, &uPort, &uWho, &CP.uRecvBlockNum, &CP.uRecvBlockSize, &CP.uSendBlockNum, &CP.uSendBlockSize))
		{
			return NULL;
		}
		GE::Uint32 uSessionID = ComplexServer::Instance()->Connect(sIP, uPort, uWho, &CP);
		return GEPython::PyObjFromUI32(uSessionID);
	}

	PyObject* DisConnect(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSession = MAX_UINT32;
		if (!GEPython::PyObjToUI32(arg, uSession))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		ComplexServer::Instance()->DisConnect(uSession, enDisConnect_Logic);
		Py_RETURN_NONE;
	}

	PyObject* IsSendOver(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSession = MAX_UINT32;
		if (!GEPython::PyObjToUI32(arg, uSession))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		PY_RETURN_BOOL(ComplexServer::Instance()->IsSendOver(uSession));
	}

	PyObject* Ping(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSession = MAX_UINT32;
		if (!GEPython::PyObjToUI32(arg, uSession))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		MsgBase msg(enGEMsg_Ping);
		ComplexServer::Instance()->SendMsg(uSession, &msg);
		Py_RETURN_NONE;
	}

	PyObject* SendPyMsg(PyObject* self, PyObject* args)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		GE::Uint16 uMsgType = enGEMsg_None;
		PyObject* msg_BorrowRef = NULL;
		if (!PyArg_ParseTuple(args, "IHO", &uSessionID, &uMsgType, &msg_BorrowRef))
		{
			return NULL;
		}
		ComplexServer::Instance()->SendPyMsg(uSessionID, uMsgType, msg_BorrowRef);
		Py_RETURN_NONE;
	}

	PyObject* SendPyMsgAndBack(PyObject* self, PyObject* args)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		GE::Uint16 uMsgType = enGEMsg_None;
		PyObject* msg_BorrowRef = NULL;
		GE::Uint32 uTimeOver = 0;
		PyObject* fun_BorrowRef = NULL;
		PyObject* param_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(args, "IHOIO|O", &uSessionID, &uMsgType, &msg_BorrowRef, &uTimeOver, &fun_BorrowRef, &param_BorrowRef))
		{
			return NULL;
		}
		ComplexServer::Instance()->SendPyMsgAndBack(uSessionID, uMsgType, msg_BorrowRef,
			uTimeOver, fun_BorrowRef, param_BorrowRef);
		Py_RETURN_NONE;
	}

	PyObject* RegDistribute(PyObject* self, PyObject* args)
	{
		GE::Uint16 uMsgType = enGEMsg_None;
		PyObject* fun_BorrowRef = NULL;
		if (!PyArg_ParseTuple(args, "HO", &uMsgType, &fun_BorrowRef))
		{
			return NULL;
		}

		ComplexServer::Instance()->RegDistribute(uMsgType, fun_BorrowRef);
		Py_RETURN_NONE;
	}

	PyObject* UnregDistribute(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uMsgType = enGEMsg_None;
		if (!GEPython::PyObjToUI16(arg, uMsgType))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		ComplexServer::Instance()->UnregDistribute(uMsgType);
		Py_RETURN_NONE;
	}

	PyObject* GetDistribute(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uMsgType = enGEMsg_None;
		if (!GEPython::PyObjToUI16(arg, uMsgType))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		return ComplexServer::Instance()->GetDistribute_NewRef(uMsgType);
	}

	PyObject* DoDistribute(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uMsgType = enGEMsg_None;
		PyObject* pyMsg = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uMsgType, &pyMsg))
		{
			return NULL;
		}
		PY_RETURN_BOOL(ComplexServer::Instance()->DoDistribute(uMsgType, pyMsg));
	}

	PyObject* CallBackFunction(PyObject* self, PyObject* args)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		GE::Int64 ID = 0;
		PyObject* arg_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(args, "IK|O", &uSessionID, &ID, &arg_BorrowRef))
		{
			return NULL;
		}
		ComplexServer::Instance()->CallBackFunction(uSessionID, ID, arg_BorrowRef);
		Py_RETURN_NONE;
	}

	PyObject* DoBackFunction(PyObject* self, PyObject* args)
	{
		GE::Int64 ID = 0;
		PyObject* arg_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(args, "KO", &ID, &arg_BorrowRef))
		{
			return NULL;
		}
		PY_RETURN_BOOL(ComplexServer::Instance()->DoCallBackFunction(ID, arg_BorrowRef));
	}

	PyObject* SetSaveGapMinute(PyObject* self, PyObject* args)
	{
		GE::Uint32 uSGM1 = 5;
		GE::Uint32 uSGM2 = 10;
		GE::Uint32 uSGM3 = 30;
		if (!PyArg_ParseTuple(args, "|III", &uSGM1, &uSGM2, &uSGM3))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.")
		}
		if (uSGM1 == 0 || uSGM2 == 0 || uSGM3 == 0)
		{
			PY_PARAM_ERROR("SaveGapMinute is 0.")
		}
		ComplexServer::Instance()->SaveGapMinute1() = uSGM1;
		ComplexServer::Instance()->SaveGapMinute2() = uSGM2;
		ComplexServer::Instance()->SaveGapMinute3() = uSGM3;
		Py_RETURN_NONE;
	}

	PyObject* GetSaveGapMinute(PyObject* self, PyObject* arg)
	{
		return Py_BuildValue("III", ComplexServer::Instance()->SaveGapMinute1(), ComplexServer::Instance()->SaveGapMinute2(), ComplexServer::Instance()->SaveGapMinute3());
	}

	PyObject* IsTimeDriver(PyObject* self, PyObject* arg)
	{
		PY_RETURN_BOOL(ComplexServer::Instance()->IsTimeDriver());
	}

	PyObject* CallSave(PyObject* self, PyObject* arg)
	{
		ComplexServer::Instance()->CallSave1();
		ComplexServer::Instance()->CallSave2();
		ComplexServer::Instance()->CallSave3();
		Py_RETURN_NONE;
	}

	PyObject* GetLastMsgTime(PyObject* self, PyObject* arg)
	{
		return GEPython::PyObjFromUI32(ComplexServer::Instance()->LastMsgTime());
	}

	PyObject* SetSendModel(PyObject* self, PyObject* arg)
	{
		if (PyObject_IsTrue(arg))
		{
			ComplexServer::Instance()->SetSendModel(true);
		}
		else
		{
			ComplexServer::Instance()->SetSendModel(false);
		}
		
		Py_RETURN_NONE;
	}

	PyObject* SetFastEndTime(PyObject* self, PyObject* arg)
	{
		GE::Uint32 ui32 = 0;
		if (!GEPython::PyObjToUI32(arg, ui32))
		{
			PY_PARAM_ERROR("param must bu GE::Uint32");
		}
		ComplexServer::Instance()->SetFastEndTime(ui32);
		Py_RETURN_NONE;
	}

	// PyComplexServer_Methods[]
	static PyMethodDef PyComplexServer_Methods[] = {
		{ "RegBeforeNewDayCallFunction", RegBeforeNewDayCallFunction, METH_VARARGS, "注册新的一天前的回调函数 " },
		{ "RegBeforeNewHourCallFunction", RegBeforeNewHourCallFunction, METH_VARARGS, "注册新的一小时前的回调函数 " },
		{ "RegBeforeNewMinuteCallFunction", RegBeforeNewMinuteCallFunction, METH_VARARGS, "注册新的一分钟前的回调函数 " },
		{ "RegPerSecondCallFunction", RegPerSecondCallFunction, METH_VARARGS, "注册每秒钟的回调函数 " },
		{ "RegAfterNewMinuteCallFunction", RegAfterNewMinuteCallFunction, METH_VARARGS, "注册新的一分钟后的回调函数 " },
		{ "RegAfterNewHourCallFunction", RegAfterNewHourCallFunction, METH_VARARGS, "注册新的一小时后的回调函数 " },
		{ "RegAfterNewDayCallFunction", RegAfterNewDayCallFunction, METH_VARARGS, "注册新的一天后的回调函数 " },
		{ "RegSaveCallFunction1", RegSaveCallFunction1, METH_VARARGS, "注册保存进程状态时的回调函数 " },
		{ "RegSaveCallFunction2", RegSaveCallFunction2, METH_VARARGS, "注册保存进程状态时的回调函数 " },
		{ "RegSaveCallFunction3", RegSaveCallFunction3, METH_VARARGS, "注册保存进程状态时的回调函数 " },
		{ "RegTick", RegTick, METH_VARARGS, "注册Tick " },
		{ "UnregTick", UnregTick, METH_O, "取消Tick " },
		{ "TiggerTick", TiggerTick, METH_VARARGS, "触发Tick " },
		{ "RegFastTick", RegFastTick, METH_VARARGS, "注册FastTick " },
		{ "UnregFastTick", UnregFastTick, METH_O, "取消FastTick " },
		{ "TriggerFastTick", TriggerFastTick, METH_O, "触发FastTick " },
		{ "CreateNetwork", CreateNetwork, METH_VARARGS, "创建网络层 " },
		{ "Listen", Listen, METH_O, "监听端口 " },
		{ "SetConnectParam", SetConnectParam, METH_VARARGS, "设置网络层参数 " },
		{ "SetPyThread", SetPyThread, METH_O, "设置是否可以多线程 " },
		{ "InitMySQLdb", InitMySQLdb, METH_NOARGS, "初始化MySQLdb模块" },
		{ "Stop", Stop, METH_NOARGS, "停止，跳出循环 " },
		{ "Connect", Connect, METH_VARARGS, "连接 " },
		{ "DisConnect", DisConnect, METH_O, "断开连接 " },
		{ "IsSendOver", IsSendOver, METH_O, "消息是否发送完毕 " },
		{ "Ping", Ping, METH_O, "给连接发心跳包（异步发送模式下可以驱动消息发送） " },
		{ "SendPyMsg", SendPyMsg, METH_VARARGS, "发送Python消息 " },
		{ "SendPyMsgAndBack", SendPyMsgAndBack, METH_VARARGS, "发送Python消息并等待回调 " },
		{ "RegDistribute", RegDistribute, METH_VARARGS, "注册消息处理函数 " },
		{ "UnregDistribute", UnregDistribute, METH_O, "取消消息处理函数 " },
		{ "GetDistribute", GetDistribute, METH_O, "获取消息处理函数 " },
		{ "DoDistribute", DoDistribute, METH_VARARGS, "进行消息处理 " },
		{ "CallBackFunction", CallBackFunction, METH_VARARGS, "呼叫等待回调的函数 " },
		{ "DoBackFunction", DoBackFunction, METH_VARARGS, "进行回调处理 " },
		{ "SetSaveGapMinute", SetSaveGapMinute, METH_VARARGS, "设置保存时间间隔（分钟） " },
		{ "GetSaveGapMinute", GetSaveGapMinute, METH_NOARGS, "获取保存时间间隔（分钟） " },
		{ "IsTimeDriver", IsTimeDriver, METH_VARARGS, "是否是在时间驱动中 " },
		{ "CallSave", CallSave, METH_VARARGS, "直接触发保存回调函数 " },
		{ "GetLastMsgTime", GetLastMsgTime, METH_VARARGS, "获取最后处理的消息时间 " },
		{ "SetSendModel", SetSendModel, METH_O, "设置网络层发送消息模式 " },
		{ "SetFastEndTime", SetFastEndTime, METH_O, "设置时间速度 " },
		{ NULL }
	};

	// PyComplexServer_Init
	void PyComplexServer_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* pComplexServer = Py_InitModule("cComplexServer", PyComplexServer_Methods);
		if (NULL == pComplexServer)
		{
			PyErr_Print();
		}
	}
}


