/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include <boost/unordered_set.hpp>
#include <boost/unordered_map.hpp>
#include "../GameEngine/GameEngine.h"
#include "MessageDefine.h"

class Role;

class RoleMgr
	: public GEControlSingleton<RoleMgr>
{
	typedef boost::unordered_map<GE::Uint16, PyObject*>				PyMsgDistribute;

public:
	typedef boost::unordered_map<GE::Uint64, Role*>					RoleMap;
	typedef boost::unordered_set<GE::Uint64>						RoleIDSet;

public:
	RoleMgr();
	~RoleMgr();
	void						LoadPyData();

/************************************************************************
角色创、查找、保存、踢除等管理
************************************************************************/
public:
	Role*						CreateRole(GE::Uint64 uRoleID, const std::string& sRoleName, 
		const std::string& sOpenID, GE::Uint64 uClientKey, GE::Uint32 uCommandSize, GE::Uint32 uCommandIndex);	//创建角色
	Role*						FindRoleByRoleID(GE::Uint64 uRoleID);											//根据角色ID查找角色
	Role*						FindRoleByClientKey(GE::Uint64 uClientKey);										//根据ClientKey查找角色
	RoleMap&					GetRoleMap() {return m_RoleIDMap;}												//获取所有在线角色
	void						KickClient(PyObject* clientKey_BorrowRef, PyObject* res_BorrowRef);				//踢掉客户端
	void						SaveRole(PyObject* role_BorrowRef);												//保存角色
	void						ExitRole(PyObject* roleid_BorrowRef);											//踢掉角色
	void						BeforeKickRole(PyObject* role_BorrowRef);										//触发提掉角色之前的处理

	void						LostClient(GE::Uint64 uClientKey, PyObject* clientKey_BorrowRef);
	void						ReLogin(GE::Uint64 uClientKey, Role* pRole);
private:
	RoleMap						m_RoleIDMap;																	//角色ID --> 角色
	RoleMap						m_ClientKeyMap;																	//ClientKey --> 角色
	GEPython::Function			m_pyKickClient;
	GEPython::Function			m_pySaveRole;
	GEPython::Function			m_pyExitRole;
	GEPython::Function			m_pyBeforeKickRole;
	GEPython::Function			m_pyLostClient;
/************************************************************************
角色消息处理（包括角色消息统计）
************************************************************************/
public:
	void						RegDistribute(GE::Uint16 uMsgType, PyObject* fun_borrorRef);					//注册Python消息处理函数
	void						UnregDistribute(GE::Uint16 uMsgType);											//取消Python消息处理函数
	bool						OnClientMsg(GE::Uint64 uClientKey, MsgBase* pMsg);								//当客户端消息过来后的处理
	void						OnDistribute(Role* pRole, MsgBase* pMsg);										//调用当前消息的处理Python函数
	void						BroadMsg();																		//广播消息
	RoleIDSet&					GetWatchRole() {return m_WatchRole;}											//获取观察角色消息的ID集合
	void						SetStatistics(bool b);															//设置统计角色消息
	bool						IsStatistics() {return this->m_bStatistics;}									//是否统计角色消息
	void						SetEchoLevel(GE::Int32 nLeval);													//设置回显等级

private:
	void						OnEcho(Role* pRole, MsgBase* pMsg);												//回显消息
	void						OnRoleCallBack(Role* pRole, MsgBase* pMsg);										//客户端回调服务端函数
	void						OnRoleToTargerPos(Role* pRole, MsgRoleToTargetPos* pMsg);						//角色改变移动目标
	void						OnRoleMovePos(Role* pRole, MsgRoleMovePos* pMsg);								//角色移动
	void						OnCheckRoleAppreance(Role* pRole, MsgCheckRoleAppearanceData* pMsg);			//客户端请求角色外观
	void						OnCheckRoleAppStatus(Role* pRole, MsgCheckRoleAppStatus* pMsg);			//客户端请求角色外观

	void						OnClientChat(Role* pRole, MsgCharMsg* pMsg);									//客户端聊天
	void						OnClickNPC(Role* pRole, MsgNPCClick* pMsg);										//客户端点击NPC
	void						OnJoinSceneOK(Role* pRole, MsgClientJoinSceneOK* pMsg);							//客户端进入场景成功

private:
	PyMsgDistribute				m_PyMsgDistribute;																//MsgType --> 处理函数
	RoleIDSet					m_WatchRole;																	//观察角色消息ID集合
	bool						m_bStatistics;																	//是否统计角色消息
	GE::Int32					m_nEchoLevel;																	//回显等级
	

/************************************************************************
时间触发（包括特殊的角色聊天统计结算）
************************************************************************/
public:
	void						CallPerSecond();																//每秒调用
	void						CallAfterNewMinute();															//新的分钟调用
	void						CallAfterNewDay();																//新的天调用
	void						RoleDayClear(Role* pRole);														//角色数据每日清理调用
	
	void						RecountProperty(Role* pRole);
	void						TiLiJap(Role* pRole, GE::Uint32 uTilejap);

	
private:
	GEPython::Function			m_pyRoleDayClear;																//角色数据每日清理脚本触发
	GE::Int16					m_nMinCnt;																		//角色分钟计数
	GEPython::Function			m_pyClientChat;																	//角色聊天脚本触发
	
	GEPython::Function			m_pyRecountProperty;															//重算属性
	GEPython::Function			m_pyTiLiJap;
};

