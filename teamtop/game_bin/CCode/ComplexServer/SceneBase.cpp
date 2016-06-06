#include "SceneBase.h"
#include "Role.h"

SceneBase::SceneBase( GE::Uint32 uSceneID, const std::string& sSceneName )
	: m_uSceneID(uSceneID)
	, m_sSceneName(sSceneName)
{

}

SceneBase::~SceneBase()
{

}

bool SceneBase::JoinRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	if (pRole->GetScene())
	{
		pRole->GetScene()->LeaveRole(pRole);
	}
	return true;
}

void SceneBase::LeaveRole( Role* pRole )
{
	this->SaveRoleSceneData(pRole);
}


void SceneBase::SaveRoleSceneData( Role* pRole )
{
}

void SceneBase::CallPerSecond()
{

}

