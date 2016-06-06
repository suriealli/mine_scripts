/************************************************************************
我是UTF8编码文件
************************************************************************/
#include "Area.h"
#include "ScriptMgr.h"

Area::Area()
{
}

Area::~Area()
{
}

void Area::JoinPlayer( Role* pRole )
{
	if (pRole->IsLink())
	{
		GE_EXC<<"JoinPlayer error role is link"<<GE_END;
		ScriptMgr::Instance()->StackWarn("Area::JoinPlayer");
	}
	else
	{
		this->m_RoleList.push_back(*pRole);
	}
}

void Area::LeavePlayer( Role* pRole )
{
	if (pRole->IsLink())
	{
		pRole->UnLink();
	}
	else
	{
		GE_EXC<<"LeavePlayer error role not link"<<GE_END;
		ScriptMgr::Instance()->StackWarn("Area::LeavePlayer");
	}
}

void Area::JoinNPC( NPC* pNPC )
{
	if (pNPC->IsLink())
	{
		GE_EXC<<"JoinNPC error pNPC is link"<<GE_END;
	}
	else
	{
		this->m_NPCList.push_back(*pNPC);
	}
}

void Area::LeaveNPC( NPC* pNPC )
{
	if (pNPC->IsLink())
	{
		pNPC->UnLink();
	}
	else
	{
		GE_EXC<<"LeaveNPC error pNPC not link"<<GE_END;
	}
}

