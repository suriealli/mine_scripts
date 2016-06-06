/*我是UTF8无签名编码 */
#include "SceneMgr.h"
#include "MapMgr.h"
#include "PublicScene.h"
#include "Mirror.h"
#include "Role.h"

GlobalObj::GlobalObj()
	: m_Index(GLOBAL_OBJ_NUM)
{
	// 这里是把0给占掉
	GE_ERROR(0 == this->CreateSceneObj());
}

GlobalObj::~GlobalObj()
{

}

GE::Uint32 GlobalObj::CreateSceneObj( )
{
	GE::Uint32 uID = 0;
	GE::Uint32 uIdx = 0;
	if (this->m_Index.Insert(uID, uIdx))
	{
		return uID;
	}
	else
	{
		return 0;
	}
}

void GlobalObj::DestroySceneObj( GE::Uint32 uID )
{
	GE::Uint32 uIdx = 0;
	if (this->m_Index.Remove(uID, uIdx))
	{
		this->m_ObjInfs[uIdx].Reset();
	}
}

bool GlobalObj::SetSceneObjInfo( GE::Uint32 uID, GE::Uint16 uType, GE::Uint16 uFlag, void* pPRT )
{
	GE::Uint32 uIdx = 0;
	if (this->m_Index.HasID(uID, uIdx))
	{
		SceneObjInfo& SOI = this->m_ObjInfs[uIdx];
		SOI.uType = uType;
		SOI.uFlag = uFlag;
		SOI.pPTR = pPRT;
		return true;
	}
	else
	{
		return false;
	}
}

bool GlobalObj::SetSceneObjPos( GE::Uint32 uID, GE::Uint16 uX, GE::Uint16 uY )
{
	GE::Uint32 uIdx = 0;
	if (this->m_Index.HasID(uID, uIdx))
	{
		this->m_ObjInfs[uIdx].uX = uX;
		this->m_ObjInfs[uIdx].uY = uY;
		return true;
	}
	else
	{
		return false;
	}
}

bool GlobalObj::GetSceneObjPos( GE::Uint32 uID, GE::Uint16& uX, GE::Uint16& uY )
{
	GE::Uint32 uIdx = 0;
	if (this->m_Index.HasID(uID, uIdx))
	{
		uX = this->m_ObjInfs[uIdx].uX;
		uY = this->m_ObjInfs[uIdx].uY;
		return true;
	}
	else
	{
		return false;
	}
}

//////////////////////////////////////////////////////////////////////////
SceneMgr::SceneMgr()
{

}

SceneMgr::~SceneMgr()
{
	// 断言副本都销毁了
	this->CallPerSceond();
#if WIN
	GE_ERROR(this->m_MirrorSceneMap.empty());
#endif
	// 销毁公共场景
	PublicSceneMap::iterator iter = this->m_PublicSceneMap.begin();
	while(iter != this->m_PublicSceneMap.end())
	{
		delete iter->second;
		this->m_PublicSceneMap.erase(iter++);
	}
}

void SceneMgr::LoadPyData()
{
	this->m_pyCreatePublicScene.Load("Game.Scene.SceneMgr", "CreataPublicScene");

}

void SceneMgr::CreateAllPublicScene()
{
	this->m_pyCreatePublicScene.Call();
}

void SceneMgr::CallPerSceond()
{
	PublicSceneMap::iterator iter = this->m_PublicSceneMap.begin();
	while(iter != this->m_PublicSceneMap.end())
	{
		PublicScene* pScene = iter->second;
		pScene->CallPerSecond();
		++iter;
	}

	MirrorSceneMap::iterator sIter = this->m_MirrorSceneMap.begin();
	while(sIter != this->m_MirrorSceneMap.end())
	{
		MirrorBase* pDynamic = sIter->second;
		if(pDynamic->CanDestory())
		{
			delete pDynamic;
			this->m_MirrorSceneMap.erase(sIter++);
		}
		else
		{
			pDynamic->CallPerSecond();
			++sIter;
		}
	}
}

PublicScene* SceneMgr::CreatePublicScene(GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName, GE::Uint8 uAreaSize, GE::Uint8 uIsSave, GE::Uint8 uCanSeeOther, PyObject* pyAfterCreateFun, PyObject* pyAfterJoinRoleFun, PyObject* pyBeforeLeaveFun, PyObject* pyAfterRestoreFun)
{
	MapTemplate *pMT = MapMgr::Instance()->GetHasLoadMapTemplate(uMapID);
	if(NULL == pMT)
	{
		GE_EXC<<"GreateScene error has not MapConfig uMapID: ("<<uMapID<<")"<<GE_END;
		return NULL;
	}
	bool isSave = true;
	if (uIsSave == 0)
	{
		isSave = false;
	}
	bool bCanSeeOther = true;
	if (uCanSeeOther == 0)
	{
		bCanSeeOther = false;
	}
	if (this->m_PublicSceneMap.find(uSceneID) != this->m_PublicSceneMap.end())
	{
		GE_EXC<<"repeat public scene id("<<uSceneID<<")."<<GE_END;
		return NULL;
	}
	PublicScene* pPublicScene = new PublicScene(uSceneID, pSceneName, pMT, uAreaSize, isSave, bCanSeeOther);
	pPublicScene->LoadAfterCreateFun(pyAfterCreateFun);
	pPublicScene->LoadAfterJoinRole(pyAfterJoinRoleFun);
	pPublicScene->LoadBeforeLeaveRole(pyBeforeLeaveFun);
	pPublicScene->LoadRestoreRole(pyAfterRestoreFun);
	this->m_PublicSceneMap.insert(std::make_pair(uSceneID, pPublicScene));
	return pPublicScene;
}

PublicScene* SceneMgr::SearchPublicScene( GE::Uint32 uSceneID )
{
	PublicSceneMap::iterator iter = this->m_PublicSceneMap.find(uSceneID);
	if (iter == this->m_PublicSceneMap.end())
	{
		return NULL;
	}
	return iter->second;
}



SingleMirrorScene* SceneMgr::CreateSingleMirrorScene( GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName, PyObject* pyBeforeLeaveFun)
{
	MirrorSceneMap::iterator sIter = m_MirrorSceneMap.find(uGlobalID);
	if (sIter != m_MirrorSceneMap.end())
	{
		GE_EXC<<"CreateSingleMirrorScene error : SingleMirrorScene uGlobalID = ("<<uGlobalID<<") is existed, uSceneID = ("<<uSceneID<<")."<<GE_END;
		return NULL;
	}
	SingleMirrorScene* pScene = new SingleMirrorScene(uGlobalID, uMapID, uSceneID, pSceneName);
	this->m_MirrorSceneMap.insert(std::make_pair<GE::Uint32, SingleMirrorScene*>(uGlobalID, pScene));

	pScene->LoadBeforeLeaveRole(pyBeforeLeaveFun);
	return pScene;
}

MultiMirrorScene* SceneMgr::CreateMultiMirrorScene( GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName, PyObject* pyBeforeLeaveFun, bool bIsAlive)
{
	MirrorSceneMap::iterator sIter = m_MirrorSceneMap.find(uGlobalID);
	if (sIter != m_MirrorSceneMap.end())
	{
		GE_EXC<<"CreateMultiMirrorScene error : MultiMirrorScene uGlobalID = ("<<uGlobalID<<") is existed, uSceneID = ("<<uSceneID<<")."<<GE_END;
		return NULL;
	}
	MultiMirrorScene* pScene = new MultiMirrorScene(uGlobalID, uMapID, uSceneID, pSceneName, bIsAlive);
	this->m_MirrorSceneMap.insert(std::make_pair<GE::Uint32, MultiMirrorScene*>(uGlobalID, pScene));

	pScene->LoadBeforeLeaveRole(pyBeforeLeaveFun);
	return pScene;
}

