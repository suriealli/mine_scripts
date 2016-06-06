/*我是UTF8无签名编码 */
#include "RoleData.h"
#include "RoleDataMgr.h"

RoleData::RoleData( GE::Uint64 uRoleID, const std::string& sRoleName, const std::string& sOpenID, GE::Uint32 uCommandSize, GE::Uint32 uCommandIndex)
	: m_uRoleID(uRoleID)
	, m_sRoleName(sRoleName)
	, m_sOpenID(sOpenID)
	, m_uCommandSize(uCommandSize)
	, m_uCommandIndex(uCommandIndex)
	, m_Int64Array(RoleDataMgr::Instance()->GetInt64Size(), 0)
	, m_DisperseInt32Array(RoleDataMgr::Instance()->GetDisperseInt32Size(), 0)
	, m_Int32Array(RoleDataMgr::Instance()->GetInt32Size(), 0)
	, m_Int16Array(RoleDataMgr::Instance()->GetInt16Size(), 0)
	, m_Int8Array(RoleDataMgr::Instance()->GetInt8Size(), 0)
	, m_DayInt8Array(RoleDataMgr::Instance()->GetDayInt8Size(), 0)
	, m_ClientInt8Array(RoleDataMgr::Instance()->GetClientInt8Size(), 0)
	, m_Int1Array(RoleDataMgr::Instance()->GetInt1Size(), false)
	, m_DayInt1Array(RoleDataMgr::Instance()->GetDayInt1Size(), false)
	, m_ObjArray(RoleDataMgr::Instance()->GetFlagSize())
	, m_FlagArray(RoleDataMgr::Instance()->GetFlagSize(), 0)
	, m_TempInt64Array(RoleDataMgr::Instance()->GetTempInt64Size(), 0)
	, m_TempObjArray(RoleDataMgr::Instance()->GetTempObjSize())
{
}

bool RoleData::DoCommand( GE::Uint32 uIndex )
{
	if (uIndex == this->m_uCommandIndex + 1)
	{
		this->m_uCommandIndex = uIndex;
		return true;
	}
	else
	{
		GE_EXC<<"DoCommand("<<uIndex<<") but index("<<m_uCommandIndex<<")."<<GE_END;
		return false;
	}
}

