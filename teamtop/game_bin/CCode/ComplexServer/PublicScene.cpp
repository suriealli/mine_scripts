#include "PublicScene.h"
#include "MessageDefine.h"
#include "AreaMap.h"
#include "Role.h"
#include "PyPublicScene.h"
#include "NPCMgr.h"
#include "RoleMgr.h"

PublicScene::PublicScene(GE::Uint32 uSceneID, const std::string& sSceneName, MapTemplate* pMT, GE::Uint8 uAreaSize, bool bIsSaveData, bool bCanSeeOther)
	: SceneBase(uSceneID, sSceneName)
	, m_bBroadcastNPCChange(true)
	, m_bNeedBroadcast(true)
	, m_uMovingTimeJap(0)
	, m_uMoveDistanceJap(0)
{
	this->m_pAreaMap = new AreaMap(pMT, uAreaSize, bCanSeeOther);
	this->m_bIsSave = bIsSaveData;
	this->m_bCanSeeOther = bCanSeeOther;

	this->m_pySelf.SetObj_NewRef((PyObject*)ServerPython::PyPublicScene_New(this));
}

PublicScene::~PublicScene()
{
	ServerPython::PyPublicScene_Del(this->m_pySelf.GetObj_BorrowRef());
	GE_SAFE_DELETE(m_pAreaMap);
#if WIN
	GE_ERROR(this->m_sceneNPCMap.empty());
	GE_ERROR(this->m_sceneRoleMap.empty());
	GE_ERROR(this->m_sceneBroadcastNPCSet.empty());
#endif
	this->m_sceneBroadcastNPCSet.clear();
}

void PublicScene::SaveRoleSceneData( Role* pRole )
{
	if (!this->IsSave())
	{
		return;
	}
	//保存数据
	pRole->SetLastSceneID(this->GetSceneID());
	pRole->SetLastPosX(pRole->GetPosX());
	pRole->SetLastPosY(pRole->GetPosY());
}

void PublicScene::CallPerSecond()
{
	SceneBase::CallPerSecond();
	this->BroadcastNPC();
}

void PublicScene::AfterCreate()
{
	if (this->m_pyAfterCreate.IsNone())
	{
		return;
	}
	this->m_pyAfterCreate.Call("(O)", this->PySelf().GetObj_BorrowRef());
}

NPC* PublicScene::CreateNPC( GE::Uint16 uTypeID, GE::Uint16 uX, GE::Uint16 uY, GE::Uint8 uDirection, bool bBroadCast, PyObject* py_BorrowRef)
{
	return  NPCMgr::Instance()->CreateNPC(this, uTypeID, uX, uY, uDirection, bBroadCast, py_BorrowRef);
}

void PublicScene::DestroyNPC( NPC *pNPC )
{
	NPCMgr::Instance()->DestroyNPC(pNPC);
}

void PublicScene::DestroyNPC( GE::Uint32 uNPCID )
{
	NPCMgr::Instance()->DestroyNPC(uNPCID);
}

void PublicScene::OnClickNPC( Role* pRole, GE::Uint32 uNPCID )
{
	SceneNPCMap::iterator iter = this->m_sceneNPCMap.find(uNPCID);
	if (iter == this->m_sceneNPCMap.end())
	{
		NPCMgr::Instance()->ClickPrivateNPC(pRole, uNPCID);
	}
	else
	{
		NPCMgr::Instance()->ClickNPC(pRole, iter->second);
	}
}

NPC* PublicScene::SearchNPC( GE::Uint32 uNPCID )
{
	SceneNPCMap::iterator iter = this->m_sceneNPCMap.find(uNPCID);
	if(iter == this->m_sceneNPCMap.end())
	{
		return NULL;
	}
	return iter->second;
}
void PublicScene::RestoreRole(Role* pRole)
{
	//同步场景坐标信息
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->m_pAreaMap->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = this->m_pAreaMap->TotalRole();
	rspMsg.uX = pRole->GetPosX();
	rspMsg.uY = pRole->GetPosY();
	pRole->SendMsg(&rspMsg);

	//发送所有应该广播的NPC
	this->BroadcastNPCToRole(pRole);
	
	this->m_pAreaMap->FindVisibleRect(pRole->GetPosX(), pRole->GetPosY());
	
	if (this->m_bCanSeeOther)
	{
		//迭代新的可见玩家与NPC
		Role* pIterRole = NULL;
		this->m_pAreaMap->BeginIteratorNewVisiblePlayer();
		while(pIterRole = (this->m_pAreaMap->GetNextNewVisiblePlayer()))
		{
			pRole->SendMsg(pIterRole->GetPosMsg());//(pRole)这个玩家看到了其他的玩家
			
		}
	}
	//////////////////////////////////////////////////////////////////////////
	NPC* pNPC = NULL;
	this->m_pAreaMap->BeginIteratorNewVisibleNPC();
	while(pNPC = static_cast<NPC*>(this->m_pAreaMap->GetNextNewVisibleNPC()))
	{
		if(pNPC->IsBroadcast())
		{
			// 广播NPC一直都存在，不用再发送了
			continue;
		}
		pRole->SendMsg(pNPC->GetPosMsg());
	}
	
	this->AfterRestoreRole(pRole);
}


bool PublicScene::JoinRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	
	SceneBase::JoinRole(pRole);
	
	if(!this->m_pAreaMap->JoinRole_S(pRole, uX, uY))
	{
		pRole->Kick();
		GE_EXC<<"Role("<<pRole->GetRoleID()<<") join scene("<<this->GetSceneID()<<") pos ("<< uX<<", "<<uY <<") error."<<GE_END;
		return false;
	}

	pRole->SetScene(this);
	pRole->SetSceneID(this->GetSceneID());
	//pRole->OnNewScene();
	pRole->LockMove();

	this->InsertRole(pRole);

	//同步场景坐标信息
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->m_pAreaMap->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = this->m_pAreaMap->TotalRole();
	rspMsg.uX = uX;
	rspMsg.uY = uY;
	pRole->SendMsg(&rspMsg);

	//发送所有应该广播的NPC
	this->BroadcastNPCToRole(pRole);

	if (this->m_bCanSeeOther)
	{
		//////////////////////////////////////////////////////////////////////////
		//迭代新的可见玩家与NPC
		Role* pIterRole = NULL;

		this->m_pAreaMap->BeginIteratorNewVisiblePlayer();
		while(pIterRole = (this->m_pAreaMap->GetNextNewVisiblePlayer()))
		{
			pRole->SendMsg(pIterRole->GetPosMsg());		//(pRole)这个玩家看到了其他的玩家
			pIterRole->SendMsg(pRole->GetPosMsg());	// 其他人(pIterRole)看到了这个新的玩家
		}
	}
	//////////////////////////////////////////////////////////////////////////
	NPC* pNPC = NULL;
	this->m_pAreaMap->BeginIteratorNewVisibleNPC();
	while(pNPC = static_cast<NPC*>(this->m_pAreaMap->GetNextNewVisibleNPC()))
	{
		if(pNPC->IsBroadcast())
		{
			// 广播NPC一直都存在，不用再发送了
			continue;
		}
		pRole->SendMsg(pNPC->GetPosMsg());
	}
	
	pRole->DoIdle(1);
	//触发进入场景调用python函数
	this->AfterJoinRole(pRole);
	return true;
}

void PublicScene::LeaveRole( Role* pRole )
{
	if (pRole->GetScene() != this)
	{
		return;
	}

	SceneBase::LeaveRole(pRole);

	// 玩家离开场景前，调用脚本,在角色类删除的时候，也会调用这个方法
	this->BeforeLeaveRole(pRole);
	
	this->RemoveRole(pRole);
	this->m_pAreaMap->LeaveRole(pRole);
	
	if (this->m_bCanSeeOther)
	{
		MsgSyncRoleDisappear rdMsg;
		rdMsg.uRoleID = pRole->GetRoleID();

		Role* pIterRole = NULL;
		this->m_pAreaMap->BeginIteratorNewVisiblePlayer();
		while(pIterRole = static_cast<Role*>(this->m_pAreaMap->GetNextNewVisiblePlayer()))
		{
			// 告诉视野范围内的玩家，有一个玩家离开了
			pIterRole->SendMsg(&rdMsg);
		}
	}

	//先让客户端把角色静止，终止某些寻路或者操作
	pRole->DoIdle(1);
	pRole->SetScene(NULL);
}

bool PublicScene::MoveRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	if(pRole->IsLockMove())
	{
		//进入场景时会锁定移动，只有客户端返回传送成功才能解锁
		return false;
	}
	if (pRole->IsIgnoreCheckMovingTime(this->m_uMovingTimeJap))
	{
		//因为有移动时间忽视设定，这次移动被忽视了
		return false;
	}
	if (this->IsIgnoreCheckMoveDistanceJap(pRole, uX, uY))
	{
		return false;
	}
	if(this->m_uMoveDistanceJap == 0 && this->m_uMovingTimeJap == 0)
	{
		// 只有在场景配置移动检测中没都设定任何的忽视时，才检查客户端发送的坐标的正确性，否则直接忽视,默认可以移动很大的距离
		bool checkX = this->CheckPosX(pRole, uX);
		bool checkY = this->CheckPosY(pRole, uY);
		if(!checkX || !checkY)
		{
			//移动出错，不给移动
			pRole->DoIdle();
			return false;
		}
	}
	switch(this->m_pAreaMap->MoveRole(pRole, uX, uY))
	{
	case enCanNotMove:
		{
			pRole->DoIdle();//移动出错，不给移动
			return false;
		}
	case enMoveNotIterOther:
		{
			return true;
		}
	default:
		break;
	}

	if (this->m_bCanSeeOther)
	{
		// 开始迭代玩家，并且告诉客户端
		Role* pIterRole = NULL;
		// 迭代新的可视玩家
		this->m_pAreaMap->BeginIteratorNewVisiblePlayer();
		while(pIterRole = this->m_pAreaMap->GetNextNewVisiblePlayer())
		{
			pRole->SendMsg(pIterRole->GetPosMsg());		//(pRole)这个玩家看到了其他的玩家
			pIterRole->SendMsg(pRole->GetPosMsg());		//其他人(pIterRole)看到了这个新的玩家
		}
	}
	//---------------------------------------------
	// 非玩家 （暂时是NPC）
	NPC* pNPC = NULL;
	this->m_pAreaMap->BeginIteratorNewVisibleNPC();
	while(pNPC = this->m_pAreaMap->GetNextNewVisibleNPC())
	{
		if(pNPC->IsBroadcast())
		{
			// 广播NPC一直都存在，不用再发送了
			continue;
		}
		pRole->SendMsg(pNPC->GetPosMsg());
	}
		
	if (this->m_bCanSeeOther)
	{
		// 不可见------------------------------------------------------------------------------
		MsgSyncRoleDisappear rdMsg;
		MsgSyncRoleDisappear other_rdMsg;
		Role* pIterRole = NULL;
		rdMsg.uRoleID = pRole->GetRoleID();
		this->m_pAreaMap->BeginIteratorNewUnvisiblePlayer();
		while(pIterRole = this->m_pAreaMap->GetNextNewUnvisiblePlayer())
		{
			// 把这个玩家看到不到的角色移除掉
			other_rdMsg.uRoleID = pIterRole->GetRoleID();
			pRole->SendMsg(&other_rdMsg);
			// 告诉周围视野外的玩家，有一个玩家消失了
			pIterRole->SendMsg(&rdMsg);
		}
	}
	pNPC = NULL;
	MsgNPCDisappear ndMsg;
	this->m_pAreaMap->BeginIteratorNewUnvisibleNPC();
	while(pNPC = this->m_pAreaMap->GetNextNewUnvisibleNPC())
	{
		// 告诉玩家，看不到这些NPC了
		ndMsg.uID = pNPC->GetNPCID();
		pRole->SendMsg(&ndMsg);
	}
	
	return true;
}

bool PublicScene::JumpRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{

	switch(this->m_pAreaMap->MoveRole(pRole, uX, uY))
	{
	case enCanNotMove:
		{
			pRole->DoIdle();//移动出错，不给移动
			return false;
		}
	case enMoveNotIterOther:
		{
			//清理目标点
			pRole->ClearTargerPos();

			//同步场景坐标信息
			MsgSyncRoleScenePos rspMsg;
			rspMsg.uSceneID = this->GetSceneID();
			rspMsg.uMapID = this->m_pAreaMap->MapID();
			rspMsg.uSceneType = this->GetSceneType();
			rspMsg.uTotalRole = this->m_pAreaMap->TotalRole();
			rspMsg.uX = uX;
			rspMsg.uY = uY;
			pRole->SendMsg(&rspMsg);
			//向周围的人同步自己的位置
			this->SendToRect(pRole->GetPosX(), pRole->GetPosY(), pRole->GetNPosMsg());
			return true;
		}
	default:
		break;
	}
	//清理目标点
	pRole->ClearTargerPos();
	//同步场景坐标信息
	MsgSyncRoleScenePos rspMsg;
	rspMsg.uSceneID = this->GetSceneID();
	rspMsg.uMapID = this->m_pAreaMap->MapID();
	rspMsg.uSceneType = this->GetSceneType();
	rspMsg.uTotalRole = this->m_pAreaMap->TotalRole();
	rspMsg.uX = uX;
	rspMsg.uY = uY;
	pRole->SendMsg(&rspMsg);

	if (this->m_bCanSeeOther)
	{
		// 开始迭代玩家，并且告诉客户端
		Role* pIterRole = NULL;
		// 迭代新的可视玩家
		this->m_pAreaMap->BeginIteratorNewVisiblePlayer();
		while(pIterRole = this->m_pAreaMap->GetNextNewVisiblePlayer())
		{
			pRole->SendMsg(pIterRole->GetPosMsg());		//(pRole)这个玩家看到了其他新的玩家
		}
	}
	//---------------------------------------------
	// NPC
	NPC* pNPC = NULL;
	this->m_pAreaMap->BeginIteratorNewVisibleNPC();
	while(pNPC = this->m_pAreaMap->GetNextNewVisibleNPC())
	{
		if(pNPC->IsBroadcast())
		{
			// 广播NPC一直都存在，不用再发送了
			continue;
		}
		pNPC->SyncDataToRole(pRole);
	}

	if (this->m_bCanSeeOther)
	{
		// 不可见------------------------------------------------------------------------------
		MsgSyncRoleDisappear rdMsg;
		MsgSyncRoleDisappear other_rdMsg;
		Role* pIterRole = NULL;
		rdMsg.uRoleID = pRole->GetRoleID();
		this->m_pAreaMap->BeginIteratorNewUnvisiblePlayer();
		while(pIterRole = this->m_pAreaMap->GetNextNewUnvisiblePlayer())
		{
			// 把这个玩家看到不到的角色移除掉
			other_rdMsg.uRoleID = pIterRole->GetRoleID();
			pRole->SendMsg(&other_rdMsg);
			// 告诉周围视野外的玩家，有一个玩家消失了
			pIterRole->SendMsg(&rdMsg);
		}
	}
	pNPC = NULL;
	MsgNPCDisappear ndMsg;
	this->m_pAreaMap->BeginIteratorNewUnvisibleNPC();
	while(pNPC = this->m_pAreaMap->GetNextNewUnvisibleNPC())
	{
		// 告诉玩家，看不到这些NPC了
		ndMsg.uID = pNPC->GetNPCID();
		pRole->SendMsg(&ndMsg);
	}

	if (this->m_bCanSeeOther)
	{
		//一定要最后才调用这个，这个会打乱迭代队列
		//向周围的人同步自己的位置
		this->SendToRect(pRole->GetPosX(), pRole->GetPosY(), pRole->GetNPosMsg());
	}
	return true;
}

bool PublicScene::JoinNPC( NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY )
{
	if(NULL == pNPC)
	{
		return false;
	}
	if (pNPC->GetScene())
	{
		return false;
	}

	this->m_pAreaMap->JoinNPC(pNPC, uX, uY);
	pNPC->SetScene(this);
	this->InsertNPC(pNPC);

	if(pNPC->IsBroadcast())
	{
		// 不需要再迭代玩家
		return true;
	}

	//迭代新的可见玩家
	Role* pIterRole = NULL;
	this->m_pAreaMap->BeginIteratorNewVisiblePlayer();
	while(pIterRole = (this->m_pAreaMap->GetNextNewVisiblePlayer()))
	{
		pNPC->SyncDataToRole(pIterRole);// 其他人(pIterRole)看到了这个新的pNPC
	}
	return true;
}

void PublicScene::LeaveNPC( NPC* pNPC )
{
	if(pNPC == NULL)
	{
		GE_EXC<<"LeaveNPC: pNPC == NULL"<<GE_END;
		return;
	}
	// 判断是否在场景内，不在就直接返回
	if(pNPC->GetScene() != this)
	{
		GE_EXC<<"npc have not scene but PublicScene::LeaveNPC."<<GE_END;
		return;
	}
	// 移除Map中的记录
	this->RemoveNPC(pNPC);
	this->m_pAreaMap->LeaveNPC(pNPC);

	if(pNPC->IsBroadcast())
	{
		// 广播的，不需要迭代告诉玩家
		pNPC->SetScene(NULL);
		return;
	}

	Role* pIterRole;
	MsgNPCDisappear ndMsg;
	ndMsg.uID = pNPC->GetNPCID();
	this->m_pAreaMap->BeginIteratorNewVisiblePlayer();
	while(pIterRole = this->m_pAreaMap->GetNextNewVisiblePlayer())
	{
		// 告诉视野范围内的玩家，有一个NPC不见了
		pIterRole->SendMsg(&ndMsg);
	}
	pNPC->SetScene(NULL);
}


bool PublicScene::JumpNPC( NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY )
{
	return true;
}

void PublicScene::SendToRect(GE::Uint16 uX, GE::Uint16 uY, MsgBase* pMsg)
{
	// 开始迭代玩家，并且告诉客户端
	Role *pIterRole = NULL;
	// 必须迭代完才可以做其他类似传送之类的操作
	this->m_pAreaMap->BeginIteratorRectPlayer(uX, uY);
	while(pIterRole = static_cast<Role*>(this->m_pAreaMap->GetNextRectPlayer()))
	{
		pIterRole->SendMsg(pMsg);
	}
}

void PublicScene::SendToAllRole( MsgBase* pMsg )
{
	SceneRoleMap::iterator iter = this->m_sceneRoleMap.begin();
	while(iter != this->m_sceneRoleMap.end())
	{
		iter->second->SendMsg(pMsg);
		++iter;
	}
}

void PublicScene::BroadToRect( Role* pAroundTheRole )
{
	// 开始迭代玩家，并且告诉客户端
	Role *pIterRole = NULL;
	// 必须迭代完才可以做其他类似传送之类的操作
	this->m_pAreaMap->BeginIteratorRectPlayer(pAroundTheRole->GetPosX(), pAroundTheRole->GetPosY());
	while(pIterRole = static_cast<Role*>(this->m_pAreaMap->GetNextRectPlayer()))
	{
		pIterRole->BroadMsg();
	}
}

void PublicScene::BroadMsg()
{
	SceneRoleMap::iterator iter = this->m_sceneRoleMap.begin();
	while (iter != this->m_sceneRoleMap.end())
	{
		iter->second->BroadMsg();
		++iter;
	}
}

void PublicScene::InsertRole( Role* pRole )
{
	SceneRoleMap::iterator iter = this->m_sceneRoleMap.find(pRole->GetRoleID());
	if(iter != this->m_sceneRoleMap.end())
	{
		GE_EXC<<"repeat PublicScene::InsertRole roleid: ("<<pRole->GetRoleID()<<")."<<GE_END;
		return;
	}
	this->m_sceneRoleMap.insert(std::make_pair(pRole->GetRoleID(), pRole));
}

void PublicScene::RemoveRole( Role* pRole )
{
	SceneRoleMap::iterator iter = this->m_sceneRoleMap.find(pRole->GetRoleID());
	if(iter != this->m_sceneRoleMap.end())
	{
		this->m_sceneRoleMap.erase(iter);
	}
}

Role* PublicScene::SearchRole( GE::Uint64 uRoleID )
{
	SceneRoleMap::iterator iter = this->m_sceneRoleMap.find(uRoleID);
	if(iter == this->m_sceneRoleMap.end())
	{
		return NULL;
	}
	return iter->second;
}

void PublicScene::InsertNPC( NPC* pNPC )
{
	SceneNPCMap::iterator iter = this->m_sceneNPCMap.find(pNPC->GetNPCID());
	if(iter != this->m_sceneNPCMap.end())
	{
		GE_EXC<<"repeat PublicScene::InsertNPC npcid: ("<<pNPC->GetNPCID()<<")."<<GE_END;
		return;
	}
	this->m_sceneNPCMap.insert(std::make_pair(pNPC->GetNPCID(), pNPC));

	if(pNPC->IsBroadcast())
	{
		if(this->m_sceneBroadcastNPCSet.find(pNPC) != this->m_sceneBroadcastNPCSet.end())
		{
			GE_EXC<<"repeat InsertNPC m_sceneBroadcastNPCSet("<<pNPC->GetNPCType()<<")."<<GE_END;
			return;
		}
		this->m_sceneBroadcastNPCSet.insert(pNPC);
		// 标记广播NPC有改变
		this->m_bBroadcastNPCChange = true;
		this->m_bNeedBroadcast = true;
	}
}

void PublicScene::RemoveNPC( NPC* pNPC )
{
	SceneNPCMap::iterator iter = this->m_sceneNPCMap.find(pNPC->GetNPCID());
	if(iter != this->m_sceneNPCMap.end())
	{
		this->m_sceneNPCMap.erase(iter);
	}

	if(pNPC->IsBroadcast())
	{
		BroadcastNPCSet::iterator iter = this->m_sceneBroadcastNPCSet.find(pNPC);
		if(iter != this->m_sceneBroadcastNPCSet.end())
		{
			this->m_sceneBroadcastNPCSet.erase(iter);
			// 标记广播NPC有改变
			this->m_bBroadcastNPCChange = true;
			this->m_bNeedBroadcast = true;
		}
	}
}

MsgBase* PublicScene::GetBroadcastNPCMsg()
{
	if (this->m_bBroadcastNPCChange)
	{
		PackMessage PM;
		PM.PackMsg(enSyncBroadcastNPC);
		NPC* pNPC = NULL;
		PM.PackUi16(static_cast<GE::Uint16>(this->m_sceneBroadcastNPCSet.size()));
		BroadcastNPCSet::iterator iter = this->m_sceneBroadcastNPCSet.begin();
		while(iter != this->m_sceneBroadcastNPCSet.end())
		{
			pNPC = *iter;
			PM.PackUi32(pNPC->GetNPCID());
			PM.PackUi16(pNPC->GetPosX());
			PM.PackUi16(pNPC->GetPosY());
			PM.PackUi16(pNPC->GetNPCType());
			PM.PackUi8(pNPC->GetDirection());
			PM.PackPyObj(pNPC->GetPySyncDict());
			++iter;
		}
		this->m_pBroadcastNPCMsg.assign(static_cast<char*>(PM.GetHead()), PM.GetSize());
		this->m_bBroadcastNPCChange = false;
	}
	return static_cast<MsgBase*>(static_cast<void*>(const_cast<char*>(this->m_pBroadcastNPCMsg.data())));
}

void PublicScene::BroadcastNPC()
{
	if (this->m_bNeedBroadcast)
	{
		this->SendToAllRole(this->GetBroadcastNPCMsg());
		this->m_bNeedBroadcast = false;
	}
}

void PublicScene::BroadcastNPCToRole( Role* pRole )
{
	pRole->SendMsg(this->GetBroadcastNPCMsg());
}

void PublicScene::LoadAfterCreateFun( PyObject* pyFun_BorrowRef )
{
	this->m_pyAfterCreate.Load(pyFun_BorrowRef);
}

void PublicScene::LoadAfterJoinRole( PyObject* pyFun_BorrowRef )
{
	this->m_pyAfterJoinRole.Load(pyFun_BorrowRef);
}

void PublicScene::LoadBeforeLeaveRole( PyObject* pyFun_BorrowRef )
{
	this->m_pyBeforeLevelRole.Load(pyFun_BorrowRef);
}

void PublicScene::LoadRestoreRole( PyObject* pyFun_BorrowRef )
{
	this->m_pyRestoreRole.Load(pyFun_BorrowRef);
}


void PublicScene::AfterJoinRole(Role* pRole )
{
	if (this->m_pyAfterJoinRole.IsNone())
	{
		return;
	}
	this->m_pyAfterJoinRole.Call("OO", this->PySelf().GetObj_BorrowRef(), pRole->GetPySelf().GetObj_BorrowRef());
}

void PublicScene::BeforeLeaveRole(Role* pRole )
{
	if (this->m_pyBeforeLevelRole.IsNone())
	{
		return;
	}
	this->m_pyBeforeLevelRole.Call("OO", this->PySelf().GetObj_BorrowRef(), pRole->GetPySelf().GetObj_BorrowRef());
}


void PublicScene::AfterRestoreRole(Role* pRole )
{
	if (this->m_pyRestoreRole.IsNone())
	{
		return;
	}
	this->m_pyRestoreRole.Call("OO", this->PySelf().GetObj_BorrowRef(), pRole->GetPySelf().GetObj_BorrowRef());
}

bool PublicScene::CheckPosX(Role* pRole, GE::Uint16 uX )
{
	if(uX > pRole->GetPosX())
	{
		return static_cast<GE::Uint16>(uX - pRole->GetPosX()) < static_cast<GE::Uint16>(pRole->GetClientSpeed());
	}
	else
	{
		return static_cast<GE::Uint16>(pRole->GetPosX() - uX) < static_cast<GE::Uint16>(pRole->GetClientSpeed());
	}
}

bool PublicScene::CheckPosY(Role* pRole, GE::Uint16 uY )
{
	if(uY > pRole->GetPosY())
	{
		return static_cast<GE::Uint16>(uY - pRole->GetPosY()) < static_cast<GE::Uint16>(pRole->GetClientSpeed());
	}
	else
	{
		return static_cast<GE::Uint16>(pRole->GetPosY() - uY) < static_cast<GE::Uint16>(pRole->GetClientSpeed());
	}
}

bool PublicScene::IsIgnoreCheckMoveDistanceJap( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	if (this->m_uMoveDistanceJap == 0)
	{
		//没有忽视设定，进入移动逻辑
		return false;
	}
	
	if (pRole->GetPosX() > uX)
	{
		if (pRole->GetPosX() - uX > this->m_uMoveDistanceJap)
		{
			//超出距离，不能忽视，进入移动逻辑
			return false;
		}
	}
	else
	{
		if (uX - pRole->GetPosX() > this->m_uMoveDistanceJap)
		{
			//超出距离，不能忽视
			return false;
		}
	}

	if (pRole->GetPosY() > uY)
	{
		if (pRole->GetPosY() - uY > this->m_uMoveDistanceJap)
		{
			//超出距离，不能忽视，进入移动逻辑
			return false;
		}
	}
	else
	{
		if (uY - pRole->GetPosY() > this->m_uMoveDistanceJap)
		{
			//超出距离，不能忽视
			return false;
		}
	}
	return true;
}

bool PublicScene::IsFlyingPos(Role *pRole)
{
	return this->m_pAreaMap->GridProperty(pRole->GetPosX(), pRole->GetPosY()) == 0;
}

void PublicScene::SetCanSeeOther( bool b )
{
	this->m_bCanSeeOther = b;

	this->m_pAreaMap->SetCanSeeOther(b);
}


