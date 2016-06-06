/************************************************************************
角色数据（可自动同步客户端）
************************************************************************/
#pragma once
#include <string>
#include <vector>
#include <boost/unordered_map.hpp>
#include "../GameEngine/GameEngine.h"
#include "RoleDataMgr.h"

class RoleData
{
	GE_DISABLE_BOJ_CPY(RoleData);
public:
	typedef std::vector<GE::Int64>						Int64Vector;
	typedef std::vector<GE::Int32>						Int32Vector;
	typedef std::vector<GE::Int16>						Int16Vector;
	typedef std::vector<GE::Int8>						Int8Vector;
	typedef std::vector<bool>							Int1Vector;
	typedef boost::unordered_map<GE::Uint16, GE::Int64>	Int64Map;
	typedef boost::unordered_map<GE::Uint16, GE::Int32> Int32Map;
	typedef std::vector<GEPython::Object>				ObjVector;
	/*
	注意，这里作为基类但是析构函数非虚，因为析构函数必定是个空函数。
	*/
	RoleData(GE::Uint64 uRoleID, const std::string& sRoleName, const std::string& sOpenID, GE::Uint32 uCommandSize, GE::Uint32 uCommandIndex);
	~RoleData() {};

public:
	bool							DoCommand(GE::Uint32 uIndex);
	GE::Uint32						GetCommandIndex() {return this->m_uCommandIndex;}
	GE::Uint32						GetCommandSize() {return this->m_uCommandSize;}

public:
	Int64Vector&					GetInt64Array() {return m_Int64Array;}
	Int32Vector&					GetDisperseInt32Array() {return m_DisperseInt32Array;}
	Int32Vector&					GetInt32Array() {return m_Int32Array;}
	Int16Vector&					GetInt16Array() {return m_Int16Array;}
	Int8Vector&						GetInt8Array() {return m_Int8Array;}
	Int8Vector&						GetDayInt8Array() {return m_DayInt8Array;}
	Int8Vector&						GetClientInt8Array() {return m_ClientInt8Array;}
	Int1Vector&						GetInt1Array() {return m_Int1Array;}
	Int1Vector&						GetDayInt1Array() {return m_DayInt1Array;}
	Int64Map&						GetDynamicInt64Array() {return m_DynamicInt64Map;}
	ObjVector&						GetObjArray() {return m_ObjArray;}
	Int32Vector&					GetFlagArray() {return m_FlagArray;}
	Int32Map&						GetCDArray() {return m_CDMap;}
	Int64Vector&					GetTempInt64Array() {return m_TempInt64Array;}
	ObjVector&						GetTempObjArray() {return m_TempObjArray;}

private:
	// 角色数组
	Int64Vector						m_Int64Array;
	Int32Vector						m_DisperseInt32Array;
	Int32Vector						m_Int32Array;
	Int16Vector						m_Int16Array;
	Int8Vector						m_Int8Array;
	Int8Vector						m_DayInt8Array;
	Int8Vector						m_ClientInt8Array;
	Int1Vector						m_Int1Array;
	Int1Vector						m_DayInt1Array;
	Int64Map						m_DynamicInt64Map;
	ObjVector						m_ObjArray;
	Int32Vector						m_FlagArray;
	Int32Map						m_CDMap;
	Int64Vector						m_TempInt64Array;
	Int32Map						m_ItemMap;
	ObjVector						m_TempObjArray;

public:
	GE::Uint64						GetRoleID() {return m_uRoleID;}
	std::string&					GetRoleName() {return m_sRoleName;}
	void							SetRoleName(const std::string& sRoleName) { m_sRoleName = sRoleName;}
	const std::string&				GetOpenID() {return m_sOpenID;}

private:
	// 角色其他数据
	GE::Uint64						m_uRoleID;				//角色ID
	std::string						m_sRoleName;			//角色名
	std::string						m_sOpenID;				//角色帐号
	GE::Uint32						m_uCommandSize;			//角色命令总条数
	GE::Uint32						m_uCommandIndex;		//角色命令最后执行位置
};

