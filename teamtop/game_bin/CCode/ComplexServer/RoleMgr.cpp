/*我是UTF8无签名编码 */
#include "RoleMgr.h"
#include "Role.h"
#include "SceneMgr.h"
#include "MessageDefine.h"
#include "NPCMgr.h"
#include "SceneBase.h"
#include "ScriptMgr.h"

// 角色消息分发
#define ROLE_MSG_CASE(msgType, msgStruct, msgFun)	\
	case msgType:{	\
		if (pMsg->Size() < sizeof(msgStruct))	\
			{GE_EXC<<"role("<<pRole->GetRoleID()<<") recv msg("<<pMsg->Type()<<") less length("<<pMsg->Size()<<")."<<GE_END;}	\
		else {this->msgFun(pRole, static_cast<msgStruct*>(pMsg));}	\
		break;}

RoleMgr::RoleMgr()
	: m_nMinCnt(0)
	, m_bStatistics(false)
	, m_nEchoLevel(0)
{

}

RoleMgr::~RoleMgr()
{
	// 销毁所有的角色
	RoleMap::iterator role_iter = this->m_RoleIDMap.begin();
	while(role_iter != this->m_RoleIDMap.end())
	{
		role_iter->second->Kick();
		++role_iter;
	}
	this->CallPerSecond();
#if WIN
	GE_ERROR(this->m_RoleIDMap.empty());
	GE_ERROR(this->m_ClientKeyMap.empty());
#endif
	// 销毁所有的角色消息处理
	PyMsgDistribute::iterator iter = this->m_PyMsgDistribute.begin();
	while(iter != this->m_PyMsgDistribute.end())
	{
		this->m_PyMsgDistribute.erase(iter++);
	}
}

void RoleMgr::LoadPyData()
{
	this->m_pyKickClient.Load("Game.Login", "KickClient");
	this->m_pySaveRole.Load("Game.Login", "SaveRole");
	this->m_pyBeforeKickRole.Load("Game.Login", "BeforeExitByKickRole");
	this->m_pyExitRole.Load("Game.Login", "ExitRole");
	this->m_pyClientChat.Load("Game.Role.Chat", "OnRoleChat");
	this->m_pyRoleDayClear.Load("Game.Role.RoleMgr", "OnRoleDayClear");

	this->m_pyLostClient.Load("Game.Login", "LostClient");

	this->m_pyRecountProperty.Load("Game.Property.PropertyMgr", "RecountPorperty");
	this->m_pyTiLiJap.Load("Game.FindBack.FindBack", "AfterTiLiJap");
	
}
//////////////////////////////////////////////////////////////////////////

Role* RoleMgr::CreateRole( GE::Uint64 uRoleID, const std::string& sRoleName, const std::string& sOpenID, GE::Uint64 uClientKey, GE::Uint32 uCommandSize, GE::Uint32 uCommandIndex )
{
	RoleMap::const_iterator riditer = this->m_RoleIDMap.find(uRoleID);
	if (riditer != this->m_RoleIDMap.end())
	{
		GE_EXC<<"repeat role id("<<uRoleID<<") on add role."<<GE_END;
		return NULL;
	}
	RoleMap::const_iterator ckeyiter = this->m_ClientKeyMap.find(uClientKey);
	if (ckeyiter != this->m_ClientKeyMap.end())
	{
		GE_EXC<<"repeat role("<<uRoleID<<") client key("<<uClientKey<<") on add role."<<GE_END;
		return NULL;
	}
	GE::Uint32 uObjID = GlobalObj::Instance()->CreateSceneObj();
	if (0 == uObjID)
	{
		GE_EXC<<"role("<<uRoleID<<") global obj fail."<<GE_END;
		return NULL;
	}
	Role* pRole = new Role(uRoleID, sRoleName, sOpenID, uClientKey, uObjID, uCommandSize, uCommandIndex);
	this->m_RoleIDMap.insert(std::make_pair(uRoleID, pRole));
	this->m_ClientKeyMap.insert(std::make_pair(uClientKey, pRole));
	GlobalObj::Instance()->SetSceneObjInfo(uObjID, enSceneObj_Role, enSceneObj_Observer | enSceneObj_Observable, pRole);
	return pRole;
}

Role* RoleMgr::FindRoleByRoleID( GE::Uint64 uRoleID )
{
	RoleMap::const_iterator riditer = this->m_RoleIDMap.find(uRoleID);
	if (riditer != this->m_RoleIDMap.end())
	{
		return riditer->second;
	}
	else
	{
		return NULL;
	}
}

Role* RoleMgr::FindRoleByClientKey( GE::Uint64 uClientKey )
{
	RoleMap::const_iterator ckeyiter = this->m_ClientKeyMap.find(uClientKey);
	if (ckeyiter != this->m_ClientKeyMap.end())
	{
		return ckeyiter->second;
	}
	else
	{
		return NULL;
	}
}

void RoleMgr::KickClient( PyObject* clientKey_BorrowRef, PyObject* res_BorrowRef )
{
	this->m_pyKickClient.CallObjArgs(2, clientKey_BorrowRef, res_BorrowRef, NULL);
}

void RoleMgr::LostClient(GE::Uint64 uClientKey, PyObject* clientKey_BorrowRef)
{
	RoleMap::const_iterator ckeyiter = this->m_ClientKeyMap.find(uClientKey);
	if (ckeyiter != this->m_ClientKeyMap.end())
	{
		this->m_ClientKeyMap.erase(ckeyiter);
	}
	this->m_pyLostClient.CallObjArgs(1, clientKey_BorrowRef, NULL);
}

void RoleMgr::ReLogin(GE::Uint64 uClientKey, Role* pRole)
{
	RoleMap::const_iterator ckeyiter = this->m_ClientKeyMap.find(uClientKey);
	if (ckeyiter != this->m_ClientKeyMap.end())
	{
		GE_EXC<<"repeat role("<<pRole->GetRoleID()<<") client key("<<uClientKey<<") on ReLogin."<<GE_END;
		return ;
	}
	this->m_ClientKeyMap.insert(std::make_pair(uClientKey, pRole));
}

void RoleMgr::SaveRole( PyObject* role_BorrowRef )
{
	this->m_pySaveRole.CallObjArgs(1, role_BorrowRef, NULL);
}

void RoleMgr::ExitRole( PyObject* roleid_BorrowRef )
{
	this->m_pyExitRole.CallObjArgs(1, roleid_BorrowRef, NULL);
}

void RoleMgr::BeforeKickRole( PyObject* role_BorrowRef )
{
	this->m_pyBeforeKickRole.CallObjArgs(1, role_BorrowRef, NULL);
}

void RoleMgr::RegDistribute( GE::Uint16 uMsgType, PyObject* fun_borrorRef )
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

void RoleMgr::UnregDistribute( GE::Uint16 uMsgType )
{
	PyMsgDistribute::iterator iter = this->m_PyMsgDistribute.find(uMsgType);
	if (iter != this->m_PyMsgDistribute.end())
	{
		Py_DECREF(iter->second);
		this->m_PyMsgDistribute.erase(iter);
	}
}

bool RoleMgr::OnClientMsg( GE::Uint64 uClientKey, MsgBase* pMsg )
{
	RoleMap::const_iterator ckeyiter = this->m_ClientKeyMap.find(uClientKey);
	if (ckeyiter != this->m_ClientKeyMap.end())
	{
		Role* pRole = ckeyiter->second;
		if (!pRole->IsKick())
		{
			switch(pMsg->Type())
			{
			case enGEMsg_Ping:
				{
					break;
				}
				ROLE_MSG_CASE(enProcessMsg_Echo, MsgBase, OnEcho);
				ROLE_MSG_CASE(enProcessMsg_RoleCallBack, MsgBase, OnRoleCallBack);
				ROLE_MSG_CASE(enRoleToTargetPos, MsgRoleToTargetPos, OnRoleToTargerPos);
				ROLE_MSG_CASE(enRoleMovePos, MsgRoleMovePos, OnRoleMovePos);
				ROLE_MSG_CASE(enCheckRoleAppearanceData, MsgCheckRoleAppearanceData, OnCheckRoleAppreance);
				ROLE_MSG_CASE(enCheckRoleAppStatus, MsgCheckRoleAppStatus, OnCheckRoleAppStatus);
				ROLE_MSG_CASE(enClientCharMsg, MsgCharMsg, OnClientChat);
				ROLE_MSG_CASE(enNPCClick, MsgNPCClick, OnClickNPC);
				ROLE_MSG_CASE(enClientJoinSceneOK, MsgClientJoinSceneOK, OnJoinSceneOK);

			default:
				{
					this->OnDistribute(pRole, pMsg);
					break;
				}
			}
			pRole->RecvOneMessage(pMsg->Type());
		}
		return true;
	}
	else
	{
		return false;
	}
	return true;
}

void RoleMgr::OnDistribute( Role* pRole, MsgBase* pMsg )
{
	PyMsgDistribute::iterator iter = this->m_PyMsgDistribute.find(pMsg->Type());
	if (iter == this->m_PyMsgDistribute.end())
	{
		GE_EXC<<"LogicServer can't distribute role msg("<<pMsg->Type()<<"). roleId("<<pRole->GetRoleID()<<")"<<GE_END;
		pRole->IncTI64(RoleDataMgr::Instance()->uWPEIndex, 1);
		return;
	}
	GEPython::Object pyobj;
	UnpackMessage UM(pMsg);
	UM.UnpackMsg(sizeof(MsgBase));
	if (!UM.UnpackPyObj(pyobj))
	{
		GE_EXC<<"can't UnpackPyObj role msg("<<pMsg->Type()<<"). roleId("<<pRole->GetRoleID()<<")"<<GE_END;
		pRole->Kick();
		return;
	}

#if WIN
	ScriptMgr::Instance()->m_pyDebugOnDistriubte.CallObjArgs(3, pRole->GetPySelf().GetObj_BorrowRef(), iter->second, pyobj.GetObj_BorrowRef(), NULL);
#endif
	// 如果角色ID被观察，则调用脚本之
	if (0 != this->m_WatchRole.size() && this->m_WatchRole.find(pRole->GetRoleID()) != this->m_WatchRole.end())
	{
		ScriptMgr::Instance()->m_pyWatchRoleDistribute.CallObjArgs(3, pRole->GetPySelf().GetObj_BorrowRef(), iter->second, pyobj.GetObj_BorrowRef(), NULL);
	}

	/*
	Return value: New reference.
	Call a callable Python object callable, with a variable number of PyObject* arguments. The arguments are provided as a variable number of parameters followed by NULL.
	Returns the result of the call on success, or NULL on failure.
	*/
	PyObject* pyResult_NewRef = PyObject_CallFunctionObjArgs(iter->second, pRole->GetPySelf().GetObj_BorrowRef(), pyobj.GetObj_BorrowRef(), NULL);
	if (NULL == pyResult_NewRef)
	{
		PyErr_Print();
	}
	else
	{
		Py_DECREF(pyResult_NewRef);
	}
}

void RoleMgr::BroadMsg()
{
	RoleMap::iterator iter = this->m_RoleIDMap.begin();
	for(; iter != this->m_RoleIDMap.end(); ++iter)
	{
		Role* pRole = iter->second;
		pRole->BroadMsg();
	}
}

void RoleMgr::SetStatistics( bool b )
{
	this->m_bStatistics = b;
	RoleMap::iterator iter = this->m_RoleIDMap.begin();
	for (iter; iter != this->m_RoleIDMap.end(); ++iter)
	{
		iter->second->ClearMessage();
	}
}

void RoleMgr::SetEchoLevel( GE::Int32 nLeval )
{
	this->m_nEchoLevel = nLeval;
}

void RoleMgr::OnEcho( Role* pRole, MsgBase* pMsg )
{
	if (0 == this->m_nEchoLevel)
	{
		GE_EXC<<"role("<<pRole->GetRoleID()<<") echo on level 0."<<GE_END;
		pRole->Kick();
	}
	else if (1 == this->m_nEchoLevel)
	{
		pRole->SendMsg(pMsg);
	}
	else
	{
		GE::Int32 nCnt = 0;
		RoleMap::iterator iter = this->m_RoleIDMap.begin();
		while(iter != this->m_RoleIDMap.end() && nCnt < this->m_nEchoLevel)
		{
			iter->second->SendMsg(pMsg);
			++iter;
			++nCnt;
		}
	}
}

void RoleMgr::OnRoleCallBack( Role* pRole, MsgBase* pMsg )
{
	pRole->OnCallBackFunction(pMsg);
}

void RoleMgr::OnRoleToTargerPos( Role* pRole, MsgRoleToTargetPos* pMsg )
{
	if (pRole->IsLockMove())
	{
		//锁定移动了
		return;
	}
	pRole->ToTargetPos(pMsg->uX, pMsg->uY);
}

void RoleMgr::OnRoleMovePos( Role* pRole, MsgRoleMovePos* pMsg )
{
	pRole->OnMovePos(pMsg->uX, pMsg->uY);
}

void RoleMgr::OnCheckRoleAppreance( Role* pRole, MsgCheckRoleAppearanceData* pMsg )
{
	if(pRole->GetRoleID() == pMsg->uRoleID)
	{
		return;
	}
	Role* srcRole = this->FindRoleByRoleID(pMsg->uRoleID);
	if (NULL == srcRole)
	{
		return;
	}
	//发送玩家外观数据
	MsgBase* pSyncMsg = srcRole->GetRoleSyncAppearanceMsg();
	if (NULL == pSyncMsg)
	{
		return;
	}
	pRole->SendMsg(pSyncMsg);
}

void RoleMgr::OnCheckRoleAppStatus( Role* pRole, MsgCheckRoleAppStatus* pMsg )
{
	if(pRole->GetRoleID() == pMsg->uRoleID)
	{
		return;
	}

	Role* srcRole = this->FindRoleByRoleID(pMsg->uRoleID);
	if (NULL == srcRole)
	{
		return;
	}
	//发送玩家外观数据
	MsgBase* pSyncMsg = srcRole->GetRoleSyncAppStatusMsg();
	if (NULL == pSyncMsg)
	{
		return;
	}
	pRole->SendMsg(pSyncMsg);
}

void RoleMgr::OnClientChat( Role* pRole, MsgCharMsg* pMsg )
{
	// 打包消息
	const std::string& pinfo = pRole->GetRoleChatInfoMsg();
	PackMessage::Instance()->Reset();
	PackMessage::Instance()->PackMsg(pMsg->Type());
	PackMessage::Instance()->PackStream(static_cast<const void*>(pinfo.data()), static_cast<GE::Uint16>(pinfo.size()));
	PackMessage::Instance()->PackStream(pMsg->Body(), pMsg->BodySize());
	// 如果禁言，并且是全服喊话，就只发送给自己
	if (!pRole->CanChat())
	{
		if (pMsg->b8.UI32_1() == 0)
		{
			pRole->BroadMsg();
		}
	}
	else
	{
		this->m_pyClientChat.Call("OLH", pRole->GetPySelf().GetObj_BorrowRef(), pMsg->b8.I64(), pMsg->Size());
	}
}

void RoleMgr::OnClickNPC( Role* pRole, MsgNPCClick* pMsg )
{
	if (pMsg->uID < MAX_CFG_NPC_ID)
	{
		//点击配置的NPC
		NPCMgr::Instance()->ClickCfgNPC(pRole, pMsg->uID);
	}
	else
	{
		//点击动态生成的NPC
		SceneBase* pScene = pRole->GetScene();
		if (pScene)
		{
			pScene->OnClickNPC(pRole, pMsg->uID);
		}
	}
}

void RoleMgr::OnJoinSceneOK( Role* pRole, MsgClientJoinSceneOK* pMsg )
{
	pRole->UnLockMove();
}

void RoleMgr::CallPerSecond( )
{
	RoleMap::iterator iter = this->m_RoleIDMap.begin();
	while(iter != this->m_RoleIDMap.end())
	{
		Role* pRole = iter->second;
		if (pRole->IsKick())
		{
			this->m_RoleIDMap.erase(iter++);
			RoleMap::const_iterator ckeyiter = this->m_ClientKeyMap.find(pRole->GetClientKey());
			if (ckeyiter != this->m_ClientKeyMap.end())
			{
				this->m_ClientKeyMap.erase(ckeyiter);
			}
			delete pRole;
		}
		else
		{
			pRole->CallPerSecond();
			++iter;
		}
	}
}

void RoleMgr::CallAfterNewMinute()
{
	RoleMap::iterator iter = this->m_RoleIDMap.begin();
	while(iter != this->m_RoleIDMap.end())
	{
		iter->second->CallAfterNewMinute();
		++iter;
	}
}

void RoleMgr::CallAfterNewDay()
{
	RoleMap::iterator iter = this->m_RoleIDMap.begin();
	while(iter != this->m_RoleIDMap.end())
	{
		iter->second->CallAfterNewDay();
		++iter;
	}
}

void RoleMgr::RoleDayClear( Role* pRole )
{
	this->m_pyRoleDayClear.CallObjArgs(1, pRole->GetPySelf().GetObj_BorrowRef(), NULL);
}

void RoleMgr::RecountProperty( Role* pRole )
{
	this->m_pyRecountProperty.CallObjArgs(1, pRole->GetPySelf().GetObj_BorrowRef(), NULL);
}

void RoleMgr::TiLiJap(Role* pRole, GE::Uint32 uTilejap)
{
	this->m_pyTiLiJap.Call("OI", pRole->GetPySelf().GetObj_BorrowRef(), uTilejap);
}


