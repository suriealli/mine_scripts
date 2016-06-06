/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "../GameEngine/GENetMessage.h"

//设置4字节对齐
#pragma pack(push)
#pragma pack(4)


// 进程间消息
enum ProcessMsgType
{
	enProcessMsg_Echo = 256,				//回显消息
	enProcessMsg_Who,						//表明身份的消息
	enProcessMsg_ServerCallBack,			//进程间消息回调
	enProcessMsg_OKClient,					//告诉客户端OK
	enProcessMsg_NewClient,					//新的客户端
	enProcessMsg_LostClient,				//失去客户端
	enProcessMsg_KickClient,				//踢掉客户端

	enProcessMsg_RoleCallBack,				//角色消息回调
	enProcessMsg_RoleSyncInt64,				//同步Int64数组
	enProcessMsg_RoleSyncDisperseInt32,		//同步DisperseInt32数组
	enProcessMsg_RoleSyncInt32,				//同步Int32数组
	enProcessMsg_RoleSyncInt16,				//同步Int16数组
	enProcessMsg_RoleSyncInt8,				//同步Int8数组
	enProcessMsg_RoleSyncDayInt8,			//同步DayInt8数组
	enProcessMsg_RoleSyncInt1,				//同步Int1数组
	enProcessMsg_RoleSyncDayInt1,			//同步DayInt1数组
	enProcessMsg_RoleSyncDynamicInt64,		//同步DynamicInt64数组
	enProcessMsg_RoleSyncClientInt8,		//同步ClientInt8数组
	enProcessMsg_RoleSyncTempInt64,			//同步TempInt64数组
	enProcessMsg_RoleSyncCD,				//同步CD数组

	enProcessMsg_RoleSyncDataBase,			//同步角色基础数据
	enProcessMsg_RoleSyncOK,				//同步角色数据成功
	enProcessMsg_RoleSyncProperty,			//同步角色属性
	enProcessMsg_RoleSyncHeroProperty,		//同步英雄属性

	enProcessMsg_RoleStartTransaction,		//开启事务
	enProcessMsg_RoleEndTransaction,		//关闭事务

	enRoleToTargetPos,						//客户端请求到达某个目标点
	enRoleMovePos,							//客户端同步自己移动的位置
	
	enSyncRoleTargerPos,					//向其他玩家同步一个玩家的目标点，当前点
	enSyncRoleNowPos,						//向其他玩家同步一个玩家的当前点,(目标点默认0,0 即静止玩家)
	enSyncRoleDisappear,					//同步一个玩家消失了

	enSyncRoleIdle,							//服务器拉停玩家
	enSyncRoleScenePos,						//通知客户端要到达哪个场景哪个坐标

	enSyncRoleVersion,						//同步一个玩家的版本号

	enSyncRoleAppreanceData,				//同步一个玩家外观数据
	enCheckRoleAppearanceData,				//查看一个玩家外观数据

	enSyncBroadcastNPC,						//同步广播的NPC消息

	enNPCPos,								//同步一个NPC位置消息
	enNPCMovingPos,							//同步一个移动中的NPC消息

	enNPCDisappear,							//同步一个NPC消失了

	enNPCClick,								//点击一个NPC
	enRoleFlyState,							//同步飞行标志状态

	enClientCharMsg,						//从客户端发来的字符消息
	enServerCharMsg,						//由服务器发出的字符消息
	enClientJoinSceneOK,					//客户端转场景成功了

	enCheckRoleAppStatus,					//请求一个角色的外观状态
	enSyncRoleAppStatus,					//同步一个角色的外观状态和相应的版本号

	enSyncTime,								//同步客户端当前时间

	enProcessMsg_AutoEnd,					//最后一个进程间消息
	enProcessMsg_End = 511					//最后一个进程间消息
};

//////////////////////////////////////////////////////////////////////////
// 注意：定义结构体内字节应该从大到小
//GE::Uint64 uA;
//GE::Uint32 uB;
//GE::Uint16 uC;
//GE::Uint8  uD
//
//定义完毕应该加上长度断言
//GE_STATIC_ASSERT(sizeof(Msg) == size);
//并且结构体的大小一定要是4的倍数
//////////////////////////////////////////////////////////////////////////

MSG_BEGIN(MsgWho, enProcessMsg_Who)
	GE::Uint32			uWho;
};

MSG_BEGIN(MsgNewClient, enProcessMsg_NewClient)
	GE::Uint32			uClientSessionID;
};

MSG_BEGIN(MsgLostClient, enProcessMsg_LostClient)
	GE::Uint32			uClientSessionID;
};

MSG_BEGIN(MsgKickClient, enProcessMsg_KickClient)
	GE::Uint32			uClientSesionID;
};

MSG_BEGIN(MsgStartTransaction, enProcessMsg_RoleStartTransaction)
	GE::Uint16			uTransaction;
};

MSG_BEGIN(MsgRoleToTargetPos, enRoleToTargetPos)
	GE::Uint16			uX;
	GE::Uint16			uY;
};

MSG_BEGIN(MsgRoleMovePos, enRoleMovePos)
	GE::Uint16			uX;
	GE::Uint16			uY;
};

MSG_BEGIN(MsgSyncRoleTargerPos, enSyncRoleTargerPos)
	GE::Uint64			uRoleID;
	GE::Uint16			uTX;//这个玩家的目的坐标
	GE::Uint16			uTY;
	GE::Uint16			uX;//这个玩家的当前坐标
	GE::Uint16			uY;
	GE::Uint16			uVersion1;//低频版本号
	GE::Uint16			uVersion2;//高频版本号
};

MSG_BEGIN(MsgSyncRoleNowPos, enSyncRoleNowPos)
	GE::Uint64			uRoleID;
	GE::Uint16			uX;//这个玩家的当前坐标
	GE::Uint16			uY;
	GE::Uint16			uVersion1;//低频版本号
	GE::Uint16			uVersion2;//高频版本号
};


MSG_BEGIN(MsgSyncRoleScenePos, enSyncRoleScenePos)
	GE::Uint32			uSceneID;
	GE::Uint16			uMapID;
	GE::Uint16			uSceneType;
	GE::Uint16			uTotalRole;
	GE::Uint16			uX;
	GE::Uint16			uY;
};

MSG_BEGIN(MsgSyncRoleVersion, enSyncRoleVersion)
	GE::Uint64			uRoleID;
	GE::Uint16			uVersion;//版本号
};

MSG_BEGIN(MsgSyncRoleDisappear, enSyncRoleDisappear)
	GE::Uint64			uRoleID;
};

MSG_BEGIN(MsgSyncRoleIdle, enSyncRoleIdle)
	GE::Uint16			uX;
	GE::Uint16			uY;
	GE::Uint32			uCode;//静止类型
};


MSG_BEGIN(MsgCheckRoleAppearanceData, enCheckRoleAppearanceData)
	GE::Uint64			uRoleID;
};

MSG_BEGIN(MsgCheckRoleAppStatus, enCheckRoleAppStatus)
	GE::Uint64			uRoleID;
};

MSG_BEGIN(MsgSyncRoleAppStatus, enSyncRoleAppStatus)
	GE::Uint64			uRoleID;
	GE::Uint16			uAppStatus;
	GE::Uint16			uAppStatusVersion;
};


MSG_BEGIN(MsgNPCPos, enNPCPos)
	GE::Uint32			uID;
	GE::Uint16			uType;
	GE::Uint16			uX;
	GE::Uint16			uY;
	GE::Uint8			uDirection;
};

MSG_BEGIN(MsgNPCMovingPos, enNPCMovingPos)
	GE::Uint32			uID;
	GE::Uint16			uType;
	GE::Uint16			uX;
	GE::Uint16			uY;
	GE::Uint16			uTX;
	GE::Uint16			uTY;
};

MSG_BEGIN(MsgNPCDisappear, enNPCDisappear)
	GE::Uint32			uID;
};
MSG_BEGIN(MsgNPCClick, enNPCClick)
	GE::Uint32			uID;
};

MSG_BEGIN(MsgSyncI32, 0)
	GE::Int32			i32;
};

MSG_BEGIN(MsgRoleFlyState, enRoleFlyState)
	GE::Uint32			uFlyState;
};

MSG_BEGIN(MsgCharMsg, enClientCharMsg)
	GE::B8				b8;
};

MSG_BEGIN(MsgClientJoinSceneOK, enClientJoinSceneOK)
};

MSG_BEGIN(MsgSyncTime, enSyncTime)
	GE::Uint32			uTime;
};

GE_STATIC_ASSERT(sizeof(MsgNPCMovingPos) == 20);
GE_STATIC_ASSERT(sizeof(MsgNPCPos) == 16);
GE_STATIC_ASSERT(sizeof(MsgCheckRoleAppearanceData) == 12);
GE_STATIC_ASSERT(sizeof(MsgSyncRoleIdle) == 12);
GE_STATIC_ASSERT(sizeof(MsgRoleMovePos) == 8);
GE_STATIC_ASSERT(sizeof(MsgRoleToTargetPos) == 8);
GE_STATIC_ASSERT(sizeof(MsgSyncRoleDisappear) == 12);
GE_STATIC_ASSERT(sizeof(MsgSyncRoleTargerPos) == 24);
GE_STATIC_ASSERT(sizeof(MsgSyncRoleNowPos) == 20);
GE_STATIC_ASSERT(sizeof(MsgSyncRoleScenePos) == 20);
GE_STATIC_ASSERT(sizeof(MsgSyncRoleVersion) == 16);
GE_STATIC_ASSERT(sizeof(MsgClientJoinSceneOK) == 4);
GE_STATIC_ASSERT(sizeof(MsgRoleFlyState) == 8);
GE_STATIC_ASSERT(sizeof(MsgCharMsg) == 12);
GE_STATIC_ASSERT(sizeof(MsgNPCClick) == 8);
GE_STATIC_ASSERT(sizeof(MsgNPCDisappear) == 8);
GE_STATIC_ASSERT(enProcessMsg_AutoEnd < enProcessMsg_End);

#pragma pack(pop)

