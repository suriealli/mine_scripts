/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include <string.h>
#include "../GameEngine/GameEngine.h"
#include "NPCTemplate.h"
#include "AreaDefine.h"

class Role;
class SceneBase;
class MsgNPCPos;
class MsgNPCMovingPos;

class NPC
{
	GE_DISABLE_BOJ_CPY(NPC);
public:
	NPC(GE::Uint32 uNPCID, NPCTemplate* pNPCTemp, GE::Uint8 uDirection, bool bIsBroadcast, PyObject* py_BorrowRef);
	~NPC();

public:
	GE::Uint32						GetNPCID(){return m_uNPCID;}								//获取NPC对象ID
	GE::Uint16						GetNPCType() {return m_pNPCTemplate->GetNPCType();}			//获取NPC类型
	GE::Uint16						GetClickLen() {return m_pNPCTemplate->GetClickLen();}		//获取点击距离
	GE::Uint8						GetClickType() {return m_pNPCTemplate->GetClickType();}		//获取点击类型
	std::string&					GetNPCName() {return m_pNPCTemplate->GetNPCName();}			//获取NPC名字
	GEPython::Object&				GetPySelf(){return m_pySelf;}								//获取NPC的Python对象
	GE::Uint8						GetDirection() {return m_uDirection;}						//获取NPC方向
	bool							IsDestroy() {return m_pySelf.IsNone();}						//NPC是否销毁
	void							Destroy();													//销毁NPC
	bool							IsBroadcast() {return m_bIsBroadcast;}						//NPC是否广播
	bool							CanClick(Role* pRole);										//角色能否点击NPC
	void							OnClick(Role* pRole);										//角色点击NPC
	GE::Uint16						GetPosX() { return m_uX;}									//获取NPC的当前X坐标
	GE::Uint16						GetPosY() { return m_uY;}									//获取NPC的当前Y坐标
	void							SetPos(GE::Uint16 uX, GE::Uint16 uY);						//设置NPC的当前坐标
	SceneBase*						GetScene(){return m_pScene;}								//获取NPC所在场景
	void							SetScene(SceneBase* pScene){m_pScene = pScene;}				//设置NPC所在场景
	GE::Uint32						GetSceneID();												//获取NPC所在场景ID
	
public:
	void							SetPyDict( PyObject* key_BorrowRef, PyObject* value_BorrowRef );
	PyObject*						GetPyDict();

	void							SetPySyncDict( PyObject* key_BorrowRef, PyObject* value_BorrowRef );
	PyObject*						GetPySyncDict();
	void							AfterChange();

public:
	// 获取缓存消息
	MsgBase*						GetPosMsg();
	void							SyncDataToRole(Role* pRole);

public:
	bool							IsLink(){return m_member_hook.is_linked();}					//是否在链表中
	void							UnLink(){m_member_hook.unlink();}							//自动脱离链表
	ListMemberHook					m_member_hook;												//链表钩子

private:
	GE::Uint32						m_uNPCID;													//全局ID
	GE::Uint16						m_uX;														//当前X坐标
	GE::Uint16						m_uY;														//当前Y坐标
	GE::Uint8						m_uDirection;												//方向
	bool							m_bIsBroadcast;												//是否需要广播
	bool							m_uIsMoving;												//是否移动中

	bool							m_bIsVaild;

	SceneBase*						m_pScene;													//所在场景对象
	NPCTemplate*					m_pNPCTemplate;												//配置模板
	MsgNPCPos*						m_pPosMsg;													//缓存消息
	
	std::string						m_SyncDataMsg;												//同步给客户端的数据

	GEPython::Object				m_pySelf;													//python对象
	GEPython::Dict					m_pySyncDict;													//python其他数据
	GEPython::Dict					m_pyDict;													//python字典
};

