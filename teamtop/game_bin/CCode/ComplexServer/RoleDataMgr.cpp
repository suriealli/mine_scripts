/*角色数据*/
#include "RoleDataMgr.h"

DataRule::DataRule()
	: bSyncClient(false)
	, bLogEvent(false)
	, nMinValue(0)
	, nMaxValue(0)
	, nMinAction(DoNothing)
	, nMaxAction(DoNothing)
	, uOverTime(MAX_UINT32)
	, pyChangeFun(NULL)
{
}

DataRule::~DataRule()
{
	if (NULL != pyChangeFun)
	{
		Py_DECREF(pyChangeFun); pyChangeFun = NULL;
	}
}

void DataRule::SetChangeFun( PyObject* pyobj_BorrowRef )
{
	if (NULL == pyChangeFun)
	{
		pyChangeFun = pyobj_BorrowRef;
		Py_INCREF(pyChangeFun);
	}
	else
	{
		GE_EXC<<"coding("<<uCoding<<") repeat set change fun."<<GE_END;
		Py_DECREF(pyChangeFun);
		pyChangeFun = pyobj_BorrowRef;
		Py_INCREF(pyChangeFun);
	}
}

RoleDataMgr::RoleDataMgr()
	: m_uMaxInt64Index(0)
	, m_uMaxDisperseInt32Index(0)
	, m_uMaxInt32Index(0)
	, m_uMaxInt16Index(0)
	, m_uMaxInt8Index(0)
	, m_uMaxDayInt8Index(0)
	, m_uMaxClientInt8Size(0)
	, m_uMaxInt1Index(0)
	, m_uMaxDayInt1Index(0)
	, m_uMaxFlagIndex(0)
	, m_uMaxTempInt64Index(0)
	, m_uMaxDynamicInt64Size(0)
	, m_uMaxCDSize(0)
	, m_uMaxTempObjSize(0)

{
	this->InitRule("RoleInt64Range", this->m_Int64Rules);
	this->InitRule("RoleDisperseInt32Range", this->m_DisperseInt32Rules);
	this->InitRule("RoleInt32Range", this->m_Int32Rules);
	this->InitRule("RoleInt16Range", this->m_Int16Rules);
	this->InitRule("RoleInt8Range", this->m_Int8Rules);
	this->InitRule("RoleDayInt8Range", this->m_DayInt8Rules);
	this->InitRule("RoleInt1Range", this->m_Int1Rules);
	this->InitRule("RoleDayInt1Range", this->m_DayInt1Rules);
	this->InitRule("RoleDynamicInt64Range", this->m_DynamicInt64Rules);
	this->InitRule("RoleObjFlagRange", this->m_FlagRules);
	this->InitRule("RoleCDRange", this->m_CDRules);
	this->InitRule("RoleTempInt64Range", this->m_TempInt64Rules);

	this->m_uMaxClientInt8Size = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.Enum", "MaxClientInt8Size"));
	this->m_uMaxDynamicInt64Size = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.Enum", "MaxDynamicInt64Size"));
	this->m_uMaxCDSize = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.Enum", "MaxCDSize"));
	this->m_uMaxTempObjSize = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.Enum", "MaxTempObjSize"));
	
	this->uLastSaveUnixTimeIndex = MAX_UINT16;
	this->uOnlineTimesIndex = MAX_UINT16;
	this->uLastClearDaysIndex = MAX_UINT16;
	this->uOnlineTimesTodayIndex = MAX_UINT16;
	this->uLoginOnlineTimeIndex = MAX_UINT16;
	this->uMaxLoginDaysIndex = MAX_UINT16;
	this->uContinueLoginDaysIndex = MAX_UINT16;
	this->uMaxContinueLoginDaysIndex = MAX_UINT16;
	this->uWPEIndex = MAX_UINT16;
	this->uTiLiIndex = MAX_UINT16;
	this->uTiLiMinuteIndex = MAX_UINT16;
	this->uMoveSpeedIndex = MAX_UINT16;
	this->uTempSpeedIndex = MAX_UINT16;
	this->uMountSpeedIndex = MAX_UINT16;
	this->uTempFlyStateIndex = MAX_UINT16;

	this->uCanChatTimeIndex = MAX_UINT16;
	this->uWorldChatIndex = MAX_UINT16;
	this->uFightStatusIndex = MAX_UINT16;
	this->uEXPIndex = MAX_UINT16;
	this->uMoneyIndex = MAX_UINT16;
	
	this->uLastPosXIndex = MAX_UINT16;
	this->uLastPosYIndex = MAX_UINT16;
	this->uLastSceneIDIndex = MAX_UINT16;

	this->uRoleAppStatusIndex = MAX_UINT16;

	this->uEnumAppStatus = MAX_UINT16;
	this->uEnumAppVersion1 = MAX_UINT16;
	this->uEnumAppVersion2 = MAX_UINT16;

	this->uHuangZuanIndex = MAX_UINT16;
	this->uLanZuanIndex = MAX_UINT16;

	this->uCareerIndex = MAX_UINT16;

}

RoleDataMgr::~RoleDataMgr()
{

}

void RoleDataMgr::InitRule( const char* sAttrName, RuleVector& RV )
{
	GE::Uint16 imin = 0;
	GE::Uint16 imax = 0;
	GEPython::Object ran = GEPython::GetModuleAttr("Common.Coding", sAttrName);
	if (!PyArg_ParseTuple(ran.GetObj_BorrowRef(), "HH", &imin, &imax))
	{
		GE_EXC<<"Get Rule Range Error. Attr("<<sAttrName<<").";
		return;
	}
	GE_ERROR(imax > imin);
	RV.resize(imax - imin);
	GE_ITER_UI16(idx, static_cast<GE::Uint16>(RV.size()))
	{
		RV.at(idx).uCoding = imin + idx;
	}
}

void RoleDataMgr::SetInt64Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_Int64Rules.at(uIdx) = DR;
	this->m_uMaxInt64Index = GE_MAX(m_uMaxInt64Index, uIdx);
}

void RoleDataMgr::SetDisperseInt32Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_DisperseInt32Rules.at(uIdx) = DR;
	this->m_uMaxDisperseInt32Index = GE_MAX(m_uMaxDisperseInt32Index, uIdx);
}

void RoleDataMgr::SetInt32Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_Int32Rules.at(uIdx) = DR;
	this->m_uMaxInt32Index = GE_MAX(m_uMaxInt32Index, uIdx);
}

void RoleDataMgr::SetInt16Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_Int16Rules.at(uIdx) = DR;
	this->m_uMaxInt16Index = GE_MAX(m_uMaxInt16Index, uIdx);
}

void RoleDataMgr::SetInt8Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_Int8Rules.at(uIdx) = DR;
	this->m_uMaxInt8Index = GE_MAX(m_uMaxInt8Index, uIdx);
}

void RoleDataMgr::SetDayInt8Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_DayInt8Rules.at(uIdx) = DR;
	this->m_uMaxDayInt8Index = GE_MAX(m_uMaxDayInt8Index, uIdx);
}

void RoleDataMgr::SetInt1Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_Int1Rules.at(uIdx) = DR;
	this->m_uMaxInt1Index = GE_MAX(m_uMaxInt1Index, uIdx);
}

void RoleDataMgr::SetDayInt1Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_DayInt1Rules.at(uIdx) = DR;
	this->m_uMaxDayInt1Index = GE_MAX(m_uMaxDayInt1Index, uIdx);
}

void RoleDataMgr::SetDynamicInt64Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_DynamicInt64Rules.at(uIdx) = DR;
}

void RoleDataMgr::SetFlagRule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_FlagRules.at(uIdx) = DR;
	this->m_uMaxFlagIndex = GE_MAX(m_uMaxFlagIndex, uIdx);
}

void RoleDataMgr::SetCDRule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_CDRules.at(uIdx) = DR;
}

void RoleDataMgr::SetTempInt64Rule( const GE::Uint16 uIdx, DataRule& DR )
{
	this->m_TempInt64Rules.at(uIdx) = DR;
	this->m_uMaxTempInt64Index = GE_MAX(m_uMaxTempInt64Index, uIdx);
}

void RoleDataMgr::LoadPyData()
{
	this->uLastSaveProcessIDIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumDisperseInt32", "LastSaveProcessID"));
	this->uLastSaveUnixTimeIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumDisperseInt32", "LastSaveUnixTime"));
	this->uOnlineTimesIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumDisperseInt32", "enOnlineTimes"));
	this->uLastClearDaysIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumDisperseInt32", "enLastClearDays"));
	this->uOnlineTimesTodayIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt32", "enOnlineTimesToday"));
	this->uLoginOnlineTimeIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumTempInt64", "LoginOnlineTime"));
	this->uMaxLoginDaysIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt16", "enMaxLoginDays"));
	this->uContinueLoginDaysIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt16", "enContinueLoginDays"));
	this->uMaxContinueLoginDaysIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt16", "enMaxContinueLoginDays"));
	this->uWPEIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumTempInt64", "enWPE"));
	this->uTiLiIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt16", "TiLi"));
	this->uTiLiMinuteIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt32", "TiLiMinute"));
	this->uMoveSpeedIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumTempInt64", "MoveSpeed"));
	this->uTempSpeedIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumTempInt64", "TempSpeed"));
	this->uMountSpeedIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumTempInt64", "MountSpeed"));
	this->uTempFlyStateIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumTempInt64", "TempFlyState"));
	this->uCanChatTimeIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumDisperseInt32", "CanChatTime"));
	this->uWorldChatIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt32", "WorldChatCD"));
	this->uFightStatusIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt1", "ST_FightStatus"));
	this->uEXPIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt64", "En_Exp"));
	this->uMoneyIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt64", "enMoney"));
	this->uLastPosXIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt16", "enLastPosX"));
	this->uLastPosYIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt16", "enLastPosY"));
	this->uLastSceneIDIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumInt32", "enLastPublicSceneID"));
	this->uRoleAppStatusIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumTempInt64", "RoleAppStatus"));
	this->uEnumAppStatus = static_cast<GE::Uint16>(GEPython::GetModuleLong("Common.Other.EnumAppearance", "App_Status"));
	this->uEnumAppVersion1 = static_cast<GE::Uint16>(GEPython::GetModuleLong("Common.Other.EnumAppearance", "App_Version"));
	this->uEnumAppVersion2 = static_cast<GE::Uint16>(GEPython::GetModuleLong("Common.Other.EnumAppearance", "App_StatusVersion"));

	this->uHuangZuanIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumDisperseInt32", "HuangZuan_Y_H_L"));
	this->uLanZuanIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumDisperseInt32", "LanZuan_Y_H_L"));

	this->uCareerIndex = static_cast<GE::Uint16>(GEPython::GetModuleLong("Game.Role.Data.EnumDisperseInt32", "enCareer"));
}

