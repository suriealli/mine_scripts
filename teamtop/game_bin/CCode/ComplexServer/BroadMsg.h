/************************************************************************
广播消息
************************************************************************/
#pragma once
#include "../GameEngine/GameEngine.h"

class BoradMsg
	: public GEControlSingleton<BoradMsg>
{
public:
	BoradMsg();
	~BoradMsg();

public:
	void				OnClientBroadMsg(MsgBase* pMsg);
	void				BroadOneClientMsg(GE::Uint64 uClientKey, GE::Uint32 uI1, GE::Uint32 uI2, const char* pHead, GE::Uint16 uSize);
	void				BroadAllClientMsg(GE::Uint32 uI1, GE::Uint32 uI2, const char* pHead, GE::Uint16 uSize);
};

