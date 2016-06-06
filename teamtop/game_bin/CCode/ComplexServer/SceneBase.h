/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include <string.h>
#include "../GameEngine/GameEngine.h"

enum SceneType
{
	enSceneNone,
	enSceneBase,
	enScenePublic,
	enMirrorBase,
	enSingleMirror,
	enMultiMirror,
};

class Role;
class NPC;

class SceneBase
{
public:
	SceneBase(GE::Uint32 uSceneID, const std::string& sSceneName);
	virtual ~SceneBase();

public:
	virtual GE::Uint32			GlobalID(){return 0;}
	GE::Uint32					GetSceneID() {return m_uSceneID;}			//获取场景ID
	const std::string&			SceneName() {return m_sSceneName;}			//获取场景名
	GEPython::Object&			PySelf(){return m_pySelf;}					//获取场景Python对象

	virtual bool				IsSave(){return false;}
	virtual bool				IsFlyingPos(Role* pRole){return false;}
public:
	virtual SceneType			GetSceneType() {return enSceneBase;}		//获取场景类型
	virtual void				SaveRoleSceneData(Role* pRole);				//保存角色的场景信息
	virtual void				CallPerSecond();							//每秒调用

public:
	virtual NPC*				CreateNPC(GE::Uint16 uTypeID, GE::Uint16 uX, GE::Uint16 uY,
											GE::Uint8 uDirection, bool bBroadCast, PyObject* py_BorrowRef) = 0;		//创建NPC
	virtual void				DestroyNPC(NPC *pNPC) = 0;									//销毁NPC
	virtual void				DestroyNPC(GE::Uint32 uNPCID) = 0;							//销毁NPC
	virtual void				OnClickNPC(Role* pRole, GE::Uint32 uNPCID) = 0;				//点击NPC
	virtual NPC*				SearchNPC( GE::Uint32 uNPCID ) { return NULL;}				//查找NPC

public:
	virtual bool				JoinRole(Role* pRole, GE::Uint16 uX = 0, GE::Uint16 uY = 0);//角色加入场景
	virtual void				LeaveRole(Role* pRole);										//角色离开场景
	virtual bool				MoveRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY) = 0;	//角色移动
	virtual bool				JumpRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY) = 0;	//角色跳跃
	virtual bool				JoinNPC(NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY) = 0;		//NPC加入场景
	virtual void				LeaveNPC(NPC* pNPC) = 0;									//NPC离开场景
	virtual bool				JumpNPC(NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY) = 0;		//NPC跳跃

public:
	virtual void				SendToRect( GE::Uint16 uX, GE::Uint16 uY, MsgBase* pMsg) = 0;	//发送消息给一个固定中心点的区域，长度为玩家视野(默认，不填充大小)的所有玩家
	virtual void				SendToAllRole(MsgBase* pMsg) {};								//发送给场景内部所有的玩家
	virtual bool				CanSeeOther() {return false;}									//此场景是否可以看到其他单位

protected:
	GE::Uint32					m_uSceneID;
	std::string					m_sSceneName;
	GEPython::Object			m_pySelf;
};

