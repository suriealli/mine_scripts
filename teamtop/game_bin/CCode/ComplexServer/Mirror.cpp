/*我是UTF8无签名编码 */
#include "Mirror.h"
#include "NPCMgr.h"
#include "SceneMgr.h"
#include "RoleMgr.h"
#include "Role.h"
#include "PublicScene.h"
#include "PySingleMirrorScene.h"
#include "PyMultiMirrorScene.h"



MirrorBase::MirrorBase(GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName)
	: SceneBase(uSceneID, pSceneName)
	, m_uGlobalID(uGlobalID)
	, m_uMapID(uMapID)
{

}

MirrorBase::~MirrorBase()
{

}

void MirrorBase::OnClickNPC(Role* pRole, GE::Uint32 uNPCID)
{
	NPCMgr::Instance()->ClickPrivateNPC(pRole, uNPCID);
}


//////////////////////////////////////////////////////////////////////////////////////////////////
//单人FB
//////////////////////////////////////////////////////////////////////////////////////////////////
SingleMirrorScene::SingleMirrorScene(GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName)
	: MirrorBase(uGlobalID, uMapID, uSceneID, pSceneName)
	, m_pRole(NULL)
{
	this->m_pySelf.SetObj_NewRef((PyObject*)ServerPython::PySingleMirrorScene_New(this));
}

SingleMirrorScene::~SingleMirrorScene()
{
	ServerPython::PySingleMirrorScene_Del(this->m_pySelf.GetObj_BorrowRef());
}

bool SingleMirrorScene::IsEmpty()
{
	return NULL == this->m_pRole;
}

void SingleMirrorScene::Destroy()
{
	if (NULL == this->m_pRole)
	{
		return;
	}
	GE::Uint32 publicSenceID = this->m_pRole->GetLastSceneID();
	PublicScene* pPublicScene = SceneMgr::Instance()->SearchPublicScene(publicSenceID);
	if (pPublicScene == NULL)
	{
		// 这份角色的数据很可能有问题，果断T之
		this->m_pRole->Kick();
	}
	else
	{
		pPublicScene->JoinRole(this->m_pRole, this->m_pRole->GetLastPosX(), this->m_pRole->GetLastPosY());
	}
}

void SingleMirrorScene::RestoreRole(Role* pRole)
{
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = 0;
	rspMsg.uX = pRole->GetPosX();
	rspMsg.uY = pRole->GetPosY();
	pRole->SendMsg(&rspMsg);
}


bool SingleMirrorScene::JoinRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	if (this->m_pRole)
	{
		GE_EXC<<"SingleMirrorScene has more than 1 role."<<GE_END;
		return false;
	}
	SceneBase::JoinRole(pRole, uX, uY);
	// 绑定之
	this->m_pRole = pRole;
	pRole->SetScene(this);
	pRole->SetSceneID(this->m_uSceneID);
	pRole->SetPos(uX, uY);
	pRole->ClearTargerPos();
	// 这里要清空角色的场景字典
	//pRole->OnNewScene();

	//同步场景坐标信息
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = 0;
	rspMsg.uX = uX;
	rspMsg.uY = uY;
	pRole->SendMsg(&rspMsg);
	return true;
}

bool SingleMirrorScene::JumpRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	pRole->SetPosEx(uX, uY);
	//同步场景坐标信息
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = 0;
	rspMsg.uX = uX;
	rspMsg.uY = uY;
	pRole->SendMsg(&rspMsg);
	return true;
}

void SingleMirrorScene::LeaveRole( Role* pRole )
{
	SceneBase::LeaveRole(pRole);
	if (pRole != this->m_pRole)
	{
		GE_EXC<<"SingleMirrorScene has a error role on LeavePlayer."<<GE_END;
		return;
	}
	this->BeforeLeaveRole(pRole);
	this->m_pRole = NULL;
	pRole->SetScene(NULL);
}

void SingleMirrorScene::BeforeLeaveRole( Role* pRole )
{
	if (this->m_pyBeforeLevelRole.IsNone())
	{
		return;
	}
	this->m_pyBeforeLevelRole.Call("OO", this->PySelf().GetObj_BorrowRef(), pRole->GetPySelf().GetObj_BorrowRef());
}

void SingleMirrorScene::LoadBeforeLeaveRole( PyObject* pyFun_BorrowRef )
{
	this->m_pyBeforeLevelRole.Load(pyFun_BorrowRef);
}

bool SingleMirrorScene::CanDestory()
{
	return this->IsEmpty();
}

bool SingleMirrorScene::MoveRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	// 设置位置
	pRole->SetPosEx(uX, uY);
	return true;
}





//////////////////////////////////////////////////////////////////////////////////////////////////
//多人FB
//////////////////////////////////////////////////////////////////////////////////////////////////
MultiMirrorScene::MultiMirrorScene(GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName, bool bAliveTimeFlag)
	: MirrorBase(uGlobalID, uMapID, uSceneID, pSceneName)
	, m_bAliveTimeFlag(bAliveTimeFlag)
{
	this->m_pySelf.SetObj_NewRef((PyObject*)ServerPython::PyMultiMirrorScene_New(this));
}

MultiMirrorScene::~MultiMirrorScene()
{
	ServerPython::PyMultiMirrorScene_Del(this->m_pySelf.GetObj_BorrowRef());
}

bool MultiMirrorScene::IsEmpty()
{
	return this->m_RoleMap.empty();
}

void MultiMirrorScene::Destroy()
{
	if (this->IsEmpty())
	{
		return;
	}
	//标记没有生存时间了
	this->m_bAliveTimeFlag = false;

	tyRoleMap::iterator iter = this->m_RoleMap.begin();
	while(iter != this->m_RoleMap.end())
	{
		Role* pRole = iter->second;
		// 这里注意要先保存新的迭代器
		++iter;
		// 返回公共场景
		GE::Uint32 publicSenceID = pRole->GetLastSceneID();
		PublicScene* pPublicScene = SceneMgr::Instance()->SearchPublicScene(publicSenceID);
		if (pPublicScene == NULL)
		{
			pRole->Kick();
		}
		else
		{
			pPublicScene->JoinRole(pRole, pRole->GetLastPosX(), pRole->GetLastPosY());
		}
	}
}

bool MultiMirrorScene::JoinRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	tyRoleMap::iterator iter = this->m_RoleMap.find(pRole->GetRoleID());
	if (iter != this->m_RoleMap.end())
	{
		GE_EXC<<"MultiMirrorScene repeat join role("<<pRole->GetRoleID()<<")."<<GE_END;
		return false;
	}
	SceneBase::JoinRole(pRole, uX, uY);

	pRole->SetScene(this);
	pRole->SetSceneID(this->m_uSceneID);
	pRole->SetPos(uX, uY);
	pRole->ClearTargerPos();

	//同步场景坐标信息
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = 0;
	rspMsg.uX = uX;
	rspMsg.uY = uY;
	pRole->SendMsg(&rspMsg);

	// 开始迭代玩家，并且告诉客户端
	for(iter = this->m_RoleMap.begin(); iter != this->m_RoleMap.end(); ++iter)
	{
		Role* pIterRole = iter->second;
		pRole->SendMsg(pIterRole->GetPosMsg());		//(pRole)这个玩家看到了其他的玩家
		pIterRole->SendMsg(pRole->GetPosMsg());	// 其他人(pIterRole)看到了这个新的玩家
	}

	this->m_RoleMap.insert(std::make_pair(pRole->GetRoleID(), pRole));

	return true;
}

void MultiMirrorScene::LeaveRole( Role* pRole )
{
	tyRoleMap::iterator iter = this->m_RoleMap.find(pRole->GetRoleID());
	if (iter == this->m_RoleMap.end())
	{
		GE_EXC<<"role have not scene but MultiMirrorScene::LeaveRole"<<GE_END;
		return;
	}
	SceneBase::LeaveRole(pRole);

	// 触发脚本
	this->BeforeLeaveRole(pRole);

	// 删除之
	this->m_RoleMap.erase(iter);
	// 告诉之
	MsgSyncRoleDisappear rdMsg;
	rdMsg.uRoleID = pRole->GetRoleID();

	for(iter = this->m_RoleMap.begin(); iter != this->m_RoleMap.end(); ++iter)
	{
		iter->second->SendMsg(&rdMsg);
	}

	pRole->DoIdle(1);
	pRole->SetScene(NULL);
}

bool MultiMirrorScene::MoveRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY)
{
	if(pRole->GetPosX() == uX && pRole->GetPosY() == uY)
	{
		return false;
	}

	// 设置位置
	pRole->SetPos(uX, uY);

	tyRoleMap::iterator iter = this->m_RoleMap.begin();
	// 告诉客户端
	for (; iter != this->m_RoleMap.end(); ++iter)
	{
		if (iter->first == pRole->GetRoleID())
		{
			continue;
		}
		iter->second->SendMsg(pRole->GetPosMsg());
	}
	return true;
}

bool MultiMirrorScene::JumpRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY)
{

	if(pRole->GetPosX() == uX && pRole->GetPosY() == uY)
	{
		return false;
	}
	pRole->SetPos(uX, uY);
	pRole->ClearTargerPos();

	//同步场景坐标信息
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = 0;
	rspMsg.uX = uX;
	rspMsg.uY = uY;
	pRole->SendMsg(&rspMsg);

	// 告诉客户端
	tyRoleMap::iterator iter = this->m_RoleMap.begin();
	for (; iter != this->m_RoleMap.end(); ++iter)
	{
		if (iter->first == pRole->GetRoleID())
		{
			continue;
		}
		iter->second->SendMsg(pRole->GetPosMsg());
	}
	return true;
}

// 查找角色
Role* MultiMirrorScene::SearchRole( GE::Uint64 uRoleID )
{
	tyRoleMap::iterator iter = this->m_RoleMap.find(uRoleID);
	if(iter == this->m_RoleMap.end())
	{
		return NULL;
	}
	return iter->second;
}

void MultiMirrorScene::SendToAllRole(MsgBase* pMsg)
{
	tyRoleMap::iterator iter = this ->m_RoleMap.begin();
	while (iter != this ->m_RoleMap.end())
	{
		iter->second->SendMsg(pMsg);
		++iter;
	}
}

void MultiMirrorScene::SendToRect( GE::Uint16 uX, GE::Uint16 uY, MsgBase* pMsg)
{
	//直接发给全场景的玩家
	SendToAllRole(pMsg);
}

void MultiMirrorScene::BeforeLeaveRole( Role* pRole )
{
	if (this->m_pyBeforeLevelRole.IsNone())
	{
		return;
	}
	this->m_pyBeforeLevelRole.Call("OO", this->PySelf().GetObj_BorrowRef(), pRole->GetPySelf().GetObj_BorrowRef());
}

void MultiMirrorScene::LoadBeforeLeaveRole( PyObject* pyFun_BorrowRef )
{
	this->m_pyBeforeLevelRole.Load(pyFun_BorrowRef);
}

bool MultiMirrorScene::CanDestory()
{
	if (this->m_bAliveTimeFlag)
	{
		//先判断这个副本的生存标识
		return false;
	}
	return this->IsEmpty();
}

void MultiMirrorScene::OnClickNPC( Role* pRole, GE::Uint32 uNPCID )
{
	NPCMgr::Instance()->ClickMirrorNPC(pRole, uNPCID);
}

void MultiMirrorScene::RestoreRole(Role* pRole)
{
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = 0;
	rspMsg.uX = pRole->GetPosX();
	rspMsg.uY = pRole->GetPosY();
	pRole->SendMsg(&rspMsg);

	// 告诉客户端
	tyRoleMap::iterator iter = this->m_RoleMap.begin();
	for (; iter != this->m_RoleMap.end(); ++iter)
	{
		if (iter->first == pRole->GetRoleID())
		{
			continue;
		}
		iter->second->SendMsg(pRole->GetPosMsg());
	}
}

