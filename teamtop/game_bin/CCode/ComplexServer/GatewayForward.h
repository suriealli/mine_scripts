/************************************************************************
网关导向
************************************************************************/
#pragma once
#include <boost/unordered_set.hpp>
#include "../GameEngine/GameEngine.h"

class WhoClient_
	: public GESingleton<WhoClient_>
{
public:
	WhoClient_();
	~WhoClient_();

public:
	void					OnClient_New(GE::Uint32 uSessionID);
	void					OnClient_Lost(GE::Uint32 uSessionID);
	void					OnGatewayNew(GE::Uint32 uSessionID);
	void					OnGatewayLost(GE::Uint32 uSessionID);

	void					OnClientMsg(GE::Uint32 uSessionID, MsgBase* pMsg);
	void					SendClientMsg(GE::Uint64 uClientKey, MsgBase* pMsg);
	void					BroadClientMsg(GE::Uint32 uWho, MsgBase* pMsg);
	void					KickClient(GE::Uint64 uClientKey);

	void					OnGatewayMsg(GE::Uint32 uSessionID, MsgBase* pMsg);

private:
	bool					IsGateway() {return m_uGatewaySessionID != MAX_UINT32;}

private:
	GE::Uint32				m_uGatewaySessionID;
};


class WhoGateway_
	: public GESingleton<WhoGateway_>
{
	typedef boost::unordered_set<GE::Uint32>		SessionSet;
public:
	WhoGateway_();
	~WhoGateway_();

public:
	bool					HasGateway() {return m_bHasGateway;}
	void					UseGateway() {m_bHasGateway = true;}

	void					OnGateway_New(GE::Uint32 uSessionID);
	void					OnGateway_Lost(GE::Uint32 uSessionID);

	void					OnGatewayMsg(GE::Uint32 uSessionID, MsgBase* pMsg);
	void					SendClientMsg(GE::Uint64 uClientKey, MsgBase* pMsg);
	void					BroadClientMsg(GE::Uint32 uWho, MsgBase* pMsg);
	void					KickClient(GE::Uint64 uClientKey);

private:
	bool					m_bHasGateway;
	SessionSet				m_SessionSet;
};

class ClientMgr
	: public GEControlSingleton<ClientMgr>
{
public:
	ClientMgr();
	~ClientMgr();

	void					LoadPyData();
public:
	void					OnClientNew(GE::Uint64 uClientKey);
	void					OnClientLost(GE::Uint64 uClientKey);
	void					OnClientMsg(GE::Uint64 uClientKey, MsgBase* pMsg);
	void					SendClientMsg(GE::Uint64 uClientKey, MsgBase* pMsg);
	void					BroadClientMsg(MsgBase* pMsg);
	void					KickClient(GE::Uint64 uClientKey);

private:
	GEPython::Function		m_pyClientNewFun;
	GEPython::Function		m_pyClientLostFun;
	GEPython::Function		m_pyClientMsgFun;
};

