/*我是UTF8无签名编码 */
#include "../GameEngine/GameMySQL.h"
#include "ComplexServer.h"
#include "ClutterDefine.h"
#include "MessageDefine.h"
#include "GatewayForward.h"
#include "RoleDataMgr.h"
#include "RoleMgr.h"
#include "SceneMgr.h"
#include "NPCMgr.h"
#include "LogTransaction.h"
#include "ScriptMgr.h"

#include "PyComplexServer.h"
#include "PyGatewayForward.h"
#include "PyRoleDataMgr.h"
#include "PyRole.h"
#include "PyRoleMgr.h"
#include "PyRoleGather.h"
#include "PyLogTransaction.h"
#include "PySceneMgr.h"
#include "PyPublicScene.h"
#include "PySingleMirrorScene.h"
#include "PyMultiMirrorScene.h"
#include "PyNPCMgr.h"
#include "PyNPC.h"
#include "ScriptMgr.h"
#include "PyScriptMgr.h"
// 帧率
#define FRAME_MSECOND			100

ComplexServer::ComplexServer()
	: m_pNetWork(NULL)
	, m_SaveGapMinute1(5)
	, m_SaveGapMinute2(20)
	, m_SaveGapMinute3(60)
	, m_bPyThread(false)
	, m_bIsTimeDriver(false)
	, m_uLastMsgTime(0)
	, m_pTick(NULL)
	, m_pFastTick(NULL)
	, m_uFastEndTime(0)
{
}

ComplexServer::~ComplexServer()
{
	GE_SAFE_DELETE(m_pNetWork)
	GE_SAFE_DELETE(m_pTick);
	GE_SAFE_DELETE(m_pFastTick);
	PyMsgDistribute::iterator iter = this->m_PyMsgDistribute.begin();
	for(; iter != this->m_PyMsgDistribute.end(); ++iter)
	{
		Py_DECREF(iter->second);
	}
	this->m_PyMsgDistribute.clear();
}

void ComplexServer::Init( int argc, char* argv[] )
{
	// 构建Tick（其依赖Python虚拟机）
	this->m_pTick = new GETick;
	this->m_pFastTick = new GEFastTick;
	// 初始化时间模块（其依赖Python虚拟机）
	GEDateTime::New();
	// 初始化C数据
	this->InitC();
	// 特殊处理进程ID为0的情况
	GEProcess* pProcess = GEProcess::Instance();
	if (0 == pProcess->ProcessID())
	{
		this->m_bPyThread = true;
		this->InitMySQLdb();
		GEPython::CallModulFunction("ComplexServer.InitEx", "InitScript", "shh", pProcess->ProcessType().c_str(), pProcess->ProcessID(), pProcess->LisPort());
		return;
	}
	else
	{
		// 初始化脚本
		GEPython::CallModulFunction("ComplexServer.Init", "InitScript", NULL);
	}
	// 初始化C相关Python数据
	this->InitCPython();
	// 网络层一定要初始化好
	GE_ERROR(m_pNetWork != NULL);
	// 开始进入消息循环
	if (this->m_bPyThread)
	{
		this->m_pyFunction.Load("ComplexServer.Thread", "MainThreadCall");
		this->Loop_PyThread();
	}
	else
	{
		this->Loop();
	}
	// 清理脚本
	GEPython::CallModulFunction("ComplexServer.Init", "FinalScript", NULL);
	// 清理C数据
	this->FinalC();
	// 清理时间模块
	GEDateTime::Delete();
}

void ComplexServer::InitC()
{
	// 这里要初始化GUID64
	GEGUID64::Instance()->AllotFromNow();
	GEGUID64::Instance()->AllotPerMinute();

	// 初始化cServer模块（其依赖Python虚拟机）
	ServerPython::PyComplexServer_Init();
	ServerPython::PyGatewayForward_Init();
	ServerPython::PyRoleDataMgr_Init();
	ServerPython::PyRole_Init();
	ServerPython::PyRoleMgr_Init();
	ServerPython::PyLogTransaction_Init();
	ServerPython::PySceneMgr_Init();
	ServerPython::PyPublicScene_Init();
	ServerPython::PySingleMirrorScene_Init();
	ServerPython::PyMultiMirrorScene_Init();
	ServerPython::PyNPCMgr_Init();
	ServerPython::PyNPC_Init();
	ServerPython::PyScriptMgr_Init();
	
	// 初始化C单件
	SceneMgr::New();
	LogTransaction::New();
	ScriptHold::New();
	ScriptMgr::New();

	NPCMgr::New();

	ClientMgr::New();
	RoleDataMgr::New();
	RoleMgr::New();
	
	// 载入Python函数
	this->m_PyFunction_NewConnect.Load("ComplexServer.Connect", "OnNewConnect");
	this->m_PyFunction_LostConnect.Load("ComplexServer.Connect", "OnLostConnect");
}

void ComplexServer::InitCPython()
{

	SceneMgr::Instance()->LoadPyData();
	LogTransaction::Instance()->LoadPyData();
	ScriptHold::Instance()->LoadPyData();
	ScriptMgr::Instance()->LoadPyData();

	NPCMgr::Instance()->LoadPyData();

	ClientMgr::Instance()->LoadPyData();
	RoleDataMgr::Instance()->LoadPyData();
	RoleMgr::Instance()->LoadPyData();

	//载入所有配置数据后才开始创建相关的场景对象
	SceneMgr::Instance()->CreateAllPublicScene();
}


void ComplexServer::FinalC()
{
	RoleMgr::Delete();
	RoleDataMgr::Delete();
	ClientMgr::Delete();

	NPCMgr::Delete();

	ScriptMgr::Delete();
	ScriptHold::Delete();
	LogTransaction::Delete();
	SceneMgr::Delete();
}

void ComplexServer::Loop()
{
	// 毫秒计时器，用于计算每帧更新
	GEKeepMsec KMS;
	// 刷新时间
	GEDateTime::Instance()->Refresh();
	//网络层开始工作
	this->m_pNetWork->Start_L();
	// 网络层消息循环
	while(this->m_pNetWork->IsRun())
	{
		// 尝试获取下一条消息
		if (this->m_pNetWork->MoveNextMsg())
		{
			// 是连接断线消息，触发OnLost虚函数
			if (this->m_pNetWork->CurIsClose())
			{
				this->OnLost();
			}
			// 是网络消息，触发OnMsg虚函数
			else
			{
				this->OnMsg();
			}
		}
		// 网络层没有消息休眠1毫秒
		else
		{
			GEDateTime::Instance()->SleepMsec(1);
		}
		// 如果网络层的连接轮询了1轮
		if (this->m_pNetWork->CurIsRound())
		{
			// 刷新时间
			GEDateTime::Instance()->Refresh();
			// 检测是否是新的帧了
			if (KMS.HasPass(FRAME_MSECOND))
			{
				// 每帧更新
				this->Update();
			}
		}
	}
}

void ComplexServer::Loop_PyThread()
{
	// 毫秒计时器，应用计算每帧更新
	GEKeepMsec KMS;
	// 刷新时间
	GEDateTime::Instance()->Refresh();
	// 是否有网络消息
	bool hasNetMsg = false;
	//网络层开始工作
	this->m_pNetWork->Start_L();
	// 网络层消息循环
	while(this->m_pNetWork->IsRun())
	{
		// 获取网络消息，完全不关Python的事，可以交出GIL
		Py_BEGIN_ALLOW_THREADS
			hasNetMsg = this->m_pNetWork->MoveNextMsg();
		// 获取GIL，继续执行
		Py_END_ALLOW_THREADS
		// 尝试获取下一条消息
		if (hasNetMsg)
		{
			// 是连接断线消息，触发OnLost虚函数
			if (this->m_pNetWork->CurIsClose())
			{
				this->OnLost();
			}
			// 是网络消息，触发OnMsg虚函数
			else
			{
				this->OnMsg();
			}
		}
		// 网络层没有消息休眠1毫秒
		else
		{
			// Sleep完全不关Python的事
			Py_BEGIN_ALLOW_THREADS
				GEDateTime::Instance()->SleepMsec(1);
			Py_END_ALLOW_THREADS
		}
		// 如果网络层的连接轮询了1轮
		if (this->m_pNetWork->CurIsRound())
		{
			// 刷新时间
			GEDateTime::Instance()->Refresh();
			// 检测是否是新的帧了
			if (KMS.HasPass(FRAME_MSECOND))
			{
				// 处理其他线程对主线程的函数调用
				this->m_pyFunction.Call();
				// 每帧更新
				this->Update();
#if WIN
				while(GEDateTime::Instance()->Seconds() < this->m_uFastEndTime)
				{
					GEDateTime::Instance()->SetUnixTime(GEDateTime::Instance()->Seconds() + 1);
					this->Update();
				}
#endif
			}
		}
	}
}

void ComplexServer::Update()
{
	static GE::Uint32 lastSecond = GEDateTime::Instance()->Second();
	static GE::Uint32 lastMinute = GEDateTime::Instance()->Minute();
	static GE::Uint32 lastHour = GEDateTime::Instance()->Hour();
	static GE::Uint32 lastDay = GEDateTime::Instance()->Day();
	/*
	同一秒，忽视之
	注意，这里不会因为服务器卡而卡秒
	*/
	if (lastSecond == GEDateTime::Instance()->Second())
	{
		return;
	}
	lastSecond = GEDateTime::Instance()->Second();
	// 计算触发
	bool bIsNewMinute = lastMinute != GEDateTime::Instance()->Minute();
	bool bIsNewHour = false;
	bool bIsNewDay = false;
	if (bIsNewMinute)
	{
		lastMinute = GEDateTime::Instance()->Minute();
		bIsNewHour = lastHour != GEDateTime::Instance()->Hour();
		if (bIsNewHour)
		{
			lastHour = GEDateTime::Instance()->Hour();
			bIsNewDay = lastDay != GEDateTime::Instance()->Day();
			if (bIsNewDay)
			{
				lastDay = GEDateTime::Instance()->Day();
			}
		}
	}
	// 标记进入时间触发中
	this->m_bIsTimeDriver = true;
	// 触发事件函数调用
	if (bIsNewMinute)
	{
		if (bIsNewHour)
		{
			if (bIsNewDay)
			{
				this->CallBeforeNewDay();
			}
			this->CallBeforeNewHour();
		}
		this->CallBeforeNewMinute();
	}
	this->CallPerSecond();
	if (bIsNewMinute)
	{
		this->CallAfterNewMinute();
		if (bIsNewHour)
		{
			this->CallAfterNewHour();
			if (bIsNewDay)
			{
				this->CallAfterNewDay();
			}
		}
	}
	// 标记离开了时间触发
	this->m_bIsTimeDriver = false;
}

void ComplexServer::CallBeforeNewDay()
{
	this->m_PyFunctionCallBeforeNewDay.CallFunctions();
}

void ComplexServer::CallBeforeNewHour()
{
	this->m_PyFunctionCallBeforeNewHour.CallFunctions();
}

void ComplexServer::CallBeforeNewMinute()
{
	this->m_PyFunctionCallBeforeNewMinute.CallFunctions();
}

void ComplexServer::CallPerSecond()
{
	this->m_PyFunctionCallPerSecond.CallFunctions();
	this->m_pTick->CallPerSecond();
	this->m_pFastTick->CallPerSecond();
	RoleMgr::Instance()->CallPerSecond();
	SceneMgr::Instance()->CallPerSceond();
	ScriptMgr::Instance()->CallPerSecond();
}

void ComplexServer::CallAfterNewMinute()
{
	GEGUID64::Instance()->AllotPerMinute();
	
	this->m_PyFunctionCallAfterNewMinute.CallFunctions();

	RoleMgr::Instance()->CallAfterNewMinute();

	// 标记离开时间驱动
	bool bTimeDriver = this->m_bIsTimeDriver;
	this->m_bIsTimeDriver = false;
	// 检测是否要保存状态
	static GE::Uint32 uLastCheckMinut = GEProcess::Instance()->ProcessID();
	if (uLastCheckMinut % this->m_SaveGapMinute1 == 0)
	{
		// C++中数据的保存
		this->CallSave1();
	}
	if (uLastCheckMinut % this->m_SaveGapMinute2 == 0)
	{
		// C++中数据的保存
		this->CallSave2();
	}
	if (uLastCheckMinut % this->m_SaveGapMinute3 == 0)
	{
		// C++中数据的保存
		this->CallSave3();
	}
	++uLastCheckMinut;
	// 还原时间驱动标记
	this->m_bIsTimeDriver = bTimeDriver;;
}

void ComplexServer::CallAfterNewHour()
{
	this->m_PyFunctionCallAfterNewHour.CallFunctions();
}

void ComplexServer::CallAfterNewDay()
{
	this->m_PyFunctionCallAfterNewDay.CallFunctions();

	RoleMgr::Instance()->CallAfterNewDay();
}

void ComplexServer::CallSave1()
{
	// Python中数据的保存
	this->m_PyFunctionCallSave1.CallFunctions();
}

void ComplexServer::CallSave2()
{
	// Python中数据的保存
	this->m_PyFunctionCallSave2.CallFunctions();
}

void ComplexServer::CallSave3()
{
	// Python中数据的保存
	this->m_PyFunctionCallSave3.CallFunctions();
}

void ComplexServer::CreateNetwork( GE::Uint32 uMaxConnect, GE::Uint16 uThread )
{
	this->m_pNetWork = new GENetWork(uMaxConnect, uThread);
}

void ComplexServer::Listen( GE::Uint32 uPort )
{
	this->m_pNetWork->Listen_L(uPort);
}

void ComplexServer::SetConnectParam( ConnectParam& CP )
{
	this->m_pNetWork->SetParam_L(CP);
}
void ComplexServer::StopNetwork()
{
	this->m_pNetWork->Stop_L();
}

GE::Uint32 ComplexServer::Connect( const char* sIP, GE::Uint32 uPort, GE::Uint16 uWho, ConnectParam* pCP /*= NULL*/ )
{
	// 注意，这里首先将SessionID设置为非法的
	GE::Uint32 uSessionID = MAX_UINT32;
	if (this->m_pNetWork->Connect_L(sIP, uPort, uSessionID, pCP))
	{
		/*
		注意，这里使用了一个潜规则，被动 = 主动 + 1
		*/
		GE::B4 b4;
		b4.UI16_0() = uWho + 1;
		b4.UI16_1() = GEProcess::Instance()->ProcessID();
		MsgWho msg;
		msg.uWho = b4.UI32();
		this->SendMsg(uSessionID, &msg);
		// 通知脚本
		GEPython::Object ret = this->m_PyFunction_NewConnect.CallAndResult("IHH", uSessionID, uWho, GEProcess::Instance()->ProcessID());
		// 设置连接信息
		this->m_pNetWork->SetConnectInfo_L(uSessionID, uWho, GEPython::PyObjFromUI32(uSessionID), GEPython::PyObjFromUI32(uWho));
		if (!ret.IsTrue())
		{
			GE_EXC<<"session("<<uSessionID<<") connect with error who("<<uWho<<")."<<GE_END;
			this->DisConnect(uSessionID, enDisConnect_WhoError);
			return MAX_UINT32;
		}
	}
	return uSessionID;
}

void ComplexServer::DisConnect( GE::Uint32 uSessionID, GE::Uint16 uReason )
{
	this->m_pNetWork->DisConnect_L(uSessionID);
}

bool ComplexServer::HasConnect( GE::Uint32 uSessionID )
{
	return this->m_pNetWork->HasConnect(uSessionID);
}

void ComplexServer::SetConnectForward( GE::Uint32 uSessionID )
{
	this->m_pNetWork->SetConnectForward_L(uSessionID);
}

void ComplexServer::OnLost( )
{
	// 还没表明身份就断线了，忽视之
	if (this->m_pNetWork->CurWho() == 0)
	{
		this->m_pNetWork->CurWho() = MAX_UINT16;
		return;
	}
	// 已经处理过了，忽视之
	if (this->m_pNetWork->CurWho() == MAX_UINT16)
	{
		return;
	}
	// 通知脚本
	this->m_PyFunction_LostConnect.Call("IH", this->m_pNetWork->CurSessionID(), this->m_pNetWork->CurWho());
	// 解除绑定缓存
	Py_XDECREF(this->m_pNetWork->CurPySessionID());
	Py_XDECREF(this->m_pNetWork->CurPyWho());
	// 标识处理完毕
	this->m_pNetWork->CurWho() = MAX_UINT16;
}

void ComplexServer::OnMsg( )
{	
	// 记录最后一条处理消息的时间
	this->m_uLastMsgTime = GEDateTime::Instance()->Seconds();

	MsgBase* pMsg = this->m_pNetWork->CurMsg();
	GE::Uint32 uSession = this->m_pNetWork->CurSessionID();
	// 只有这一条消息对身份的要求特殊（必须为0）
	if (pMsg->Type() == enProcessMsg_Who)
	{
		// 消息长度错误，T掉连接
		if (pMsg->Size() < sizeof(MsgWho))
		{
			GE_EXC<<"session("<<uSession<<") msg size("<<pMsg->Size()<<") < type("<<enProcessMsg_Who<<") size("<<sizeof(MsgWho)<<")."<<GE_END;
			this->DisConnect(uSession, enDisConnect_MsgConverError);
			return;
		}
		// 重复表明身份，T掉连接
		MsgWho* pMW = static_cast<MsgWho*>(pMsg);
		if (this->m_pNetWork->CurWho())
		{
			GE_EXC<<"session("<<uSession<<") with who("<<this->m_pNetWork->CurWho()<<") recv who("<<pMW->uWho<<")."<<GE_END;
			this->DisConnect(uSession, enDisConnect_RepeatWho);
			return;
		}
		GE::B4& b4 = GE_AS_B4(pMW->uWho);
		GE::Uint16 uWho = b4.UI16_0();
		GE::Uint16 uProcessID = b4.UI16_1();
		// 通知脚本
		GEPython::Object ret = this->m_PyFunction_NewConnect.CallAndResult("IHH", uSession, uWho, uProcessID);
		if (!ret.IsTrue())
		{
			GE_EXC<<"session("<<uSession<<") recv error who("<<uWho<<")."<<GE_END;
			this->DisConnect(uSession, enDisConnect_WhoError);
			return;
		}
		// 绑定身份
		this->m_pNetWork->CurWho() = uWho;
		// 绑定缓存
		this->m_pNetWork->CurPySessionID() = GEPython::PyObjFromUI32(uSession);
		this->m_pNetWork->CurPyWho() = GEPython::PyObjFromUI32(uWho);
		return;
	}
	
	// 按照身份分发消息
	this->DoWho();
}

bool ComplexServer::IsSendOver( GE::Uint32 uSessionID )
{
	return this->m_pNetWork->IsSendOver_L(uSessionID);
}

void ComplexServer::SendMsg( GE::Uint32 uSessionID, MsgBase* pMsg )
{
	this->m_pNetWork->SendBytes_L(uSessionID, pMsg, pMsg->Size());
}

void ComplexServer::BroadMsg(GE::Uint16 uWho, MsgBase* pMsg)
{
	this->m_pNetWork->BroadBytes(uWho, pMsg, pMsg->Size());
}

void ComplexServer::SendBytes( GE::Uint32 uSessionID, void* pHead, GE::Uint16 uSize )
{
	// 未开启了网络拼包功能不能发送不完整的消息
	if (!GENetEnv::Instance()->CanCombineMsg())
	{
		GE_EXC<<"can't use SendBytes function on !CanCombineMsg."<<GE_END;
		return;
	}
	this->m_pNetWork->SendBytes_L(uSessionID, pHead, uSize);
}

void ComplexServer::BroadBytes( GE::Uint16 uWho, void* pHead, GE::Uint16 uSize )
{
	// 未开启了网络拼包功能不能发送不完整的消息
	if (!GENetEnv::Instance()->CanCombineMsg())
	{
		GE_EXC<<"can't use SendBytes function on !CanCombineMsg."<<GE_END;
		return;
	}
	this->m_pNetWork->BroadBytes(uWho, pHead, uSize);
}

void ComplexServer::SendPyMsg( GE::Uint32 uSessionID, GE::Uint16 uMsgType, PyObject* msg_BorrowRef )
{
	PackMessage PM;
	MsgBase MB(uMsgType);
	PM.PackMsg(&MB, MB.Size());
	PM.PackPyObj(msg_BorrowRef);
	if (PM.HasError())
	{
		GEProcess::Instance()->PyStackWarn("send py msg has error.");
		return;
	}
	this->SendMsg(uSessionID, PM.Msg());
}

void ComplexServer::SendPyMsgAndBack( GE::Uint32 uSessionID, GE::Uint16 uMsgType, PyObject* msg_BorrowRef, GE::Uint32 uSec, PyObject* cbfun_BorrowRef, PyObject* regparam_BorrowRef )
{
	PackMessage PM;
	MsgBase MB(uMsgType);
	PM.PackMsg(&MB, MB.Size());
	GE::Int64 uTickID = 0;
	// 如果没回调函数就不用注册Tick了
	if (cbfun_BorrowRef != Py_None)
	{
		uTickID = this->m_pTick->RegTick(uSec, cbfun_BorrowRef, regparam_BorrowRef);
	}
	PM.PackSpe1(uTickID, msg_BorrowRef);
	if (PM.HasError())
	{
		GEProcess::Instance()->PyStackWarn("send py msg and back has error.");
		return;
	}
	this->SendMsg(uSessionID, PM.Msg());
}

void ComplexServer::CallBackFunction( GE::Uint32 uSessionID, GE::Int64 ID, PyObject* arg_BorrowRef )
{
	PackMessage PM;
	MsgBase MB(enProcessMsg_ServerCallBack);
	PM.PackMsg(&MB, MB.Size());
	PM.PackI64(ID);
	PM.PackPyObj(arg_BorrowRef);
	if (PM.HasError())
	{
		GEProcess::Instance()->PyStackWarn("call back function has error.");
		return;
	}
	this->SendMsg(uSessionID, PM.Msg());
}

void ComplexServer::RegDistribute( GE::Uint16 uMsgType, PyObject* fun_borrorRef )
{
	PyMsgDistribute::iterator iter = this->m_PyMsgDistribute.find(uMsgType);
	if (iter == this->m_PyMsgDistribute.end())
	{
		Py_INCREF(fun_borrorRef);
		this->m_PyMsgDistribute.insert(std::make_pair(uMsgType, fun_borrorRef));
	}
	else
	{
		GE_EXC<<"repeat RegDistribute uMsgType("<<uMsgType<<")."<<GE_END;
	}
}

void ComplexServer::UnregDistribute( GE::Uint16 uMsgType )
{
	PyMsgDistribute::iterator iter = this->m_PyMsgDistribute.find(uMsgType);
	if (iter != this->m_PyMsgDistribute.end())
	{
		Py_DECREF(iter->second);
		this->m_PyMsgDistribute.erase(iter);
	}
}

PyObject* ComplexServer::GetDistribute_NewRef( GE::Uint16 uMsgType )
{
	PyObject* pyo = Py_None;
	PyMsgDistribute::iterator iter = this->m_PyMsgDistribute.find(uMsgType);
	if (iter != this->m_PyMsgDistribute.end())
	{
		pyo = iter->second;
	}
	Py_INCREF(pyo);
	return pyo;
}

bool ComplexServer::DoWho()
{
	MsgBase* pMsg = this->m_pNetWork->CurMsg();
	GE::Uint32 uSession = this->m_pNetWork->CurSessionID();
	GE::Uint16 uWho = this->m_pNetWork->CurWho();

	// 按照身份分发消息
	switch(uWho)
	{
	case enWho_None:
		{
			GE_EXC<<"session("<<this->m_pNetWork->CurSessionID()<<") without who recv msg("<<this->m_pNetWork->CurMsg()->Type()<<")."<<GE_END;
			this->DisConnect(this->m_pNetWork->CurSessionID(), enDisConnect_NoWho);
			break;
		}
	case enWho_Client_:
		{
			WhoClient_::Instance()->OnClientMsg(uSession, pMsg);
			break;
		}
	case enWho_Gateway:
		{
			WhoClient_::Instance()->OnGatewayMsg(uSession, pMsg);
			break;
		}
	case enWho_Gateway_:
		{
			WhoGateway_::Instance()->OnGatewayMsg(uSession, pMsg);
			break;
		}
	default:
		{
			this->DoMsg();
			break;
		}
	}
	return true;
}

bool ComplexServer::DoMsg()
{
	MsgBase* pMsg = this->m_pNetWork->CurMsg();
	GE::Uint32 uSession = this->m_pNetWork->CurSessionID();
	GE::Uint16 uWho = this->m_pNetWork->CurWho();

	// 按照消息类型分发消息
	switch(pMsg->Type())
	{
	case enGEMsg_Ping:
		{
			break;
		}
	case enProcessMsg_Echo:
		{
			this->SendMsg(uSession, pMsg);
			break;
		}
	case enProcessMsg_ServerCallBack:
		{
			if (!this->DoCurCallBackFunction())
			{
				GE_EXC<<"session("<<this->m_pNetWork->CurSessionID()<<") recv unknown msg("<<pMsg->Type()<<")."<<GE_END;
				// 如果是客户端发送了不能处理的消息，T之
				if (uWho == enWho_Client_)
				{
					this->DisConnect(uSession, enDisConnect_UnknownCallBack);
				}
			}
			break;
		}
	default:
		{
			// 默认处理下
			if (!this->DoCurDistribute())
			{
				GE_EXC<<"session("<<this->m_pNetWork->CurSessionID()<<") recv unknown msg("<<pMsg->Type()<<")."<<GE_END;
				// 如果是客户端发送了不能处理的消息，T之
				if (uWho == enWho_Client_)
				{
					this->DisConnect(uSession, enDisConnect_UnknownMsg);
				}
			}
			break;
		}
	}
	return true;
}

bool ComplexServer::DoCallBackFunction( GE::Int64 uTickID, PyObject* borrowRef )
{
	this->m_pTick->TriggerTick(uTickID, borrowRef);
	return true;
}

bool ComplexServer::DoDistribute( GE::Uint16 uMsgType, PyObject* borrowRef )
{
	PyMsgDistribute::iterator iter = this->m_PyMsgDistribute.find(uMsgType);
	if (iter == this->m_PyMsgDistribute.end())
	{
		GE_EXC<<"can't distribute server msg("<<uMsgType<<")."<<GE_END;
		return false;
	}
	/*
	Return value: New reference.
	Call a callable Python object callable, with a variable number of C arguments.
	Returns the result of the call on success, or NULL on failure.
	*/
	PyObject* pyResult_NewRef = PyObject_CallFunction(iter->second, const_cast<char*>("IO"), m_pNetWork->CurSessionID(), borrowRef);
	if (NULL == pyResult_NewRef)
	{
		PyErr_Print();
	}
	else
	{
		Py_DECREF(pyResult_NewRef);
	}
	return true;
}


bool ComplexServer::DoCurDistribute( )
{
	MsgBase* pMsg = this->m_pNetWork->CurMsg();
	
	GEPython::Object pyobj;
	UnpackMessage UM(pMsg);
	UM.UnpackMsg(sizeof(MsgBase));
	if (!UM.UnpackPyObj(pyobj))
	{
		GE_EXC<<"can't UnpackPyObj server msg("<<pMsg->Type()<<")."<<GE_END;
		return false;
	}
	return this->DoDistribute(pMsg->Type(), pyobj.GetObj_BorrowRef());
}



bool ComplexServer::DoCurCallBackFunction( )
{
	MsgBase* pMsg = this->m_pNetWork->CurMsg();
#ifdef WIN
	GE_ERROR(pMsg->Type() == enProcessMsg_ServerCallBack);
#endif
	GE::Int64 uTickID = 0;
	GEPython::Object obj;
	UnpackMessage UM(pMsg);
	UM.UnpackMsg(sizeof(MsgBase));
	UM.UnpackI64(uTickID);
	UM.UnpackPyObj(obj);
	if (UM.HasError())
	{
		GE_EXC<<"unpack server call back error."<<GE_END;
		return false;
	}
	return this->DoCallBackFunction(uTickID, obj.GetObj_BorrowRef());
}

void ComplexServer::InitMySQLdb()
{
	init_mysql();
}

bool ComplexServer::RemoteEndPoint( GE::Uint32 uSessionID, std::string& sIP, GE::Uint32& uPort )
{
	return this->m_pNetWork->RemoteEndPoint(uSessionID, sIP, uPort);
}



