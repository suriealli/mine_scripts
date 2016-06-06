/************************************************************************
乱七八糟的定义
************************************************************************/
#pragma once
#include "../GameEngine/GENetConnect.h"

#define CLIENT_MESSAGE_BEGIN 768
#define CLIENT_MESSAGE_END 777

// 断开连接的原因
enum DisconnectReason
{
	enDisConnect_RemoteClose = enNetConnect_RemoteClose,
	enDisConnect_MsgError = enNetConnect_MsgError,
	enDisConnect_SendBufFull = enNetConnect_SendBufFull,
	enDisConnect_RecvBufFull = enNetConnect_RecvBufFull,
	enDisConnect_ConnectFull = enNetConnect_ConnectFull,
	enDisConnect_MsgConverError,
	enDisConnect_RepeatWho,
	enDisConnect_WhoError,
	enDisConnect_NoWho,
	enDisConnect_UnknownMsg,
	enDisConnect_UnknownCallBack,
	enDisConnect_NoInit,
	enDisConnect_Logic,
};

/*
TCP端点的类型
注意，这里使用了一个潜规则，被动 = 主动 + 1
*/
enum EndPointType
{
	enWho_None,					//占位
	enWho_Client,				//客户端（主动）
	enWho_Client_,				//客户端（被动）
	enWho_GM,					//GM工具（主动）
	enWho_GM_,					//GM工具（被动）
	enWho_Gateway,				//网关（主动）
	enWho_Gateway_,				//网关（被动）
	enWho_Http,					//HTTP（主动）
	enWho_Http_,				//HTTP（被动）
	enWho_Logic,				//逻辑（主动）
	enWho_Logic_,				//逻辑（被动）
	enWho_Control,				//控制（主动）
	enWho_Control_,				//控制（被动）
};


