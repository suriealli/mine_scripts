/*我是UTF8无签名编码 */
#include "Role.h"
#include "RoleDataMgr.h"
#include "GatewayForward.h"
#include "MessageDefine.h"
#include "AreaMap.h"
#include "SceneMgr.h"
#include "RoleMgr.h"
#include "PyRole.h"
#include "SceneBase.h"
#include "LogTransaction.h"
#include "ScriptMgr.h"



// 保存间隔
#define SAVE_JAP_SECOND 333
// 经验积累
#define ACCUMULATE_EXP  100000
// 金钱积累
#define ACCUMULATE_MONEY 20000

// 检测是否被T掉
#define CHECK_KICK	if (this->IsKick()) return;
// 最大的自动恢复体力值
#define MAX_TILI 150

// 检测变化量是否是整数
#define CHECK_JAP	\
	if (this->IsKick() || jap == 0) return;	\
	if (jap < 0)	\
	{	\
		GE_EXC<<"role("<<this->GetRoleID()<<") "<<__FUNCTION__<<" index("<<uIdx<<") jap < 0."<<GE_END;	\
		return;	\
	}

// 初始化数组
#define INIT_ARRAY(itype, ivector, ifun, msgtype, ipack, frule)	\
	if (Py_None == arg_BorrowRef)	\
	{	\
		return;	\
	}	\
	if (!PyString_CheckExact(arg_BorrowRef))	\
	{	\
		GE_EXC<<"role("<<this->GetRoleID()<<") "<<__FUNCTION__<<" need string."<<GE_END;	\
		this->Kick();	\
		return;	\
	}	\
	void* pHead = PyString_AS_STRING(arg_BorrowRef);	\
	GE::Uint16 uSize = static_cast<GE::Uint16>((PyString_GET_SIZE(arg_BorrowRef) / sizeof(itype)));	\
	itype* pV = static_cast<itype*>(pHead);	\
	ivector& IV = this->ifun();	\
	if (IV.size() < uSize)	\
	{	\
		GE_EXC<<"role("<<this->GetRoleID()<<") IV("<<IV.size()<<") < uSize("<<uSize<<") in "<<__FUNCTION__<<GE_END;	\
		this->Kick();	\
		return;	\
	}	\
	PackMessage PM;	\
	PM.PackMsg(msgtype);	\
	GE_ITER_UI16(uIdx, uSize)	\
	{	\
		itype nValue = (*pV);	\
		IV.at(uIdx) = nValue;	\
		if (RoleDataMgr::Instance()->frule(uIdx).bSyncClient && nValue != 0)	\
		{	\
			PM.PackI16(uIdx);	\
			PM.ipack(nValue);	\
		}	\
		pV += 1;	\
	}	\
	this->SendMsg(PM.Msg());


#define SYNC_ARRAY(itype, ivector, ifun, msgtype, ipack, frule)	\
	ivector& IV = this->ifun();	\
	PackMessage PM;	\
	PM.PackMsg(msgtype);	\
	GE_ITER_UI16(uIdx, IV.size())	\
	{	\
		itype nValue = IV.at(uIdx);	\
		if (RoleDataMgr::Instance()->frule(uIdx).bSyncClient && nValue != 0)	\
			{	\
			PM.PackI16(uIdx);	\
			PM.ipack(nValue);	\
			}	\
	}	\
	this->SendMsg(PM.Msg());


// 初始化数组
#define INIT_ARRAY_NOT_RULE(itype, ivector, ifun, msgtype, ipack)	\
	if (Py_None == arg_BorrowRef)	\
	{	\
		return;	\
	}	\
	if (!PyString_CheckExact(arg_BorrowRef))	\
	{	\
		GE_EXC<<"role("<<this->GetRoleID()<<") "<<__FUNCTION__<<" need string."<<GE_END;	\
		this->Kick();	\
		return;	\
	}	\
	void* pHead = PyString_AS_STRING(arg_BorrowRef);	\
	GE::Uint16 uSize = static_cast<GE::Uint16>((PyString_GET_SIZE(arg_BorrowRef) / sizeof(itype)));	\
	itype* pV = static_cast<itype*>(pHead);	\
	ivector& IV = this->ifun();	\
	if (IV.size() < uSize)	\
	{	\
		GE_EXC<<"role("<<this->GetRoleID()<<") IV("<<IV.size()<<") < uSize("<<uSize<<") in "<<__FUNCTION__<<GE_END;	\
		this->Kick();	\
		return;	\
	}	\
	PackMessage PM;	\
	PM.PackMsg(msgtype);	\
	GE_ITER_UI16(uIdx, uSize)	\
	{	\
		itype nValue = (*pV);	\
		IV.at(uIdx) = nValue;	\
		if (nValue != 0)	\
		{	\
			PM.PackI16(uIdx);	\
			PM.ipack(nValue);	\
		}	\
		pV += 1;	\
	}	\
	this->SendMsg(PM.Msg());


// 序列化数组
#define SERI_ARRAY(ivector, ifun, ipack)	\
	PackMessage PM;	\
	PM.PackMsg(0);	\
	ivector& IV = this->ifun();	\
	GE_ITER_UI16(uIdx, static_cast<GE::Uint16>(IV.size()))	\
	{	\
		PM.ipack(IV.at(uIdx));	\
	}	\
	return PyString_FromStringAndSize(static_cast<const char*>(PM.GetBodyHead()), PM.GetBodySize());	\

// 做设置
#define DO_SET(ipack)	\
	if (uIdx >= IV.size())	\
	{	\
		GE_EXC<<__FUNCTION__<<"uIdx("<<uIdx<<") >= IV.size("<<IV.size()<<")."<<GE_END;	\
		return;	\
	}	\
	if (IV.at(uIdx) == val) {return;}	\
	if (DR.bLogEvent)	\
	{	\
		LogTransaction::Instance()->LogValue(this->GetRoleID(), DR.uCoding, IV.at(uIdx), val);	\
	}	\
	GE::Int64 nOld = IV.at(uIdx);\
	IV.at(uIdx) = val;	\
	if (DR.bSyncClient)	\
	{	\
		PackMessage PM;	\
		PM.PackMsg(DR.uCoding);	\
		PM.ipack(val);	\
		this->SendMsg(PM.Msg());	\
	}	\
	if (NULL != DR.pyChangeFun)	\
	{	\
		GEPython::Object oldValue = GEPython::PyObjFromI64(nOld);\
		GEPython::Object newValue = GEPython::PyObjFromI64(val);\
		PyObject* pyResult_NewRef = PyObject_CallFunctionObjArgs(DR.pyChangeFun, this->GetPySelf().GetObj_BorrowRef(), oldValue.GetObj_BorrowRef(), newValue.GetObj_BorrowRef(), NULL);	\
		if (NULL == pyResult_NewRef)	\
		{	\
			PyErr_Print();	\
		}	\
		else	\
		{	\
			Py_DECREF(pyResult_NewRef);	\
		}	\
	}

// 做加法
#define DO_INC(vtype, frule, fget, fset)	\
	const DataRule& DR = RoleDataMgr::Instance()->frule(uIdx);	\
	const GE::Int64 nOldValue = static_cast<GE::Int64>(this->fget(uIdx));	\
	const GE::Int64 nChange = static_cast<GE::Int64>(jap);	\
	if ( (DR.nMaxValue < nOldValue + nChange))	\
	{	\
		if (DR.uCoding == 23552)\
		{	\
			GE_EXC << "role(" << this->GetRoleID() << ") "  <<" WPE --> Kick" << GE_END;	\
		}	\
		else\
		{	\
			GE_EXC << "role(" << this->GetRoleID() << ") " << __FUNCTION__ << " index(" << uIdx << ") " << nOldValue << " + " << nChange << " > " << DR.nMaxValue << GE_END;	\
		}	\
		if (DR.nMaxAction == DoNothing)	\
		{	\
			this->fset(uIdx, static_cast<vtype>(DR.nMaxValue));	\
		}	\
		else if (DR.nMaxAction == DoRound)	\
		{	\
			this->fset(uIdx, static_cast<vtype>(DR.nMaxValue));	\
		}	\
		else if (DR.nMaxAction == DoKick)	\
		{	\
			this->Kick();	\
		}	\
	}	\
	else	\
	{	\
		this->fset(uIdx, static_cast<vtype>(nOldValue + nChange));	\
	}

// 做减法
#define DO_DEC(vtype, frule, fget, fset)	\
	const DataRule& DR = RoleDataMgr::Instance()->frule(uIdx);	\
	const GE::Int64 nOldValue = static_cast<GE::Int64>(this->fget(uIdx));	\
	const GE::Int64 nChange = static_cast<GE::Int64>(jap);	\
	if ((nOldValue - nChange < DR.nMinValue))	\
	{	\
		GE_EXC<<"role("<<this->GetRoleID()<<") "<<__FUNCTION__<<" index("<<uIdx<<") "<<nOldValue<<" - "<<jap<<" < "<<DR.nMinValue<<GE_END;	\
		ScriptMgr::Instance()->StackWarn("DO_DEC Warning!");\
		if (DR.nMinAction == DoNothing)	\
		{	\
			this->fset(uIdx, static_cast<vtype>(DR.nMinValue));	\
		}	\
		else if (DR.nMinAction == DoRound)	\
		{	\
			this->fset(uIdx, static_cast<vtype>(DR.nMinValue));	\
		}	\
		else if (DR.nMinAction == DoKick)	\
		{	\
			this->Kick();	\
		}	\
	}	\
	else	\
	{	\
		this->fset(uIdx, static_cast<vtype>(nOldValue - jap));	\
	}


Role::Role( GE::Uint64 uRoleID, const std::string& sRoleName, const std::string& sOpenID, GE::Uint64 uClientKey, GE::Uint32 uObjID, GE::Uint32 uCommandSize, GE::Uint32 uCommandIndex )
	: RoleData(uRoleID, sRoleName, sOpenID, uCommandSize, uCommandIndex)
	, m_uClientKey(uClientKey)
	, m_uObjID(uObjID)
	, m_pScene(NULL)
	, m_uTX(0)
	, m_uTY(0)
	, m_uX(0)
	, m_uY(0)
	, m_uZ(0)
	, m_uVersion1(0)
	, m_uVersion2(0)
	, m_bAppChangeFlag1(true)
	, m_bAppChangeFlag2(true)
	, m_bChatInfoChange(true)
	, m_bIsLockMove(false)
	, m_uLastMovingTime(0)
	, m_bNeedRecount(true)
	, m_uHpTime(0)
	, m_uAccumulateIncExp(0)
	, m_uAccumulateIncMoney(0)
	, m_uAccumulateDecMoney(0)
{
	this->m_pySelf.SetObj_NewRef((PyObject*)ServerPython::PyRole_New(this));
	this->m_pyClientKey.SetObj_NewRef(GEPython::PyObjFromUI64(uClientKey));

	this->m_Tick.SetOwner(this->m_pySelf.GetObj_BorrowRef());
	//目标点缓存消息
	this->m_TPosMsg.uRoleID = uRoleID;
	this->m_TPosMsg.uTX = 0;
	this->m_TPosMsg.uTY = 0;
	this->m_TPosMsg.uX = 0;
	this->m_TPosMsg.uY = 0;
	this->m_TPosMsg.uVersion1 = 0;
	this->m_TPosMsg.uVersion2 = 0;
	//当前坐标缓存消息
	this->m_NPosMsg.uRoleID = uRoleID;
	this->m_NPosMsg.uVersion1 = 0;
	this->m_NPosMsg.uVersion2 = 0;
	this->m_NPosMsg.uX = 0;
	this->m_NPosMsg.uY = 0;
	//外观状态缓存消息
	this->m_AppStatusMsg.uRoleID = uRoleID;
	this->m_AppStatusMsg.uAppStatus = 0;
	this->m_AppStatusMsg.uAppStatusVersion = 0;

	
}

Role::~Role()
{
	this->Kick();
}

void Role::Kick()
{
	//默认保存并且T掉，告诉原因是Py_None(未知)
	this->Kick(Py_True, Py_None);
}

void Role::Kick(PyObject* isSave_BorrowRef, PyObject* res_BorrowRef )
{
	if (this->IsKick())
	{
		return;
	}
	RoleMgr::Instance()->BeforeKickRole(this->m_pySelf.GetObj_BorrowRef());
	if (this->m_pScene)
	{
		m_pScene->LeaveRole(this);
		this->m_pScene = NULL;
	}
	//移除全局对象
	GlobalObj::Instance()->DestroySceneObj(this->m_uObjID);

	//保存
	if (isSave_BorrowRef == Py_True)
	{
		this->Save();
	}
	//告诉踢掉的原因
	if (res_BorrowRef != Py_True)
	{
		RoleMgr::Instance()->KickClient(this->m_pyClientKey.GetObj_BorrowRef(), res_BorrowRef);
	}
	// 通知脚本
	ServerPython::PyRoleObject* pyRoleObj = ServerPython::PyRole_FromObj(this->GetPySelf().GetObj_BorrowRef());
	if (pyRoleObj)
	{
		RoleMgr::Instance()->ExitRole(pyRoleObj->role_id);
	}
	ServerPython::PyRole_Del(this->m_pySelf.GetObj_BorrowRef());
	this->m_pySelf.SetNone();
}


void Role::Lost()
{
	//断开连接
	RoleMgr::Instance()->LostClient(this->GetClientKey(), this->m_pyClientKey.GetObj_BorrowRef());
	//修改当前clientkey
	this->m_uClientKey = MAX_UINT64;
	this->m_pyClientKey.SetObj_NewRef(GEPython::PyObjFromUI64(this->m_uClientKey));

	//修正最后的场景和坐标
	if (NULL != this->m_pScene)
	{
		if (this->m_pScene->IsSave())
		{
			this->SetLastSceneID(this->GetSceneID());
			this->SetLastPosX(this->GetPosX());
			this->SetLastPosY(this->GetPosY());
		}
	}
}

bool Role::ReLogin(GE::Uint64 uClientKey)
{
	if (this->m_uClientKey != MAX_UINT64)
	{
		GE_EXC<<"ReLogin has usable clientkey "<<this->GetRoleID()<<GE_END;
		return false;
	}
	this->m_uClientKey = uClientKey;
	this->m_pyClientKey.SetObj_NewRef(GEPython::PyObjFromUI64(uClientKey));
	RoleMgr::Instance()->ReLogin(uClientKey, this);
	return true;
}


void Role::Save()
{
	// 记录角色的保存时间
	this->SetDI32(RoleDataMgr::Instance()->uLastSaveProcessIDIndex, GEProcess::Instance()->ProcessID());
	this->SetDI32(RoleDataMgr::Instance()->uLastSaveUnixTimeIndex, static_cast<GE::Int32>(GEDateTime::Instance()->Seconds()));
	RoleMgr::Instance()->SaveRole(this->m_pySelf.GetObj_BorrowRef());
}

void Role::CallPerSecond()
{
	CHECK_KICK;
	// 触发Tick
	this->m_Tick.CallPerSecond();
	//再次检测，因为每秒调用会有可能把角色踢了
	CHECK_KICK;
	// 检查属性重算
	this->CheckRecountProperty();
	// 计算在线时间
	GE::Int32 nOnlineTime = this->GetDI32(RoleDataMgr::Instance()->uOnlineTimesIndex) + 1;
	this->SetDI32(RoleDataMgr::Instance()->uOnlineTimesIndex, nOnlineTime);
	GE::Int32 nOnlienTimeToday = this->GetI32(RoleDataMgr::Instance()->uOnlineTimesTodayIndex) + 1;
	this->SetI32(RoleDataMgr::Instance()->uOnlineTimesTodayIndex, nOnlienTimeToday);
	this->IncTI64(RoleDataMgr::Instance()->uLoginOnlineTimeIndex, 1);
	// 触发保存和同步在线时间
	if (nOnlineTime % SAVE_JAP_SECOND == 0)
	{
		this->Save();
		this->SyncI32(RoleDataMgr::Instance()->uOnlineTimesTodayIndex, nOnlienTimeToday);
	}
	if (nOnlineTime % 60 == 0)
	{
		MsgSyncTime msg;
		msg.uTime = GEDateTime::Instance()->Seconds();
		this->SendMsg(&msg);
	}
}

void Role::CallAfterNewMinute()
{
	// 每分钟清0 WPE计数器
	this->SetTI64(RoleDataMgr::Instance()->uWPEIndex, 0);
	// 计算体力
	this->CountTiLi();
}


void Role::CountTiLi()
{
	GE::Uint32 uTilijap = 0;
	GE::Uint32 uNowMin = GEDateTime::Instance()->Minutes();
	GE::Uint32 uTiLiMin = static_cast<GE::Uint32>(this->GetI32(RoleDataMgr::Instance()->uTiLiMinuteIndex));
	if(uTiLiMin + 30 < uNowMin)
	{
		LogTransaction::Instance()->StartTransaction(30004);
		GE::Uint32 uCnt = (uNowMin - uTiLiMin) / 30;
		GE::Uint16 uNowTiLi = this->GetTiLi();
		if (uNowTiLi < MAX_TILI)
		{
			if(uNowTiLi + uCnt * 5 > MAX_TILI)
			{
				//体力溢出值
				uTilijap = uNowTiLi + uCnt * 5 - MAX_TILI;
				this->SetTiLi(MAX_TILI);
			}
			else
			{
				this->IncTiLi(uCnt * 5);
			}
		}
		else
		{
			uTilijap = uCnt * 5;
		}
		if (uTilijap > 0)
		{
			//调用脚本
			RoleMgr::Instance()->TiLiJap(this, uTilijap);
		}
		this->IncI32(RoleDataMgr::Instance()->uTiLiMinuteIndex, uCnt * 30);
		LogTransaction::Instance()->EndTransaction();
	}
}


void Role::CallAfterNewDay()
{
	this->ClearPerDay();
}

void Role::ClearPerDay()
{
	// 今天已经清理过了，忽视之
	GE::Int32 nDays = static_cast<GE::Int32>(GEDateTime::Instance()->Days());
	GE::Int32 nLastDays = this->GetDI32(RoleDataMgr::Instance()->uLastClearDaysIndex);
	if (nLastDays >= nDays)
	{
		return;
	}
	LogTransaction::Instance()->StartTransaction(30010);
	this->SetDI32(RoleDataMgr::Instance()->uLastClearDaysIndex, nDays);
	// 清零每日数组
	GE_ITER_UI16(uIdx, this->GetDayInt8Array().size())
	{
		this->GetDayInt8Array()[uIdx] = 0;
	}
	GE_ITER_UI16(uIdx, this->GetDayInt1Array().size())
	{
		this->GetDayInt1Array()[uIdx] = 0;
	}
	// 通知客户端
	MsgBase MB_DI8(enProcessMsg_RoleSyncDayInt8);
	this->SendMsg(&MB_DI8);
	MsgBase MB_DI1(enProcessMsg_RoleSyncDayInt1);
	this->SendMsg(&MB_DI1);
	// 每日在线时间清零和同步客户端
	this->SetI32(RoleDataMgr::Instance()->uOnlineTimesTodayIndex, 0);
	this->SyncI32(RoleDataMgr::Instance()->uOnlineTimesTodayIndex, 0);
	// 最大登录天数+1
	this->IncI16(RoleDataMgr::Instance()->uMaxLoginDaysIndex, 1);
	// 连续登录
	if (nLastDays + 1 == nDays)
	{
		// 当前连续登录天数+1
		GE::Int16 nMCD = this->GetI16(RoleDataMgr::Instance()->uContinueLoginDaysIndex) + 1;
		this->SetI16(RoleDataMgr::Instance()->uContinueLoginDaysIndex, nMCD);
		// 最大连续登录天数
		if (this->GetI16(RoleDataMgr::Instance()->uMaxContinueLoginDaysIndex) < nMCD)
		{
			this->SetI16(RoleDataMgr::Instance()->uMaxContinueLoginDaysIndex, nMCD);
		}
	}
	LogTransaction::Instance()->EndTransaction();
	//调用python函数进行其他清零
	RoleMgr::Instance()->RoleDayClear(this);
}

void Role::SendMsg( MsgBase* pMsg )
{
	CHECK_KICK;
	ClientMgr::Instance()->SendClientMsg(this->m_uClientKey, pMsg);
	this->SendOneMessage(pMsg->Type());
}

void Role::SendPyMsg( GE::Uint16 uMsgType, PyObject* msg_BorrowRef )
{
	CHECK_KICK;
	PackMessage PM;
	MsgBase MB(uMsgType);
	PM.PackMsg(&MB, MB.Size());
	PM.PackPyObj(msg_BorrowRef);
	this->SendMsg(PM.Msg());

#if WIN
	GEPython::Object pyType = GEPython::PyObjFromUI32(uMsgType);
	ScriptMgr::Instance()->m_pyDebugDoSendObj.CallObjArgs(4, this->GetPySelf().GetObj_BorrowRef(), pyType.GetObj_BorrowRef(), msg_BorrowRef, Py_None, NULL);
#endif
}

void Role::SendPyMsgAndBack( GE::Uint16 uMsgType, PyObject* msg_BorrowRef, GE::Uint32 uSec, PyObject* cbfun_BorrowRef, PyObject* regparam_BorrowRef )
{
	CHECK_KICK;
	PackMessage PM;
	MsgBase MB(uMsgType);
	PM.PackMsg(&MB, MB.Size());
	GE::Int32 uTickID = 0;
	// 如果没回调函数就不用注册Tick了
	if (cbfun_BorrowRef != Py_None)
	{
		uTickID = this->m_Tick.RegTick(uSec, cbfun_BorrowRef, regparam_BorrowRef);
		// 居然找不到TickID
		if (0 == uTickID)
		{
			GE_EXC<<"role("<<this->GetRoleID()<<") tick reg error on SendPyMsgAndBack."<<GE_END;
			this->Kick();
		}
	}
	PM.PackSpe1(uTickID, msg_BorrowRef);
	this->SendMsg(PM.Msg());

#if WIN
	GEPython::Object pyType = GEPython::PyObjFromUI32(uMsgType);
	ScriptMgr::Instance()->m_pyDebugDoSendObj.CallObjArgs(4, this->GetPySelf().GetObj_BorrowRef(), pyType.GetObj_BorrowRef(), msg_BorrowRef, cbfun_BorrowRef, NULL);
#endif
}

void Role::BroadMsg()
{
	this->SendMsg(PackMessage::Instance()->Msg());
}

void Role::CallBackFunction( GE::Uint32 uFunID, PyObject* arg_BorrowRef )
{
	CHECK_KICK;
	PackMessage PM;
	MsgBase MB(enProcessMsg_RoleCallBack);
	PM.PackMsg(&MB, MB.Size());
	PM.PackUi32(uFunID);
	PM.PackPyObj(arg_BorrowRef);
	this->SendMsg(PM.Msg());

#if WIN
	ScriptMgr::Instance()->m_pyDebugDoCallback.CallObjArgs(2, this->GetPySelf().GetObj_BorrowRef(), arg_BorrowRef, NULL);
#endif
}

void Role::OnCallBackFunction( MsgBase* pMsg )
{
	CHECK_KICK;
	GE::Int32 nTckIDs = 0;
	GEPython::Object obj;
	UnpackMessage UM(pMsg);
	UM.UnpackMsg(sizeof(MsgBase));
	UM.UnpackI32(nTckIDs);
	UM.UnpackPyObj(obj);

#if WIN
	PyObject* pyFun_BorrowRef = this->m_Tick.GetFun_BorrowRef(nTckIDs);
	if (pyFun_BorrowRef)
	{
		ScriptMgr::Instance()->m_pyDebugOnCallback.CallObjArgs(3, this->GetPySelf().GetObj_BorrowRef(), pyFun_BorrowRef, obj.GetObj_BorrowRef(), NULL);
	}
#endif

	if (UM.HasError())
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") unpack role call back error."<<GE_END;
		this->Kick();
	}
	else
	{
		this->m_Tick.TriggerTick(nTckIDs, obj.GetObj_BorrowRef());
	}
}

void Role::OnMovePos(GE::Uint16 uX, GE::Uint16 uY)
{
	if (!CheckMovePos(uX, uY))
	{
		return;
	}
	this->m_pScene->MoveRole(this, uX, uY);
}

void Role::ToTargetPos( GE::Uint16 uX, GE::Uint16 uY)
{
	// 玩家请求到达某个目的坐标
	if (!CheckTargetPos(uX, uY))
	{
		return;
	}
	// 向这个玩家所在九宫格内的玩家同步自己的目的坐标
	this->SetTargrtPos(uX, uY);
	if (this->m_pScene)
	{
		if (this->m_pScene->CanSeeOther())
		{
			this->m_pScene->SendToRect(this->GetPosX(), this->GetPosY(), this->GetTPosMsg());
		}
	}
}


bool Role::CheckTargetPos( GE::Uint16 uX, GE::Uint16 uY )
{
	//检查客户端发送过来的坐标的正确性
	if (uX == 0 || uY == 0)
	{
		return false;
	}
	if (uX == this->m_uTX && uY == this->m_uTY)
	{
		//等于当前目标坐标
		return false;
	}

	if (uX == this->m_uX && uY == this->m_uY)
	{
		//等于当前坐标
		return false;
	}
	return true;
}


bool Role::CheckMovePos( GE::Uint16 uX, GE::Uint16 uY )
{
	//检查客户端发送过来的坐标的正确性
	if (uX == 0 || uY == 0)
	{
		return false;
	}
	if (uX == this->m_uX && uY == this->m_uY)
	{
		//等于当前坐标
		return false;
	}
	return true;
}

void Role::ClearTargerPos()
{
	//清理目的点坐标
	//传送，闪烁，等都要处理
	this->SetTargrtPos(0, 0);
}

void Role::SetPos( GE::Uint16 uX, GE::Uint16 uY )
{
	this->m_uX = uX;
	this->m_uY = uY;
	//缓存消息数据更新
	this->m_TPosMsg.uX = this->m_uX;
	this->m_TPosMsg.uY = this->m_uY;

	this->m_NPosMsg.uX = this->m_uX;
	this->m_NPosMsg.uY = this->m_uY;
}

void Role::SetPosEx( GE::Uint16 uX, GE::Uint16 uY )
{
	this->m_uX = uX;
	this->m_uY = uY;
}

void Role::SetTargrtPos( GE::Uint16 uX, GE::Uint16 uY )
{
	this->m_uTX = uX;
	this->m_uTY = uY;
	//缓存消息数据更新
	this->m_TPosMsg.uTX = uX;
	this->m_TPosMsg.uTY = uY;
}

//////////////////////////////////////////////////////////////////////////
//uCode
//0: 普通
//1: 传送静止

void Role::DoIdle(GE::Uint8 uCode)
{
	MsgSyncRoleIdle msg;
	msg.uX = this->m_uX;
	msg.uY = this->m_uY;
	msg.uCode = uCode;
	this->SendMsg(&msg);
}

MsgBase* Role::GetPosMsg()
{
	if(this->m_uTX == 0 || this->m_uTY == 0)
	{
		return this->GetNPosMsg();
	}
	else
	{
		return this->GetTPosMsg();
	}
}


///////////////////////////////////////////
void Role::ChangeVersion1()
{
	if (this->m_uVersion1 >= MAX_UINT16)
	{
		//循环用
		this->m_uVersion1 = 0;
	}
	else
	{
		++this->m_uVersion1;
	}
	
	//缓存消息数据更新
	this->m_TPosMsg.uVersion1 = this->m_uVersion1;
	this->m_NPosMsg.uVersion1 = this->m_uVersion1;
	
	//缓存消息字典版本号更新
	this->m_ApperanceDict.SetObj_NewRef(GEPython::PyObjFromI32(RoleDataMgr::Instance()->uEnumAppVersion1), GEPython::PyObjFromI32(this->GetVersion1()));

	if (this->m_pScene)
	{
		if (this->m_pScene->CanSeeOther())
		{
			//同步版本信息,等待客户端请求数据
			//(不要直接发送，可能改变外观会是多次，只改变版本号，等客户端请求时，这个时候外观已经多次改变的代码已经执行完毕)
			MsgSyncRoleVersion msg;
			msg.uRoleID = this->GetRoleID();
			msg.uVersion = this->m_uVersion1;
			this->m_pScene->SendToRect(this->GetPosX(), this->GetPosY(), &msg);
		}
	}
}

void Role::SetAppStatus( GE::Uint16 uValue )
{
	//设置外观状态(频率比较高)
	if (uValue == this->GetTI64(RoleDataMgr::Instance()->uRoleAppStatusIndex))
	{
		//相同
		return;
	}
	//设置状态
	this->SetTI64(RoleDataMgr::Instance()->uRoleAppStatusIndex, uValue);
	//更新缓存的外观消息字典
	this->m_ApperanceDict.SetObj_NewRef(GEPython::PyObjFromI32(RoleDataMgr::Instance()->uEnumAppStatus), GEPython::PyObjFromUI32(uValue));

	//设置已经改变外观，等待重新打包外观数据
	this->m_bAppChangeFlag2 = true;
	//外观状态缓存消息更新
	this->m_AppStatusMsg.uAppStatus = uValue;
	//马上同步状态信息
	this->ChangeVersion2();
}

void Role::ChangeVersion2()
{
	if (this->m_uVersion2 >= MAX_UINT16)
	{
		this->m_uVersion2 = 0;
	}
	else
	{
		++this->m_uVersion2;
	}

	//缓存消息版本号更新
	this->m_TPosMsg.uVersion2 = this->m_uVersion2;
	this->m_NPosMsg.uVersion2 = this->m_uVersion2;

	//缓存消息版本号更新
	this->m_AppStatusMsg.uAppStatusVersion = this->m_uVersion2;
	//设置最新的版本号
	this->m_ApperanceDict.SetObj_NewRef(GEPython::PyObjFromI32(RoleDataMgr::Instance()->uEnumAppVersion2), GEPython::PyObjFromI32(this->GetVersion2()));

	if (this->m_pScene)
	{
		if (this->m_pScene->CanSeeOther())
		{
			//视野内同步状态版本信息(这个可以直接发送，因为只有一个状态)
			this->m_pScene->SendToRect(this->GetPosX(), this->GetPosY(), this->GetRoleSyncAppStatusMsg());

			//发给全场景
			//this->m_pScene->SendToAllRole(this->GetRoleSyncAppStatusMsg());
		}
	}
}


void Role::SetApperance( PyObject* key_BorrowRef, PyObject* value_BorrowRef )
{
	//设置外观(频率比较低)
	this->m_ApperanceDict.SetObj_BorrowRef(key_BorrowRef, value_BorrowRef);
	
	if (this->m_bAppChangeFlag1 == false)
	{
		//设置已经改变外观
		this->m_bAppChangeFlag1 = true;
		//多次改变外观后，重新打包之前，只改变版本号一次
		this->ChangeVersion1();
	}
}

MsgBase* Role::GetRoleSyncAppearanceMsg()
{
	if (this->m_bAppChangeFlag1 || this->m_bAppChangeFlag2)
	{
		//重新打包外观消息
		PackMessage PM;
		PM.PackMsg(enSyncRoleAppreanceData);
		PM.PackPyObj(this->m_ApperanceDict.GetDict_BorrowRef());
		this->m_ApperanceMsg.assign(static_cast<char*>(PM.GetHead()), PM.GetSize());
		this->m_bAppChangeFlag1 = false;
		this->m_bAppChangeFlag2 = false;
	}
	return static_cast<MsgBase*>(static_cast<void*>(const_cast<char*>(this->m_ApperanceMsg.data())));
}

MsgBase* Role::GetRoleSyncAppStatusMsg()
{
	return &this->m_AppStatusMsg;
}

PyObject* Role::GetRoleSyncAppearanceObj()
{
	return this->m_ApperanceDict.GetDict_NewRef();
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////
void Role::SetChatInfo( PyObject* key_BorrowRef, PyObject* value_BorrowRef )
{
	this->m_ChatInfoDict.SetObj_BorrowRef(key_BorrowRef, value_BorrowRef);
	this->m_bChatInfoChange = true;
}

std::string& Role::GetRoleChatInfoMsg()
{
	if (this->m_bChatInfoChange)
	{
		PackMessage PM;
		PM.PackMsg(0);
		PM.PackPyObj(this->m_ChatInfoDict.GetDict_BorrowRef());
		this->m_ChatInfoMsg.assign(static_cast<char*>(PM.GetBodyHead()), PM.GetBodySize());
		this->m_bChatInfoChange = false;
	}
	return this->m_ChatInfoMsg;
}

void Role::SetCanChatTime( GE::Int32 nSecond )
{
	this->SetDI32(RoleDataMgr::Instance()->uCanChatTimeIndex, nSecond);
}

bool Role::CanChat()
{
	return static_cast<GE::Uint32>(this->GetDI32(RoleDataMgr::Instance()->uCanChatTimeIndex)) < GEDateTime::Instance()->Seconds();
}

void Role::SyncDataBase()
{
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncDataBase);
	PM.PackI64(this->GetRoleID());
	PM.PackStream_1(this->GetRoleName().c_str(), static_cast<GE::Uint8>(this->GetRoleName().size()));
	this->SendMsg(PM.Msg());
}

void Role::SyncOK()
{
	MsgBase msg(enProcessMsg_RoleSyncOK);
	this->SendMsg(&msg);
}

void Role::SyncByReLogin()
{
	this->SyncI64();
	this->SyncI32();
	this->SyncI16();
	this->SyncI8();
	this->SyncI1();
	this->SyncDI64();
	this->SyncDI32();
	this->SyncDI8();
	this->SyncDI1();
	this->SyncCD();
	this->SyncCI8();
	this->SyncTI64();

	this->SyncFlyState();
}

//////////////////////////////////////////////////////////////////////////

void Role::InitI64( PyObject* arg_BorrowRef )
{
	INIT_ARRAY(GE::Int64, Role::Int64Vector, GetInt64Array, enProcessMsg_RoleSyncInt64, PackI64, GetInt64Rule);
}

void Role::SyncI64( )
{
	SYNC_ARRAY(GE::Int64, Role::Int64Vector, GetInt64Array, enProcessMsg_RoleSyncInt64, PackI64, GetInt64Rule);
}


PyObject* Role::SeriI64_NewRef()
{
	SERI_ARRAY(Role::Int64Vector, GetInt64Array, PackI64);
}

GE::Int64 Role::GetI64( GE::Uint16 uIdx )
{
	return this->GetInt64Array().at(uIdx);
}

void Role::SetI64( GE::Uint16 uIdx, GE::Int64 val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetInt64Rule(uIdx);
	Int64Vector& IV = this->GetInt64Array();
	if (uIdx >= IV.size())
	{
	GE_EXC<<__FUNCTION__<<"uIdx("<<uIdx<<") >= IV.size("<<IV.size()<<")."<<GE_END;
	return;
	}
	if (IV.at(uIdx) == val) {return;}
	if (DR.bLogEvent)
	{
		// 经验金钱要特殊记录日志
		if (uIdx == RoleDataMgr::Instance()->uEXPIndex)
		{
			GE::Int64 jap = val - IV.at(uIdx);
			if (jap > 0)
			{
				this->m_uAccumulateIncExp += jap;
				if (this->m_uAccumulateIncExp > ACCUMULATE_EXP)
				{
					LogTransaction::Instance()->LogValue(this->GetRoleID(), DR.uCoding, IV.at(uIdx), val);
					this->m_uAccumulateIncExp = 0;
				}
			}
		}
		else if (uIdx == RoleDataMgr::Instance()->uMoneyIndex)
		{
			GE::Int64 jap = val - IV.at(uIdx);
			if (jap > 0)
			{
				this->m_uAccumulateIncMoney += jap;
				if (this->m_uAccumulateIncMoney > ACCUMULATE_MONEY)
				{
					LogTransaction::Instance()->LogValue(this->GetRoleID(), DR.uCoding, IV.at(uIdx), val);
					this->m_uAccumulateIncMoney = 0;
				}
			}
			else
			{
				this->m_uAccumulateDecMoney -= jap;
				if (this->m_uAccumulateDecMoney > ACCUMULATE_MONEY)
				{
					LogTransaction::Instance()->LogValue(this->GetRoleID(), DR.uCoding, IV.at(uIdx), val);
					this->m_uAccumulateDecMoney = 0;
				}
			}
		}
		else
		{
			LogTransaction::Instance()->LogValue(this->GetRoleID(), DR.uCoding, IV.at(uIdx), val);
		}
	}
	IV.at(uIdx) = val;
	if (DR.bSyncClient)
	{
		PackMessage PM;
		PM.PackMsg(DR.uCoding);
		PM.PackI64(val);
		this->SendMsg(PM.Msg());
	}
	if (NULL != DR.pyChangeFun)
	{
		PyObject* pyResult_NewRef = PyObject_CallFunctionObjArgs(DR.pyChangeFun, this->GetPySelf().GetObj_BorrowRef(), NULL);
		if (NULL == pyResult_NewRef)
		{
			PyErr_Print();
		}
		else
		{
			Py_DECREF(pyResult_NewRef);
		}
	}
}

void Role::IncI64( GE::Uint16 uIdx, GE::Int64 jap )
{
	CHECK_JAP;
	DO_INC(GE::Int64, GetInt64Rule, GetI64, SetI64);
}

void Role::DecI64( GE::Uint16 uIdx, GE::Int64 jap )
{
	CHECK_JAP;
	DO_DEC(GE::Int64, GetInt64Rule, GetI64, SetI64);
}

void Role::InitDI32( PyObject* arg_BorrowRef )
{
	if (Py_None == arg_BorrowRef)
	{
		return;
	}
	if (!PyTuple_CheckExact(arg_BorrowRef))
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") InitDI32 need tuple."<<GE_END;
		// 注意，这里不要保存数据
		this->Kick();
		return;
	}
	GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg_BorrowRef));
	Role::Int32Vector& IV = this->GetDisperseInt32Array();
	if (IV.size() < uSize)
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") InitDI32 size("<<IV.size()<<") < tuple size("<<uSize<<")."<<GE_END;
		// 注意，这里不要保存数据
		this->Kick();
		return;
	}
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncDisperseInt32);
	GE_ITER_UI16(uIdx, uSize)
	{
		GE::Int32 nValue = 0;
		if (!GEPython::PyObjToI32(PyTuple_GET_ITEM(arg_BorrowRef, uIdx), nValue))
		{
			GE_EXC<<"role("<<this->GetRoleID()<<") InitDI32 can't get int32 at index("<<uIdx<<")."<<GE_END;
			// 注意，这里不要保存数据
			this->Kick();
			return;
		}
		IV.at(uIdx) = nValue;
		if (RoleDataMgr::Instance()->GetDisperseInt32Rule(uIdx).bSyncClient && nValue != 0)
		{
			PM.PackUi16(uIdx);
			PM.PackI32(nValue);
		}
	}
	this->SendMsg(PM.Msg());
}


void Role::SyncDI32()
{
	Role::Int32Vector& IV = this->GetDisperseInt32Array();
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncDisperseInt32);
	GE_ITER_UI16(uIdx, IV.size())
	{
		GE::Int32 nValue = IV.at(uIdx);
		if (RoleDataMgr::Instance()->GetDisperseInt32Rule(uIdx).bSyncClient && nValue != 0)
		{
			PM.PackUi16(uIdx);
			PM.PackI32(nValue);
		}
	}
	this->SendMsg(PM.Msg());
}


PyObject* Role::SeriDI32_NewRef()
{
	Role::Int32Vector& IV = this->GetDisperseInt32Array();
	GE::Uint16 uSize = static_cast<GE::Uint16>(IV.size());
	GEPython::Tuple tuple(uSize);
	GE_ITER_UI16(uIdx, uSize)
	{
		tuple.AppendObj_NewRef(GEPython::PyObjFromI32(IV.at(uIdx)));
	}
	return tuple.GetTuple_NewRef();
}

GE::Int32 Role::GetDI32( GE::Uint16 uIdx )
{
	return this->GetDisperseInt32Array().at(uIdx);
}

GE::Int32& Role::GetDI32Ref( GE::Uint16 uIdx )
{
	return this->GetDisperseInt32Array().at(uIdx);
}

void Role::SetDI32( GE::Uint16 uIdx, GE::Int32 val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetDisperseInt32Rule(uIdx);
	Int32Vector& IV = this->GetDisperseInt32Array();
	DO_SET(PackI32);
}

void Role::IncDI32( GE::Uint16 uIdx, GE::Int32 jap )
{
	CHECK_JAP(jap);
	DO_INC(GE::Int32, GetDisperseInt32Rule, GetDI32, SetDI32);
}

void Role::DecDI32( GE::Uint16 uIdx, GE::Int32 jap )
{
	CHECK_JAP(jap);
	DO_DEC(GE::Int32, GetDisperseInt32Rule, GetDI32, SetDI32);
}

void Role::InitI32( PyObject* arg_BorrowRef )
{
	INIT_ARRAY(GE::Int32, Role::Int32Vector, GetInt32Array, enProcessMsg_RoleSyncInt32, PackI32, GetInt32Rule);
}

void Role::SyncI32()
{
	SYNC_ARRAY(GE::Int32, Role::Int32Vector, GetInt32Array, enProcessMsg_RoleSyncInt32, PackI32, GetInt32Rule);
}

PyObject* Role::SeriI32_NewRef()
{
	SERI_ARRAY(Role::Int32Vector, GetInt32Array, PackI32);
}

GE::Int32 Role::GetI32( GE::Uint16 uIdx )
{
	return this->GetInt32Array()[uIdx];
}

void Role::SetI32( GE::Uint16 uIdx, GE::Int32 val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetInt32Rule(uIdx);
	Int32Vector& IV = this->GetInt32Array();
	DO_SET(PackI32);
}

void Role::IncI32( GE::Uint16 uIdx, GE::Int32 jap )
{
	CHECK_JAP;
	DO_INC(GE::Int32, GetInt32Rule, GetI32, SetI32);
}

void Role::DecI32( GE::Uint16 uIdx, GE::Int32 jap )
{
	CHECK_JAP;
	DO_DEC(GE::Int32, GetInt32Rule, GetI32, SetI32);
}

void Role::SyncI32( GE::Uint16 uIdx, GE::Int32 val )
{
	const DataRule& DR = RoleDataMgr::Instance()->GetInt32Rule(uIdx);
	MsgSyncI32 msg;
	msg.Type(DR.uCoding);
	msg.i32 = val;
	this->SendMsg(&msg);
}

void Role::InitI16( PyObject* arg_BorrowRef )
{
	INIT_ARRAY(GE::Int16, Role::Int16Vector, GetInt16Array, enProcessMsg_RoleSyncInt16, PackI16, GetInt16Rule);
}

void Role::SyncI16( )
{
	SYNC_ARRAY(GE::Int16, Role::Int16Vector, GetInt16Array, enProcessMsg_RoleSyncInt16, PackI16, GetInt16Rule);
}

PyObject* Role::SeriI16_NewRef()
{
	SERI_ARRAY(Role::Int16Vector, GetInt16Array, PackI16);
}

GE::Int16 Role::GetI16( GE::Uint16 uIdx )
{
	return this->GetInt16Array().at(uIdx);
}

void Role::SetI16( GE::Uint16 uIdx, GE::Int16 val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetInt16Rule(uIdx);
	Int16Vector& IV = this->GetInt16Array();
	DO_SET(PackI16);
}

void Role::IncI16( GE::Uint16 uIdx, GE::Int16 jap )
{
	CHECK_JAP;
	DO_INC(GE::Int16, GetInt16Rule, GetI16, SetI16);
}

void Role::DecI16( GE::Uint16 uIdx, GE::Int16 jap )
{
	CHECK_JAP;
	DO_DEC(GE::Int16, GetInt16Rule, GetI16, SetI16);
}

void Role::InitI8( PyObject* arg_BorrowRef )
{
	INIT_ARRAY(GE::Int8, Role::Int8Vector, GetInt8Array, enProcessMsg_RoleSyncInt8, PackI8, GetInt8Rule);
}

void Role::SyncI8()
{
	SYNC_ARRAY(GE::Int8, Role::Int8Vector, GetInt8Array, enProcessMsg_RoleSyncInt8, PackI8, GetInt8Rule);
}

PyObject* Role::SeriI8_NewRef()
{
	SERI_ARRAY(Role::Int8Vector, GetInt8Array, PackI8);
}

GE::Int8 Role::GetI8( GE::Uint16 uIdx )
{
	return this->GetInt8Array().at(uIdx);
}

void Role::SetI8( GE::Uint16 uIdx, GE::Int8 val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetInt8Rule(uIdx);
	Int8Vector& IV = this->GetInt8Array();
	DO_SET(PackI8);
}

void Role::IncI8( GE::Uint16 uIdx, GE::Int8 jap )
{
	CHECK_JAP;
	DO_INC(GE::Int8, GetInt8Rule, GetI8, SetI8);
}

void Role::DecI8( GE::Uint16 uIdx, GE::Int8 jap )
{
	CHECK_JAP;
	DO_DEC(GE::Int8, GetInt8Rule, GetI8, SetI8);
}

void Role::InitDI8( PyObject* arg_BorrowRef )
{
	INIT_ARRAY(GE::Int8, Role::Int8Vector, GetDayInt8Array, enProcessMsg_RoleSyncDayInt8, PackI8, GetDayInt8Rule);
}

void Role::SyncDI8( )
{
	SYNC_ARRAY(GE::Int8, Role::Int8Vector, GetDayInt8Array, enProcessMsg_RoleSyncDayInt8, PackI8, GetDayInt8Rule);
}

PyObject* Role::SeriDI8_NewRef()
{
	SERI_ARRAY(Role::Int8Vector, GetDayInt8Array, PackI8);
}

GE::Int8 Role::GetDI8( GE::Uint16 uIdx )
{
	return this->GetDayInt8Array().at(uIdx);
}

void Role::SetDI8( GE::Uint16 uIdx, GE::Int8 val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetDayInt8Rule(uIdx);
	Int8Vector& IV = this->GetDayInt8Array();
	DO_SET(PackI8);
}

void Role::IncDI8( GE::Uint16 uIdx, GE::Int8 jap )
{
	CHECK_JAP;
	DO_INC(GE::Int8, GetDayInt8Rule, GetDI8, SetDI8);
}

void Role::DecDI8( GE::Uint16 uIdx, GE::Int8 jap )
{
	CHECK_JAP;
	DO_DEC(GE::Int8, GetDayInt8Rule, GetDI8, SetDI8);
}

void Role::InitI1( PyObject* arg_BorrowRef )
{
	if (Py_None == arg_BorrowRef)
	{
		return;
	}
	if (!PyString_CheckExact(arg_BorrowRef))
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") InitI1 need string."<<GE_END;
		// 注意，这里不要保存角色数据
		this->Kick();
		return;
	}
	void* pHead = PyString_AS_STRING(arg_BorrowRef);
	GE::Uint16 uSize = static_cast<GE::Uint16>((PyString_GET_SIZE(arg_BorrowRef)));
	GE::Uint8* pV = static_cast<GE::Uint8*>(pHead);
	Role::Int1Vector& IV = this->GetInt1Array();
	if (IV.size() < uSize * 8)
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") InitI1 size("<<IV.size()<<") < ("<<uSize<<") * 8."<<GE_END;
		// 注意，这里不要保存角色数据
		this->Kick();
		return;
	}
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncInt1);
	GE_ITER_UI16(uIdx, uSize)
	{
		GE::Uint8 uValue = (*pV);
		GE_ITER_UI16(uBit, 8)
		{
			GE::Uint16 uFlagIdx = uIdx * 8 + uBit;
			if (uValue & (1 << uBit))
			{
				IV.at(uFlagIdx) = true;
				if (RoleDataMgr::Instance()->GetInt1Rule(uFlagIdx).bSyncClient)
				{
					PM.PackUi16(uFlagIdx);
				}
			}
			else
			{
				IV.at(uFlagIdx) = false;
			}
		}
		pV += 1;
	}
	this->SendMsg(PM.Msg());
}

void Role::SyncI1()
{
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncInt1);
	Role::Int1Vector& IV = this->GetInt1Array();
	if (IV.size() % 8 != 0)
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") IV("<<IV.size()<<") % 8 != 0 in SyncI1."<<GE_END;
	}
	GE::Uint16 uSize = static_cast<GE::Uint16>(IV.size() / 8);
	GE_ITER_UI16(uIdx, uSize)
	{
		GE::Uint8 uValue = 0;
		GE_ITER_UI16(uBit, 8)
		{
			GE::Uint16 uFlagIdx = uIdx * 8 + uBit;
			if (IV.at(uFlagIdx) && RoleDataMgr::Instance()->GetInt1Rule(uFlagIdx).bSyncClient)
			{
				PM.PackUi16(uFlagIdx);
			}
		}
	}
	this->SendMsg(PM.Msg());
}


PyObject* Role::SeriI1_NewRef()
{
	PackMessage PM;
	PM.PackMsg(0);
	Role::Int1Vector& IV = this->GetInt1Array();
	if (IV.size() % 8 != 0)
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") IV("<<IV.size()<<") % 8 != 0 in SeriI1_NewRef."<<GE_END;
	}
	GE::Uint16 uSize = static_cast<GE::Uint16>(IV.size() / 8);
	GE_ITER_UI16(uIdx, uSize)
	{
		GE::Uint8 uValue = 0;
		GE_ITER_UI16(uBit, 8)
		{

			if (IV.at(uIdx * 8 + uBit))
			{
				uValue = uValue | (1 << uBit);
			}
		}
		PM.PackUi8(uValue);
	}
	return PyString_FromStringAndSize(static_cast<const char*>(PM.GetBodyHead()), PM.GetBodySize());
}

bool Role::GetI1( GE::Uint16 uIdx )
{
	return this->GetInt1Array()[uIdx];
}

void Role::SetI1( GE::Uint16 uIdx, bool val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetInt1Rule(uIdx);
	Int1Vector& IV = this->GetInt1Array();
	DO_SET(PackI8);
}

void Role::InitDI1( PyObject* arg_BorrowRef )
{
	if (Py_None == arg_BorrowRef)
	{
		return;
	}
	if (!PyString_CheckExact(arg_BorrowRef))
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") InitDI1 need string."<<GE_END;
		// 注意，这里不要保存角色数据
		this->Kick();
		return;
	}
	void* pHead = PyString_AS_STRING(arg_BorrowRef);
	GE::Uint16 uSize = static_cast<GE::Uint16>((PyString_GET_SIZE(arg_BorrowRef)));
	GE::Uint8* pV = static_cast<GE::Uint8*>(pHead);
	Role::Int1Vector& IV = this->GetDayInt1Array();
	if (IV.size() < uSize * 8)
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") InitDI1 size("<<IV.size()<<") < ("<<uSize<<") * 8."<<GE_END;
		// 注意，这里不要保存角色数据
		this->Kick();
		return;
	}
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncDayInt1);
	GE_ITER_UI16(uIdx, uSize)
	{
		GE::Uint8 uValue = (*pV);
		GE_ITER_UI16(uBit, 8)
		{
			GE::Uint16 uFlagIdx = uIdx * 8 + uBit;
			if (uValue & (1 << uBit))
			{
				IV.at(uFlagIdx) = true;
				if (RoleDataMgr::Instance()->GetDayInt1Rule(uFlagIdx).bSyncClient)
				{
					PM.PackUi16(uFlagIdx);
				}
			}
			else
			{
				IV.at(uFlagIdx) = false;
			}
		}
		pV += 1;
	}
	this->SendMsg(PM.Msg());
}

void Role::SyncDI1()
{
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncDayInt1);
	Role::Int1Vector& IV = this->GetDayInt1Array();
	if (IV.size() % 8 != 0)
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") size("<<IV.size()<<") % 8 != 0 in SyncDI1 ."<<GE_END;
	}
	GE::Uint16 uSize = static_cast<GE::Uint16>(IV.size() / 8);
	GE_ITER_UI16(uIdx, uSize)
	{
		GE::Uint8 uValue = 0;
		GE_ITER_UI16(uBit, 8)
		{
			GE::Uint16 uFlagIdx = uIdx * 8 + uBit;
			if (IV.at(uFlagIdx) && RoleDataMgr::Instance()->GetDayInt1Rule(uFlagIdx).bSyncClient)
			{
				PM.PackUi16(uFlagIdx);
			}
		}
	}
	this->SendMsg(PM.Msg());
}

PyObject* Role::SeriDI1_NewRef()
{
	PackMessage PM;
	PM.PackMsg(0);
	Role::Int1Vector& IV = this->GetDayInt1Array();
	if (IV.size() % 8 != 0)
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") size("<<IV.size()<<") % 8 != 0 in SeriDI1_NewRef ."<<GE_END;
	}
	GE::Uint16 uSize = static_cast<GE::Uint16>(IV.size() / 8);
	GE_ITER_UI16(uIdx, uSize)
	{
		GE::Uint8 uValue = 0;
		GE_ITER_UI16(uBit, 8)
		{
			if (IV.at(uIdx * 8 + uBit))
			{
				uValue = uValue | (1 << uBit);
			}
		}
		PM.PackUi8(uValue);
	}
	return PyString_FromStringAndSize(static_cast<const char*>(PM.GetBodyHead()), PM.GetBodySize());
}

bool Role::GetDI1( GE::Uint16 uIdx )
{
	return this->GetDayInt1Array()[uIdx];
}

void Role::SetDI1( GE::Uint16 uIdx, bool val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetDayInt1Rule(uIdx);
	Int1Vector& IV = this->GetDayInt1Array();
	DO_SET(PackI8);
}

void Role::InitDI64( PyObject* arg_BorrowRef )
{
	if (Py_None == arg_BorrowRef)
	{
		return;
	}
	if (!PyDict_CheckExact(arg_BorrowRef))
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") InitDI64 must be Dict."<<GE_END;
		GE_OUT<<PyObject_Str(arg_BorrowRef)<<GE_END;
		// 注意这里不要保存角色数据
		this->Kick();
		return;
	}
	Py_ssize_t pos = 0;
	PyObject* key = NULL;
	PyObject* value = NULL;
	GE::Uint16 uSize = static_cast<GE::Uint16>(PyDict_Size(arg_BorrowRef));
	GE::Uint16 uIdx = 0;
	GE::Int64 nValue = 0;
	Role::Int64Map& IM = this->GetDynamicInt64Array();
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncDynamicInt64);
	GE_ITER_UI16(idx, uSize)
	{
		int ret = PyDict_Next(arg_BorrowRef, &pos, &key, &value);
#if WIN	
		GE_ERROR(0 != ret);
#endif
		if (GEPython::PyObjToUI16(key, uIdx) && GEPython::PyObjToI64(value, nValue))
		{
			const DataRule& DR = RoleDataMgr::Instance()->GetDynamicInt64Rule(uIdx);
			if (GEDateTime::Instance()->Seconds() < DR.uOverTime)
			{
				IM[uIdx] = nValue;
				if (DR.bSyncClient)
				{
					PM.PackUi16(uIdx);
					PM.PackIntObj(nValue);
				}
			}
		}
		else
		{
			GE_EXC<<"role("<<this->GetRoleID()<<") InitDI64 Error."<<GE_END;
		}
	}
	this->SendMsg(PM.Msg());
}


void Role::SyncDI64()
{
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncDynamicInt64);

	Role::Int64Map::iterator iter = this->GetDynamicInt64Array().begin();
	for (; iter != this->GetDynamicInt64Array().end(); ++iter)
	{
		if (0 == iter->second)
		{
			continue;
		}
		const DataRule& DR = RoleDataMgr::Instance()->GetDynamicInt64Rule(iter->first);
		if (DR.bSyncClient)
		{
			PM.PackUi16(iter->first);
			PM.PackIntObj(iter->second);
		}
	}
	this->SendMsg(PM.Msg());
}


PyObject* Role::SeriDI64_NewRef()
{
	GEPython::Dict dict;
	Role::Int64Map::iterator iter = this->GetDynamicInt64Array().begin();
	for (; iter != this->GetDynamicInt64Array().end(); ++iter)
	{
		// 根据默认规则，如果值是0的话就没必要记录了
		if (0 == iter->second)
		{
			continue;
		}
		const DataRule& DR = RoleDataMgr::Instance()->GetDynamicInt64Rule(iter->first);
		// 过期了也没必要保持了
		if (GEDateTime::Instance()->Seconds() >= DR.uOverTime)
		{
			continue;
		}
		// 需要保持的
		PyObject* key_NewRef = GEPython::PyObjFromI32(iter->first);
		PyObject* value_NewRef = GEPython::PyObjFromI64(iter->second);
		dict.SetObj_NewRef(key_NewRef, value_NewRef);
	}
	return dict.GetDict_NewRef();
}

GE::Int64 Role::GetDI64( GE::Uint16 uIdx )
{
	Role::Int64Map::const_iterator iter = this->GetDynamicInt64Array().find(uIdx);
	if (iter == this->GetDynamicInt64Array().end())
	{
		return 0;
	}
	else
	{
		return iter->second;
	}
}

void Role::SetDI64( GE::Uint16 uIdx, GE::Int64 val )
{
	if (0 == val)
	{
		this->GetDynamicInt64Array().erase(uIdx);
	}
	else
	{
		this->GetDynamicInt64Array()[uIdx] = val;
	}
	const DataRule& DR = RoleDataMgr::Instance()->GetDynamicInt64Rule(uIdx);
	if (DR.bSyncClient)
	{
		PackMessage PM;
		PM.PackMsg(DR.uCoding);
		PM.PackIntObj(val);
		this->SendMsg(PM.Msg());
	}
	if (DR.bLogEvent)
	{
		;
	}
}

void Role::IncDI64( GE::Uint16 uIdx, GE::Int64 jap )
{
	CHECK_JAP;
	DO_INC(GE::Int64, GetDynamicInt64Rule, GetDI64, SetDI64);
}

void Role::DecDI64( GE::Uint16 uIdx, GE::Int64 jap )
{
	CHECK_JAP;
	DO_DEC(GE::Int64, GetDynamicInt64Rule, GetDI64, SetDI64);
}

void Role::InitObj( PyObject* arg_BorrowRef )
{
	if (Py_None == arg_BorrowRef)
	{
		return;
	}
	if (!PyTuple_CheckExact(arg_BorrowRef))
	{
		GE_EXC<<"role ("<<this->GetRoleID()<<") InitObj need tuple."<<GE_END;
		// 注意，这里不要保存角色数据
		this->Kick();
		return;
	}
	GE::Uint16 uMaxSize = static_cast<GE::Uint16>(this->GetObjArray().size());
	GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg_BorrowRef));
	if (uMaxSize < uSize)
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") IV("<<this->GetObjArray().size()<<") < ("<<uSize<<") in InitObj"<<GE_END;
		// 注意，这里不要保存角色数据
		this->Kick();
		return;
	}
	GE_ITER_UI16(uIdx, uSize)
	{
		this->SetObj(uIdx, PyTuple_GET_ITEM(arg_BorrowRef, uIdx));
	}
	// 默认是空字典
	for (GE::Uint16 uIdx = uSize; uIdx < uMaxSize; ++uIdx)
	{
		GEPython::Dict d;
		this->SetObj(uIdx, d.GetDict_BorrowRef());
	}
}

PyObject* Role::SeriObj_NewRef()
{
	GE::Uint16 uSize = static_cast<GE::Uint16>(this->GetObjArray().size());
	GEPython::Tuple tuple(uSize);
	GE_ITER_UI16(uIdx, uSize)
	{
		tuple.AppendObj_NewRef(this->GetObj_ReadOnly_NewRef(uIdx));
	}
	return tuple.GetTuple_NewRef();
}

PyObject* Role::GetObj_NewRef( GE::Uint16 uIdx )
{
	return this->GetObjArray().at(uIdx).GetObj_NewRef();
	this->IncObVersion(uIdx);
}

PyObject* Role::GetObj_ReadOnly_NewRef( GE::Uint16 uIdx )
{
	return this->GetObjArray().at(uIdx).GetObj_NewRef();
}

void Role::SetObj( GE::Uint16 uIdx, PyObject* arg_BorrowRef )
{
	this->GetObjArray().at(uIdx).SetObj_BorrowRef(arg_BorrowRef);
	this->IncObVersion(uIdx);
}

void Role::IncObVersion( GE::Uint16 uIdx )
{
	GE::Int32 nVersion = this->GetFlagArray().at(uIdx) + 1;
	this->GetFlagArray().at(uIdx) = nVersion;
	const DataRule& DR = RoleDataMgr::Instance()->GetFlagRule(uIdx);
	if (DR.bSyncClient)
	{
		PackMessage PM;
		PM.PackMsg(DR.uCoding);
		PM.PackI32(nVersion);
		this->SendMsg(PM.Msg());
	}
}

GE::Int32 Role::GetObjVersion( GE::Uint16 uIdx )
{
	return this->GetFlagArray().at(uIdx);
}

void Role::InitCI8( PyObject* arg_BorrowRef )
{
	INIT_ARRAY_NOT_RULE(GE::Int8, Role::Int8Vector, GetClientInt8Array, enProcessMsg_RoleSyncClientInt8, PackI8);
}

void Role::SyncCI8()
{
	PackMessage PM;	
	PM.PackMsg(enProcessMsg_RoleSyncClientInt8);
	Role::Int8Vector& IV = this->GetClientInt8Array();
	GE_ITER_UI16(uIdx, static_cast<GE::Uint16>(IV.size()))
	{	
		GE::Int8 i8 = IV.at(uIdx);
		if (i8 != 0)
		{
			PM.PackI16(uIdx);
			PM.PackI8(i8);
		}
		
	}
	this->SendMsg(PM.Msg());
}

PyObject* Role::SeriCI8_NewRef()
{
	SERI_ARRAY(Role::Int8Vector, GetClientInt8Array, PackI8);
}

GE::Int8 Role::GetCI8( GE::Uint16 uIdx )
{
	return this->GetClientInt8Array()[uIdx];
}

void Role::SetCI8( GE::Uint16 uIdx, GE::Int8 val )
{
	this->GetClientInt8Array()[uIdx] = val;
}

void Role::SyncTI64()
{
	Int64Vector& IV = this->GetTempInt64Array();
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncTempInt64);
	GE_ITER_UI16(uIdx, IV.size())
	{
		GE::Int64 nValue = IV[uIdx];
		if (RoleDataMgr::Instance()->GetTempInt64Rule(uIdx).bSyncClient && nValue != 0)
		{
			PM.PackI16(uIdx);
			PM.PackIntObj(nValue);
		}
	}
	this->SendMsg(PM.Msg());
}




GE::Int64 Role::GetTI64( GE::Uint16 uIdx )
{
	return this->GetTempInt64Array()[uIdx];
}

void Role::SetTI64( GE::Uint16 uIdx, GE::Int64 val )
{
	CHECK_KICK;
	const DataRule& DR = RoleDataMgr::Instance()->GetTempInt64Rule(uIdx);
	Int64Vector& IV = this->GetTempInt64Array();
	DO_SET(PackIntObj);
}

void Role::IncTI64( GE::Uint16 uIdx, GE::Int64 jap )
{
	CHECK_JAP;
	DO_INC(GE::Int64, GetTempInt64Rule, GetTI64, SetTI64);
}

void Role::DecTI64( GE::Uint16 uIdx, GE::Int64 jap )
{
	CHECK_JAP;
	DO_DEC(GE::Int64, GetTempInt64Rule, GetTI64, SetTI64);
}

void Role::InitCD( PyObject* arg_BorrowRef )
{
	if (Py_None == arg_BorrowRef)
	{
		return;
	}
	if (!PyDict_CheckExact(arg_BorrowRef))
	{
		GE_EXC<<"role("<<this->GetRoleID()<<") InitCD must be Dict."<<GE_END;
		GE_OUT<<PyObject_Str(arg_BorrowRef)<<GE_END;
		// 注意这里不要保存角色数据
		this->Kick();
		return;
	}
	Py_ssize_t pos = 0;
	PyObject* key = NULL;
	PyObject* value = NULL;
	GE::Uint16 uSize = static_cast<GE::Uint16>(PyDict_Size(arg_BorrowRef));
	GE::Uint16 uIdx = 0;
	GE::Int32 nValue = 0;
	Role::Int32Map& IM = this->GetCDArray();
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncCD);
	GE::Int32 nNow = static_cast<GE::Int32>(GEDateTime::Instance()->Seconds());
	GE_ITER_UI16(idx, uSize)
	{
		int ret = PyDict_Next(arg_BorrowRef, &pos, &key, &value);
#if WIN	
		GE_ERROR(0 != ret);
#endif
		if (GEPython::PyObjToUI16(key, uIdx) && GEPython::PyObjToI32(value, nValue))
		{
			if (nNow < nValue)
			{
				IM[uIdx] = nValue;
				if (RoleDataMgr::Instance()->GetCDRule(uIdx).bSyncClient)
				{
					PM.PackUi16(uIdx);
					PM.PackI32(nValue);
				}
			}
		}
		else
		{
			GE_EXC<<"role("<<this->GetRoleID()<<") InitCD Error."<<GE_END;
		}
	}
	this->SendMsg(PM.Msg());
}

void Role::SyncCD()
{
	PackMessage PM;
	PM.PackMsg(enProcessMsg_RoleSyncCD);
	GE::Int32 nNow = static_cast<GE::Int32>(GEDateTime::Instance()->Seconds());
	Role::Int32Map::iterator iter = this->GetCDArray().begin();
	for (; iter != this->GetCDArray().end(); ++iter)
	{
		if (nNow >= iter->second)
		{
			continue;
		}
		if (RoleDataMgr::Instance()->GetCDRule(iter->first).bSyncClient)
		{
			PM.PackUi16(iter->first);
			PM.PackI32(iter->second);
		}
	}
	this->SendMsg(PM.Msg());
}

PyObject* Role::SeriCD_NewRef()
{
	GEPython::Dict dict;
	Role::Int32Map::iterator iter = this->GetCDArray().begin();
	GE::Int32 nNow = static_cast<GE::Int32>(GEDateTime::Instance()->Seconds());
	for (; iter != this->GetCDArray().end(); ++iter)
	{
		// 如果过期了没必要记录
		if (nNow >= iter->second)
		{
			continue;
		}
		PyObject* key_NewRef = GEPython::PyObjFromI32(iter->first);
		PyObject* value_NewRef = GEPython::PyObjFromI32(iter->second);
		dict.SetObj_NewRef(key_NewRef, value_NewRef);
	}
	return dict.GetDict_NewRef();
}

GE::Int32 Role::GetCD( GE::Uint16 uIdx )
{
	Role::Int32Map::const_iterator iter = this->GetCDArray().find(uIdx);
	if (iter == this->GetCDArray().end())
	{
		return 0;
	}
	else
	{	
		// 如果过期了，返回0
		GE::Int32 nNow = static_cast<GE::Int32>(GEDateTime::Instance()->Seconds());
		if (nNow >= iter->second)
		{
			return 0;
		}
		else
		{
			return iter->second - nNow;
		}
	}
}

void Role::SetCD( GE::Uint16 uIdx, GE::Int32 val )
{
	if(val <= 0)
	{
		val = - static_cast<GE::Int32>(GEDateTime::Instance()->Seconds());
	}
	GE::Int32 nOverTime = static_cast<GE::Int32>(GEDateTime::Instance()->Seconds()) + val;
	GE::Int32 nOld = this->GetCD(uIdx);
	this->GetCDArray()[uIdx] = nOverTime;
	const DataRule& DR = RoleDataMgr::Instance()->GetCDRule(uIdx);
	if (DR.bSyncClient)
	{
		PackMessage PM;
		PM.PackMsg(DR.uCoding);
		PM.PackI32(nOverTime);
		this->SendMsg(PM.Msg());
	}
	if (NULL != DR.pyChangeFun)	
	{	
		GEPython::Object oldValue = GEPython::PyObjFromI64(nOld);
		GEPython::Object newValue = GEPython::PyObjFromI64(this->GetCD(uIdx));
		PyObject* pyResult_NewRef = PyObject_CallFunctionObjArgs(DR.pyChangeFun, this->GetPySelf().GetObj_BorrowRef(), oldValue.GetObj_BorrowRef(), newValue.GetObj_BorrowRef(), NULL);
		if (NULL == pyResult_NewRef)	
		{
			PyErr_Print();
		}
		else
		{
			Py_DECREF(pyResult_NewRef);
		}
	}
}

void Role::SetTempObj( GE::Uint16 uIdx, PyObject* obj_BorrowRef )
{
	this->GetTempObjArray().at(uIdx).SetObj_BorrowRef(obj_BorrowRef);
}

PyObject* Role::GetTempObj_NewRef( GE::Uint16 uIdx )
{
	return this->GetTempObjArray().at(uIdx).GetObj_NewRef();
}


void Role::SetCareer(GE::Int32 uCareer)
{
	this->SetDI32(RoleDataMgr::Instance()->uCareerIndex, uCareer);
}

GE::Int32 Role::GetCareer()
{
	return this->GetDI32(RoleDataMgr::Instance()->uCareerIndex);
}

void Role::CheckRecountProperty()
{
	if (this->m_bNeedRecount == false)
	{
		return;
	}
	RoleMgr::Instance()->RecountProperty(this);
}

void Role::SetFly( GE::Uint8 uCode )
{
	if(this->GetPosZ() == uCode)
	{
		return;
	}
	this->SetPosZ(uCode);
	this->SyncFlyState();
}

void Role::SyncFlyState()
{
	MsgRoleFlyState msg;
	msg.uFlyState = this->GetPosZ();
	this->SendMsg(&msg);
}



GE::Int16 Role::GetTiLi()
{
	return this->GetI16(RoleDataMgr::Instance()->uTiLiIndex);
}

void Role::SetTiLi( GE::Uint16 uValue )
{
	this->SetI16(RoleDataMgr::Instance()->uTiLiIndex, uValue);
}

void Role::IncTiLi( GE::Uint16 uValue )
{
	if (this->GetTiLi() + uValue > 9999)
	{
		//体力最多9999
		return;
	}
	this->IncI16(RoleDataMgr::Instance()->uTiLiIndex, uValue);
}

void Role::DecTiLi( GE::Uint16 uValue )
{
	this->DecI16(RoleDataMgr::Instance()->uTiLiIndex, uValue);
}

void Role::ClearMessage( )
{
	this->m_SendMessageMap.clear();
	this->m_RecvMessageMap.clear();
}

void Role::SendOneMessage( GE::Uint16 uMsgType )
{
	if (!RoleMgr::Instance()->IsStatistics())
	{
		return;
	}
	MessageMap::iterator iter = this->m_SendMessageMap.find(uMsgType);
	if (iter == this->m_SendMessageMap.end())
	{
		this->m_SendMessageMap.insert(std::make_pair(uMsgType, 1));
	}
	else
	{
		++(iter->second);
	}
}

void Role::RecvOneMessage( GE::Uint16 uMsgType )
{
	if (!RoleMgr::Instance()->IsStatistics())
	{
		return;
	}
	MessageMap::iterator iter = this->m_RecvMessageMap.find(uMsgType);
	if (iter == this->m_RecvMessageMap.end())
	{
		this->m_RecvMessageMap.insert(std::make_pair(uMsgType, 1));
	}
	else
	{
		++(iter->second);
	}
}


GE::Int16 Role::GetTempFly()
{
	return static_cast<GE::Uint16>(this->GetTI64(RoleDataMgr::Instance()->uTempFlyStateIndex));
}

void Role::SetTempFly( GE::Uint16 uValue )
{
	this->SetTI64(RoleDataMgr::Instance()->uTempFlyStateIndex, uValue);
}


GE::Int16 Role::GetNowSpeed()
{
	if (this->GetTempSpeed() > 0)
	{
		return this->GetTempSpeed();
	}
	else if (this->GetMountSpeed() > 0)
	{
		return this->GetMountSpeed();
	}
	else
	{
		return this->GetMoveSpeed();
	}
}

GE::Int16 Role::GetTempSpeed()
{
	return static_cast<GE::Uint16>(this->GetTI64(RoleDataMgr::Instance()->uTempSpeedIndex));
}

void Role::SetTempSpeed( GE::Uint16 uValue )
{
	this->SetTI64(RoleDataMgr::Instance()->uTempSpeedIndex, uValue);
}

GE::Int16 Role::GetMountSpeed()
{
	return static_cast<GE::Uint16>(this->GetTI64(RoleDataMgr::Instance()->uMountSpeedIndex));
}

void Role::SetMountSpeed( GE::Uint16 uValue )
{
	this->SetTI64(RoleDataMgr::Instance()->uMountSpeedIndex, uValue);
}

GE::Int16 Role::GetMoveSpeed()
{
	return static_cast<GE::Uint16>(this->GetTI64(RoleDataMgr::Instance()->uMoveSpeedIndex));
}

void Role::SetMoveSpeed( GE::Uint16 uValue )
{
	this->SetTI64(RoleDataMgr::Instance()->uMoveSpeedIndex, uValue);
}

bool Role::IsIgnoreCheckMovingTime(GE::Uint32 uTimeJap)
{
	if (uTimeJap == 0)
	{
		return false;
	}
	GE::Uint32 uNowTime = GEDateTime::Instance()->Seconds();
	if (uNowTime - this->GetMovingTime() >= uTimeJap)
	{
		//超出距离，不能忽视，进入移动逻辑
		this->UpdateMovingTime(uNowTime);
		return false;
	}
	else
	{
		//忽视这次移动
		return true;
	}

}

GE::Uint32 Role::GetLastSceneID()
{
	return this->GetI32(RoleDataMgr::Instance()->uLastSceneIDIndex);
}

void Role::SetLastSceneID( GE::Uint32 uSceneID )
{
	 this->SetI32(RoleDataMgr::Instance()->uLastSceneIDIndex, uSceneID);
}

GE::Uint16 Role::GetLastPosX()
{
	return this->GetI16(RoleDataMgr::Instance()->uLastPosXIndex);
}

GE::Uint16 Role::GetLastPosY()
{
	return this->GetI16(RoleDataMgr::Instance()->uLastPosYIndex);
}

void Role::SetLastPosX( GE::Uint16 uPosX )
{
	 return this->SetI16(RoleDataMgr::Instance()->uLastPosXIndex, uPosX);
}

void Role::SetLastPosY( GE::Uint16 uPosY )
{
	return this->SetI16(RoleDataMgr::Instance()->uLastPosYIndex, uPosY);
}

bool Role::IsFlyingPos()
{
	if (this->GetScene() == NULL)
	{
		return true;
	}
	return this->GetScene()->IsFlyingPos(this);
}

bool Role::IsFlying()
{
	if (this->GetTempFly() == 2)
	{
		//锁定飞行
		return false;
	}
	else if (this->GetTempFly() == 1)
	{
		//临时飞行
		return true;
	}
	//没有设置临时飞行，取正常数据
	return GetPosZ() != 0;
}






