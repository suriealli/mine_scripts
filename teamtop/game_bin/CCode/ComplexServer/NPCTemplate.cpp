#include "NPCTemplate.h"
#include <math.h>
#include "Role.h"
#include "NPCMgr.h"

NPCTemplate::NPCTemplate( GE::Uint16 uNPCType, GE::Uint16 uClickLen, const std::string& strNPCName, GE::Uint8 uClickType, GE::Uint8 uIsMovingNPC)
	: m_uNPCType(uNPCType)
	, m_uClickLen(uClickLen)
	, m_strNPCName(strNPCName)
	, m_uClickType(uClickType)
{
	if (uIsMovingNPC)
	{
		this->m_bIsMovingNPC = true;
	}
	else
	{
		this->m_bIsMovingNPC = false;
	}
}

NPCTemplate::~NPCTemplate()
{

}

void NPCTemplate::LoadClickFun( PyObject* pyFun_BorrowRef )
{
	this->m_pyOnClickFun.Load(pyFun_BorrowRef);
}


//////////////////////////////////////////////////////////////////////////
NPCConfigObj::NPCConfigObj(GE::Uint32 uID, GE::Uint32 uSceneID, GE::Uint16 uNPCType, GE::Uint16 uX, GE::Uint16 uY )
	: m_uID(uID)
	, m_uSceneID(uSceneID)
	, m_uNPCType(uNPCType)
	, m_uX(uX)
	, m_uY(uY)
{
	NPCTemplate* pT = NPCMgr::Instance()->GetNPCTemplate(this->m_uNPCType);
	if (NULL == pT)
	{
		GE_EXC<<"can not find npc temp in new NPCConfigObj NpcType = ("<<this->m_uNPCType<<")"<<GE_END;
		this->m_uClickLen = 0;
		this->m_bIsMovingNPC = false;
	}else
	{
		this->m_uClickLen = pT->GetClickLen();
		this->m_bIsMovingNPC = pT->IsMovingNPC();
	}
}

NPCConfigObj::~NPCConfigObj()
{

}

bool NPCConfigObj::CanClick( Role* pRole )
{
	if (pRole->GetSceneID() != this->m_uSceneID)
	{
		return false;
	}

	if (true == this->m_bIsMovingNPC)
	{
		return true;
	}

	//判断矩形范围内是否可以点击
	GE::Int16 rx = pRole->GetPosX();
	GE::Int16 ry = pRole->GetPosY();
	

	if(abs(rx - static_cast<GE::Int16>(this->m_uX)) > this->m_uClickLen)
	{
		return false;
	}

	if (abs(ry - static_cast<GE::Int16>(this->m_uY)) > this->m_uClickLen)
	{
		return false;
	}
	return true;
}

//////////////////////////////////////////////////////////////////////////

