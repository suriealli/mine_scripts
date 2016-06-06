/*我是UTF8无签名编码 */
#include <sstream>
#include "GatewayForward.h"
#include "ComplexServer.h"
#include "ClutterDefine.h"
#include "MessageDefine.h"
#include "RoleMgr.h"
//////////////////////////////////////////////////////////////////////////
// WhoClient_
//////////////////////////////////////////////////////////////////////////
WhoClient_::WhoClient_()
	: m_uGatewaySessionID(MAX_UINT32)
{

}

WhoClient_::~WhoClient_()
{

}

void WhoClient_::OnClient_New( GE::Uint32 uSessionID )
{
	if (this->IsGateway())
	{
		MsgNewClient msg;
		msg.uClientSessionID = uSessionID;
		ComplexServer::Instance()->SetConnectForward(uSessionID);
		ComplexServer::Instance()->SendMsg(this->m_uGatewaySessionID, &msg);
	}
	else
	{
		GE::B8 ClientKey(uSessionID, MAX_UINT32);
		ClientMgr::Instance()->OnClientNew(ClientKey.UI64());
	}
	// 告诉客户端OK了（这里告诉一个时间，用于加密）
	std::stringstream ss;
	GEDateTime* pDT = GEDateTime::Instance();
	ss<<pDT->Year()<<"-"<<pDT->Month()<<"_"<<pDT->Day()<<" "<<pDT->Hour()<<":"<<pDT->Minute()<<":"<<pDT->Second();
	const std::string& str = ss.str();
	PackMessage PM;
	PM.PackMsg(enProcessMsg_OKClient);// 跑完流程了
	PM.PackStream_1(str.data(), static_cast<GE::Uint8>(str.length()));
	ComplexServer::Instance()->SendMsg(uSessionID, PM.Msg());
}

void WhoClient_::OnClient_Lost( GE::Uint32 uSessionID )
{
	if (this->IsGateway())
	{
		MsgLostClient msg;
		msg.uClientSessionID = uSessionID;
		ComplexServer::Instance()->SetConnectForward(uSessionID);
		ComplexServer::Instance()->SendMsg(this->m_uGatewaySessionID, &msg);
	}
	else
	{
		GE::B8 ClientKey(uSessionID, MAX_UINT32);
		ClientMgr::Instance()->OnClientLost(ClientKey.UI64());
	}
}

void WhoClient_::OnGatewayNew( GE::Uint32 uSessionID )
{
#ifdef WIN
	GE_ERROR(this->m_uGatewaySessionID == MAX_UINT32);
#endif
	this->m_uGatewaySessionID = uSessionID;
}

void WhoClient_::OnGatewayLost( GE::Uint32 uSessionID )
{
#ifdef WIN
	GE_ERROR(this->m_uGatewaySessionID == uSessionID);
#endif
	this->m_uGatewaySessionID = MAX_UINT32;
}

void WhoClient_::OnClientMsg( GE::Uint32 uSessionID, MsgBase* pMsg )
{
	if (this->IsGateway())
	{
		GE_EXC<<"recv client msg on gateway process."<<GE_END;
	}
	else
	{
		GE::B8 ClientKey(uSessionID, MAX_UINT32);
		ClientMgr::Instance()->OnClientMsg(ClientKey.UI64(), pMsg);
	}
}

void WhoClient_::SendClientMsg( GE::Uint64 uClientKey, MsgBase* pMsg )
{
	if (this->IsGateway())
	{
		GE_EXC<<"send client msg on gateway process."<<GE_END;
	}
	else
	{
		GE::B8& ClientKey = GE_AS_B8(uClientKey);
#ifdef WIN
		GE_ERROR(ClientKey.UI32_1() == MAX_UINT32);
#endif
		ComplexServer::Instance()->SendMsg(ClientKey.UI32_0(), pMsg);
	}
}

void WhoClient_::BroadClientMsg( GE::Uint32 uWho, MsgBase* pMsg )
{
	if (this->IsGateway())
	{
		GE_EXC<<"send client msg on gateway process."<<GE_END;
	}
	else
	{
		ComplexServer::Instance()->BroadMsg(static_cast<GE::Uint16>(uWho), pMsg);
	}
}

void WhoClient_::KickClient( GE::Uint64 uClientKey )
{
	if (this->IsGateway())
	{
		GE_EXC<<"kick client on gateway process."<<GE_END;
	}
	else
	{
		GE::B8& ClientKey = GE_AS_B8(uClientKey);
#ifdef WIN
		GE_ERROR(ClientKey.UI32_1() == MAX_UINT32);
#endif
		ComplexServer::Instance()->DisConnect(ClientKey.UI32_0(), enDisConnect_Logic);
	}
}

void WhoClient_::OnGatewayMsg( GE::Uint32 uSessionID, MsgBase* pMsg )
{
	if (!this->IsGateway())
	{
		GE_EXC<<"recv gateway msg but not gateway."<<GE_END;
		return;
	}
#ifdef WIN
	GE_ERROR(uSessionID == m_uGatewaySessionID);
#endif
	switch(pMsg->Type())
	{
	case enProcessMsg_KickClient:
		{
			// 这条消息是服务端发的，没严格检查
			MsgKickClient* pNMsg = static_cast<MsgKickClient*>(pMsg);
			ComplexServer::Instance()->DisConnect(pNMsg->uClientSesionID, enDisConnect_Logic);
			break;
		}
	default:
		{
			GE_EXC<<"gateway recv unknown msg("<<pMsg->Type()<<")."<<GE_END;
			break;
		}
	}
}

//////////////////////////////////////////////////////////////////////////
// WhoGateway_
//////////////////////////////////////////////////////////////////////////
WhoGateway_::WhoGateway_()
	: m_bHasGateway(false)
{

}

WhoGateway_::~WhoGateway_()
{

}

void WhoGateway_::OnGateway_New( GE::Uint32 uSessionID )
{
	if (!this->HasGateway())
	{
		GE_EXC<<"gateway_ new without gateway"<<GE_END;
		return;
	}
	SessionSet::const_iterator citer = this->m_SessionSet.find(uSessionID);
	if (citer == this->m_SessionSet.end())
	{
		this->m_SessionSet.insert(uSessionID);
	}
	else
	{
		GE_EXC<<"repeat gateway_ session("<<uSessionID<<")."<<GE_END;
	}
}

void WhoGateway_::OnGateway_Lost( GE::Uint32 uSessionID )
{
	if (!this->HasGateway())
	{
		GE_EXC<<"gateway_ lost without gateway"<<GE_END;
		return;
	}
	SessionSet::const_iterator citer = this->m_SessionSet.find(uSessionID);
	if (citer == this->m_SessionSet.end())
	{
		GE_EXC<<"can't find gateway_ session("<<uSessionID<<")."<<GE_END;
	}
	else
	{
		this->m_SessionSet.erase(citer);
	}
}

void WhoGateway_::OnGatewayMsg( GE::Uint32 uSessionID, MsgBase* pMsg )
{
	if (!this->HasGateway())
	{
		GE_EXC<<"gateway_ msg without gateway"<<GE_END;
		return;
	}
	switch (pMsg->Type())
	{
	case enProcessMsg_NewClient:
		{
			// 这条消息是服务端发送过来的，没做严密检测
			MsgNewClient* pNMsg = static_cast<MsgNewClient*>(pMsg);
			GE::B8 ClientKey(pNMsg->uClientSessionID, uSessionID);
			ClientMgr::Instance()->OnClientNew(ClientKey.UI64());
			break;
		}
	case enProcessMsg_LostClient:
		{
			// 这条消息是服务端发送过来的，没做严密检测
			MsgLostClient* pNMsg = static_cast<MsgLostClient*>(pMsg);
			GE::B8 ClientKey(pNMsg->uClientSessionID, uSessionID);
			ClientMgr::Instance()->OnClientLost(ClientKey.UI64());
			break;
		}
	case enGEMsg_Forward_From:
		{
			// 这条消息是服务端发送过来的，没做严密检测
			MsgForwardFrom* pFMsg = static_cast<MsgForwardFrom*>(pMsg);
			MsgBase* pNMsg = static_cast<MsgBase*>(static_cast<void*>((char*)(pFMsg) + sizeof(MsgForwardFrom)));
#ifdef WIN
			GE_ERROR(pMsg->Size() + sizeof(MsgForwardFrom) == pFMsg->Size());
#endif
			GE::B8 ClientKey(pFMsg->uSessionID, uSessionID);
			ClientMgr::Instance()->OnClientMsg(ClientKey.UI64(), pNMsg);
			break;
		}
	default:
		{
			GE_EXC<<"gateway_ recv unknown msg("<<pMsg->Type()<<")."<<GE_END;
			break;
		}
	}	
}

void WhoGateway_::SendClientMsg( GE::Uint64 uClientKey, MsgBase* pMsg )
{
	if (!this->HasGateway())
	{
		GE_EXC<<"send client msg without gateway"<<GE_END;
		return;
	}
	GE::B8& ClientKey = GE_AS_B8(uClientKey);
#ifdef WIN
	GE_ERROR(ClientKey.UI32_1() != MAX_UINT32);
#endif
	// 网络层拼包
	MsgForwardTo msg;
	msg.uSessionID = ClientKey.UI32_0();
	msg.AddSize(pMsg->Size());
	ComplexServer::Instance()->SendBytes(ClientKey.UI32_1(), &msg, sizeof(msg));
	ComplexServer::Instance()->SendBytes(ClientKey.UI32_1(), pMsg, pMsg->Size());
}

void WhoGateway_::BroadClientMsg( GE::Uint32 uWho, MsgBase* pMsg )
{
	if (!this->HasGateway())
	{
		GE_EXC<<"broad client msg without gateway"<<GE_END;
		return;
	}
	// 网络层拼包
	MsgForwardOther msg;
	msg.uWho = uWho;
	msg.AddSize(pMsg->Size());

	SessionSet::iterator iter = this->m_SessionSet.begin();
	for(; iter != this->m_SessionSet.end(); ++iter)
	{
		ComplexServer::Instance()->SendBytes(*iter, &msg, sizeof(msg));
		ComplexServer::Instance()->SendBytes(*iter, pMsg, pMsg->Size());
	}
}

void WhoGateway_::KickClient( GE::Uint64 uClientKey )
{
	if (!this->HasGateway())
	{
		GE_EXC<<"kick client without gateway"<<GE_END;
		return;
	}
	GE::B8& ClientKey = GE_AS_B8(uClientKey);
#ifdef WIN
	GE_ERROR(ClientKey.UI32_1() != MAX_UINT32);
#endif
	MsgKickClient msg;
	msg.uClientSesionID = ClientKey.UI32_0();
	ComplexServer::Instance()->SendMsg(ClientKey.UI32_1(), &msg);
}

//////////////////////////////////////////////////////////////////////////
// ClientMgr
//////////////////////////////////////////////////////////////////////////
ClientMgr::ClientMgr()
{
	
}

ClientMgr::~ClientMgr()
{

}

void ClientMgr::OnClientNew( GE::Uint64 uClientKey )
{
	this->m_pyClientNewFun.Call("(K)", uClientKey);
}

void ClientMgr::OnClientLost( GE::Uint64 uClientKey )
{
	this->m_pyClientLostFun.Call("(K)", uClientKey);
}

void ClientMgr::OnClientMsg( GE::Uint64 uClientKey, MsgBase* pMsg )
{
	// 这里写了个潜规则，因为没做好区分客户端发送来的消息是否有对应的角色对象
	if (pMsg->Type() >= CLIENT_MESSAGE_BEGIN && pMsg->Type() <= CLIENT_MESSAGE_END)
	{
		GEPython::Object obj;
		UnpackMessage UM(pMsg);
		UM.UnpackMsg(sizeof(MsgBase));
		UM.UnpackPyObj(obj);
		this->m_pyClientMsgFun.Call("KHO", uClientKey, pMsg->Type(), obj.GetObj_BorrowRef());
	}
	else
	{
		RoleMgr::Instance()->OnClientMsg(uClientKey, pMsg);
	}
}

void ClientMgr::SendClientMsg( GE::Uint64 uClientKey, MsgBase* pMsg )
{
	if (WhoGateway_::Instance()->HasGateway())
	{
		WhoGateway_::Instance()->SendClientMsg(uClientKey, pMsg);
	}
	else
	{
		WhoClient_::Instance()->SendClientMsg(uClientKey, pMsg);
	}
}

void ClientMgr::BroadClientMsg( MsgBase* pMsg )
{
	if (WhoGateway_::Instance()->HasGateway())
	{
		WhoGateway_::Instance()->BroadClientMsg(enWho_Client_, pMsg);
	}
	else
	{
		WhoClient_::Instance()->BroadClientMsg(enWho_Client_, pMsg);
	}
}

void ClientMgr::KickClient( GE::Uint64 uClientKey )
{
	if (WhoGateway_::Instance()->HasGateway())
	{
		WhoGateway_::Instance()->KickClient(uClientKey);
	}
	else
	{
		WhoClient_::Instance()->KickClient(uClientKey);
	}
}

void ClientMgr::LoadPyData()
{
	this->m_pyClientNewFun.Load("ComplexServer.Plug.Gateway.ClientMgr", "OnClientNew");
	this->m_pyClientLostFun.Load("ComplexServer.Plug.Gateway.ClientMgr", "OnClientLost");
	this->m_pyClientMsgFun.Load("ComplexServer.Plug.Gateway.ClientMgr", "OnClientMsg");
}

