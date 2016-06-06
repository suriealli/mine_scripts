#include "NPCMgr.h"
#include "NPCTemplate.h"
#include "Role.h"
#include "NPC.h"
#include "SceneBase.h"
#include "PublicScene.h"

NPCMgr::NPCMgr()
{
	this->m_AlloGloBalID = MAX_CFG_NPC_ID + 1;
}

NPCMgr::~NPCMgr()
{
	// 销毁所有的NPC
	NPCMap::iterator npc_iter = this->m_NPCMap.begin();
	while(npc_iter != this->m_NPCMap.end())
	{
		npc_iter->second->Destroy();
		++npc_iter;
	}
	// 删除NPC对象
	this->CallPerSecond();
	// Win下断言
#if WIN
	GE_ERROR(this->m_NPCMap.empty());
#endif
	// 销毁配置NPC
	NPCConfigObjMap::iterator config_iter = this->m_NPCConfigObjMap.begin();
	while(config_iter != this->m_NPCConfigObjMap.end())
	{
		delete config_iter->second;
		this->m_NPCConfigObjMap.erase(config_iter++);
	}
	// 销毁NPC模板
	NPCTemplateMap::iterator temp_iter = this->m_NPCTemplateMap.begin();
	while(temp_iter != this->m_NPCTemplateMap.end())
	{
		delete temp_iter->second;
		this->m_NPCTemplateMap.erase(temp_iter++);
	}
}

void NPCMgr::LoadPyData()
{
	this->m_pyClickNPCConfigFun.Load("Game.NPC.NPCCfgFun", "OnClick");
	this->m_pyClickPrivateNPCFun.Load("Game.NPC.PrivateNPC.PrivateNPC", "OnClickPrivateNPC");
	this->m_pyClickMirrorNPCFun.Load("Game.NPC.PrivateNPC.PrivateNPC", "OnClickMirrorNPC");
	this->m_pyLoadClickFun.Load("Game.NPC.NPCMgr", "LoadNPCClickFun");
	this->m_pyLoadClickFun.Call();
}

void NPCMgr::CallPerSecond()
{
	NPCMap::iterator npc_iter = this->m_NPCMap.begin();
	while(npc_iter != this->m_NPCMap.end())
	{
		NPC* pNPC = npc_iter->second;
		if(pNPC->IsDestroy())
		{
			delete pNPC;
			this->m_NPCMap.erase(npc_iter++);
		}
		else
		{
			++npc_iter;
		}
	}
}

void NPCMgr::CreateNPCTemplate( GE::Uint16 uType, const char* name, GE::Uint16 uClickLen, GE::Uint8 uClickType, GE::Uint8 uIsMovingNPC)
{
	NPCTemplateMap::iterator iter = this->m_NPCTemplateMap.find(uType);
	if(iter != this->m_NPCTemplateMap.end())
	{
		GE_EXC<<"repeat CreateNPCTemplate uType: ("<<uType<<")."<<GE_END;
		return;
	}
	else
	{
		this->m_NPCTemplateMap.insert(std::make_pair(uType, new NPCTemplate(uType, uClickLen, name, uClickType, uIsMovingNPC)));
	}
}

void NPCMgr::CreateNPCConfigObj( GE::Uint32 uID, GE::Uint16 uType, GE::Uint32 uSceneID, GE::Uint16 uX, GE::Uint16 uY )
{
	NPCConfigObjMap::iterator iter = this->m_NPCConfigObjMap.find(uID);
	if(iter != this->m_NPCConfigObjMap.end())
	{
		GE_EXC<<"repeat CreateNPCConfigObj uID: ("<<uID<<")."<<GE_END;
		return;
	}
	else
	{
		this->m_NPCConfigObjMap.insert(std::make_pair(uID, new NPCConfigObj(uID, uSceneID, uType, uX, uY)));
	}
}


NPCTemplate* NPCMgr::GetNPCTemplate( GE::Uint16 uType )
{
	NPCTemplateMap::iterator iter = this->m_NPCTemplateMap.find(uType);
	if(iter != this->m_NPCTemplateMap.end())
	{
		return iter->second;
	}
	else
	{
		return NULL;
	}
}

NPCConfigObj* NPCMgr::GetNPCConfigObj( GE::Uint32 uID )
{
	NPCConfigObjMap::iterator iter = this->m_NPCConfigObjMap.find(uID);
	if(iter != this->m_NPCConfigObjMap.end())
	{
		return iter->second;
	}
	else
	{
		return NULL;
	}
}


NPC* NPCMgr::CreateNPC( SceneBase* pScene, GE::Uint16 uTypeID, GE::Uint16 uX, GE::Uint16 uY, GE::Uint8 uDirection, bool bBroadCast, PyObject* py_BorrowRef)
{
	if(NULL == pScene)
	{
		GE_EXC<<"CreateNPC uSceneID error "<<GE_END;
		return NULL;
	}
	NPCTemplate* pNT = this->GetNPCTemplate(uTypeID);
	if(NULL == pNT)
	{
		GE_EXC<<"CreateNPC, NPCTemplate NULL uTypeID = "<<uTypeID<<GE_END;
		return NULL;
	}
	GE::Uint32 uGolbalID = this->AllotGlobalID();
	NPC* pNPC = new NPC(uGolbalID, pNT, uDirection, bBroadCast, py_BorrowRef);
	//pNPC->SetScene(pScene);

	this->InsertNPCToMap(pNPC);
	//pNPC->AfterCreate();

	pScene->JoinNPC(pNPC, uX, uY);
	return pNPC;
}

void NPCMgr::DestroyNPC( GE::Uint32 uGlobalID )
{
	NPC* pNPC = this->SearchNPC(uGlobalID);
	if(pNPC == NULL)
	{
		return;
	}
	else
	{
		pNPC->Destroy();
	}
}

void NPCMgr::DestroyNPC( NPC* pNPC )
{
	if(pNPC == NULL)
	{
		return;
	}
	else
	{
		pNPC->Destroy();
	}
}

NPC* NPCMgr::SearchNPC( GE::Uint32 uNPCID )
{
	NPCMap::iterator iter = this->m_NPCMap.find(uNPCID);
	if (iter != this->m_NPCMap.end())
	{
		return iter->second;
	}
	return NULL;
}

void NPCMgr::InsertNPCToMap( NPC* pNPC )
{
	NPCMap::iterator iter = this->m_NPCMap.find(pNPC->GetNPCID());
	if(iter != this->m_NPCMap.end())
	{
		GE_EXC<<"repeat  NPCMgr::InsertNPCToMap npcid: ("<<pNPC->GetNPCID()<<")."<<GE_END;
		return;
	}
	this->m_NPCMap.insert(std::make_pair(pNPC->GetNPCID(), pNPC));
}

void NPCMgr::ClickCfgNPC( Role* pRole, GE::Uint32 uNPCID )
{
	if (uNPCID <= MAX_CFG_NPC_ID)
	{
		NPCConfigObj* pNPCObj = this->GetNPCConfigObj(uNPCID);
		if (NULL == pNPCObj)
		{
			return;
		}
		//判断点击场景与距离
		if (!pNPCObj->CanClick(pRole))
		{
			return;
		}
		//调用脚本
		this->m_pyClickNPCConfigFun.Call("OI",pRole->GetPySelf().GetObj_BorrowRef(), uNPCID);
		return;
	}
	else
	{
		GE_EXC<<"ClickCfgNPC error "<<uNPCID<<GE_END;
	}
}

void NPCMgr::ClickNPC( Role* pRole, NPC* pNPC )
{
	if (NULL == pNPC)
	{
		return;
	}
	if (!pNPC->CanClick(pRole))
	{
		return;
	}
	//调用脚本函数
	pNPC->OnClick(pRole);
}

void NPCMgr::ClickPrivateNPC( Role* pRole, GE::Uint32 uNPCID)
{
	this->m_pyClickPrivateNPCFun.Call("OI",pRole->GetPySelf().GetObj_BorrowRef(), uNPCID);
}

void NPCMgr::ClickMirrorNPC( Role* pRole, GE::Uint32 uNPCID )
{
	this->m_pyClickMirrorNPCFun.Call("OI",pRole->GetPySelf().GetObj_BorrowRef(), uNPCID);
}


bool NPCMgr::GetFlyNPCPos(GE::Uint32 nNPCID, GE::Uint32& uSceneID, GE::Uint16 &uX, GE::Uint16 &uY )
{
	NPCConfigObj* pNPCObj = this->GetNPCConfigObj(nNPCID);
	if (NULL == pNPCObj)
	{
		return false;
	}
	uSceneID = pNPCObj->GetSceneID();
	uX = pNPCObj->GetPosX();
	uY = pNPCObj->GetPosY();
	return true;
}

void NPCMgr::LoadNPCClickFun( GE::Uint16 uTypeID, PyObject* pyFun_BorrowRef )
{
	NPCTemplate* pNT = this->GetNPCTemplate(uTypeID);
	if(NULL == pNT)
	{
		GE_EXC<<"LoadNPCClickFun, NPCTemplate NULL uTypeID = "<<uTypeID<<GE_END;
		return;
	}
	pNT->LoadClickFun(pyFun_BorrowRef);
}

GE::Uint32 NPCMgr::AllotGlobalID()
{
	if (this->m_AlloGloBalID >= MAX_UINT32)
	{
		this->m_AlloGloBalID = MAX_CFG_NPC_ID + 1;
	}
	return ++m_AlloGloBalID;
}


