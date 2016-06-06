/*××的Python接口*/
#include "PyGatewayForward.h"
#include "GatewayForward.h"
#include "ClutterDefine.h"

//////////////////////////////////////////////////////////////////////////
// PyGatewayForward模块
//////////////////////////////////////////////////////////////////////////
namespace ServerPython
{
	PyObject* OnClient_New(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		GE::Uint16 uProcessID = MAX_UINT16;
		if (!PyArg_ParseTuple(arg, "IH", &uSessionID, &uProcessID))
		{
			return NULL;
		}
		WhoClient_::Instance()->OnClient_New(uSessionID);
		Py_RETURN_NONE;
	};
	
	PyObject* OnClient_Lost(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		if (!GEPython::PyObjToUI32(arg, uSessionID))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		WhoClient_::Instance()->OnClient_Lost(uSessionID);
		Py_RETURN_NONE;
	};

	PyObject* OnGatewayNew(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		if (!GEPython::PyObjToUI32(arg, uSessionID))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		WhoClient_::Instance()->OnGatewayNew(uSessionID);
		Py_RETURN_NONE;
	};

	PyObject* OnGatewayLost(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		if (!GEPython::PyObjToUI32(arg, uSessionID))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		WhoClient_::Instance()->OnGatewayLost(uSessionID);
		Py_RETURN_NONE;
	};

	PyObject* UseGateway(PyObject* self, PyObject* arg)
	{
		WhoGateway_::Instance()->UseGateway();
		Py_RETURN_NONE;
	};

	PyObject* OnGateway_New(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		if (!GEPython::PyObjToUI32(arg, uSessionID))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		WhoGateway_::Instance()->OnGateway_New(uSessionID);
		Py_RETURN_NONE;
	};

	PyObject* OnGateway_Lost(PyObject* self, PyObject* arg)
	{
		GE::Uint32 uSessionID = MAX_UINT32;
		if (!GEPython::PyObjToUI32(arg, uSessionID))
		{
			PY_PARAM_ERROR("param must be GE::Uint32.");
		}
		WhoGateway_::Instance()->OnGateway_Lost(uSessionID);
		Py_RETURN_NONE;
	};

	PyObject* SendClientMsg(PyObject* self, PyObject* arg)
	{
		GE::Uint64 uClientKey = MAX_UINT64;
		GE::Uint16 uMsgType = enGEMsg_None;
		PyObject* pMsg_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(arg, "KH|O", &uClientKey, &uMsgType, &pMsg_BorrowRef))
		{
			return NULL;
		}
		PackMessage PM;
		PM.PackMsg(uMsgType);
		PM.PackPyObj(pMsg_BorrowRef);
		ClientMgr::Instance()->SendClientMsg(uClientKey, PM.Msg());
		Py_RETURN_NONE;
	};

	PyObject* BroadClientMsg(PyObject* self, PyObject* arg)
	{
		GE::Uint16 uMsgType = enGEMsg_None;
		PyObject* pMsg_BorrowRef = Py_None;
		if (!PyArg_ParseTuple(arg, "I|O", &uMsgType, &pMsg_BorrowRef))
		{
			return NULL;
		}
		PackMessage PM;
		PM.PackMsg(uMsgType);
		PM.PackPyObj(pMsg_BorrowRef);
		ClientMgr::Instance()->BroadClientMsg(PM.Msg());
		Py_RETURN_NONE;
	};

	PyObject* KickClient(PyObject* self, PyObject* arg)
	{
		GE::Uint64 uClientKey = MAX_UINT64;
		if (!GEPython::PyObjToUI64(arg, uClientKey))
		{
			PY_PARAM_ERROR("param must be GE::Uint64.");
		}
		ClientMgr::Instance()->KickClient(uClientKey);
		Py_RETURN_NONE;
	};

	// PyGatewayForward_Methods[]
	static PyMethodDef PyGatewayForward_Methods[] = {
		{ "OnClient_New", OnClient_New, METH_VARARGS, "新的客户端连接（被动）  "},
		{ "OnClient_Lost", OnClient_Lost, METH_O, "失去客户端连接（被动）  "},
		{ "OnGatewayNew", OnGatewayNew, METH_O, "新的网关连接（主动）  "},
		{ "OnGatewayLost", OnGatewayLost, METH_O, "失去网关连接（主动）  "},
		{ "UseGateway", UseGateway, METH_NOARGS, "使用网关  "},
		{ "OnGateway_New", OnGateway_New, METH_O, "新的网关连接（被动）  "},
		{ "OnGateway_Lost", OnGateway_Lost, METH_O, "失去网关连接（被动）  "},
		{ "SendClientMsg", SendClientMsg, METH_VARARGS, "给客户端连接发送Python消息  "},
		{ "BroadClientMsg", BroadClientMsg, METH_VARARGS, "给客户端连接广播Python消息  "},
		{ "KickClient", KickClient, METH_O, "主动要求踢掉客户端连接  "},
		{ NULL }
	};

	// PyGatewayForward_Init
	void PyGatewayForward_Init( void )
	{
		// 断言下，必须Python虚拟机初始化了才行
		GE_ERROR(Py_IsInitialized());
		PyObject* pGatewayForward = Py_InitModule("cGatewayForward", PyGatewayForward_Methods);
		if (NULL == pGatewayForward)
		{
			PyErr_Print();
		}
	}
}

