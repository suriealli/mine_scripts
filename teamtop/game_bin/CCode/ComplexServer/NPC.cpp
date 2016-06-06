#include "NPC.h"
#include "Role.h"
#include "SceneBase.h"
#include "MessageDefine.h"
#include "PyNPC.h"

NPC::NPC( GE::Uint32 uNPCID, NPCTemplate* pNPCTemp, GE::Uint8 uDirection, bool bIsBroadcast, PyObject* py_BorrowRef)
	: m_uNPCID(uNPCID)
	, m_uDirection(uDirection)
	, m_bIsBroadcast(bIsBroadcast)
	, m_pScene(NULL)
	, m_pNPCTemplate(pNPCTemp)
	, m_uX(0)
	, m_uY(0)
	, m_bIsVaild(false)
{
	this->m_pySelf.SetObj_NewRef((PyObject*)ServerPython::PyNPC_New(this));
	if (PyDict_Check(py_BorrowRef))
	{
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyDict_Size(py_BorrowRef));
		Py_ssize_t pos = 0;
		PyObject* key = NULL;
		PyObject* value = NULL;
		GE_ITER_UI16(idx, uSize)
		{
			if(0 == PyDict_Next(py_BorrowRef, &pos, &key, &value))
			{
				GE_EXC<<"error in create npc, npcsyncdata error"<<GE_END;
				continue;
			}
			this->SetPySyncDict(key, value);
		}
	}
}


NPC::~NPC()
{
}

bool NPC::CanClick( Role* pRole )
{
	if (pRole->GetSceneID() != this->GetSceneID())
	{
		return false;
	}

	if (true == this->m_pNPCTemplate->IsMovingNPC())
	{
		return true;
	}

	//判断矩形范围内是否可以点击
	GE::Int16 rx = pRole->GetPosX();
	GE::Int16 ry = pRole->GetPosY();

	if(abs(rx - static_cast<GE::Int16>(this->GetPosX())) > this->GetClickLen())
	{
		return false;
	}

	if (abs(ry - static_cast<GE::Int16>(this->GetPosY())) > this->GetClickLen())
	{
		return false;
	}

	return true;
}

GE::Uint32 NPC::GetSceneID()
{
	if(this->m_pScene)
	{
		return this->m_pScene->GetSceneID();
	}
	else
	{
		return 0;
	}
}

void NPC::SetPos( GE::Uint16 uX, GE::Uint16 uY )
{
	this->m_uX = uX;
	this->m_uY = uY;

	PackMessage PM;
	PM.PackMsg(enNPCPos);
	PM.PackUi32(this->m_uNPCID);
	PM.PackUi16(this->m_pNPCTemplate->GetNPCType());
	PM.PackUi16(this->m_uX);
	PM.PackUi16(this->m_uY);
	PM.PackUi8(this->m_uDirection);
	PM.PackPyObj(this->m_pySyncDict.GetDict_BorrowRef());
	this->m_SyncDataMsg.assign(static_cast<char*>(PM.GetHead()), PM.GetSize());

	this->m_bIsVaild = true;
}


MsgBase* NPC::GetPosMsg()
{
	return static_cast<MsgBase*>(static_cast<void*>(const_cast<char*>(this->m_SyncDataMsg.data())));
}

void NPC::SyncDataToRole(Role* pRole)
{
	if (this->m_bIsVaild == false)
	{
		return;
	}
	pRole->SendMsg(this->GetPosMsg());
}

void NPC::Destroy()
{
	if (this->IsDestroy())
	{
		return;
	}

	if (this->m_pScene)
	{
		this->m_pScene->LeaveNPC(this);
	}

	ServerPython::PyNPC_Del(this->m_pySelf.GetObj_BorrowRef());
	this->m_pySelf.SetNone();

}

void NPC::OnClick( Role* pRole )
{
	if (this->m_pNPCTemplate->m_pyOnClickFun.IsNone())
	{
		return;
	}
	this->m_pNPCTemplate->m_pyOnClickFun.Call("OO", pRole->GetPySelf().GetObj_BorrowRef(), this->GetPySelf().GetObj_BorrowRef());
}

void NPC::SetPyDict( PyObject* key_BorrowRef, PyObject* value_BorrowRef )
{
	//设置
	this->m_pyDict.SetObj_BorrowRef(key_BorrowRef, value_BorrowRef);
}

PyObject* NPC::GetPyDict()
{
	return this->m_pyDict.GetDict_NewRef();
}

void NPC::SetPySyncDict( PyObject* key_BorrowRef, PyObject* value_BorrowRef )
{
	//设置
	this->m_pySyncDict.SetObj_BorrowRef(key_BorrowRef, value_BorrowRef);
}

PyObject* NPC::GetPySyncDict()
{
	return this->m_pySyncDict.GetDict_NewRef();
}

void NPC::AfterChange()
{
	//重新打包
	PackMessage PM;
	PM.PackMsg(enNPCPos);
	PM.PackUi32(this->m_uNPCID);
	PM.PackUi16(this->m_pNPCTemplate->GetNPCType());
	PM.PackUi16(this->m_uX);
	PM.PackUi16(this->m_uY);
	PM.PackUi8(this->m_uDirection);
	PM.PackPyObj(this->m_pySyncDict.GetDict_BorrowRef());
	this->m_SyncDataMsg.assign(static_cast<char*>(PM.GetHead()), PM.GetSize());

	this->m_pScene->SendToRect(this->m_uX, this->m_uY, this->GetPosMsg());
}

