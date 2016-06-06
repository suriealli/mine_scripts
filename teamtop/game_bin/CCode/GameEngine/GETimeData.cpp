/*我是UTF8无签名编码 */
#include "GETimeData.h"
#include "GEDateTime.h"
#include "PyTimeData.h"

GETimeData::GETimeData()
	: m_uLowerID(0)
{
	// 创建对应的Python对象
	this->m_pySelf.SetObj_NewRef((PyObject*)GEPython::PyTimeData_New(this));
}

GETimeData::~GETimeData()
{
	// 将Python的cptr指针设置为NULL
	GEPython::PyTimeData_Del(m_pySelf.GetObj_BorrowRef());
	// 释放还为触发的TimeData
	TimeDataMap::iterator _iter = this->m_TimeDataMap.begin();
	while(_iter != this->m_TimeDataMap.end())
	{
		Py_DECREF(_iter->second);
		++_iter;
	}
	this->m_TimeDataMap.clear();
}

GE::Uint64 GETimeData::HoldData( GE::Uint32 uTimeSec, PyObject* pyData_BorrowRef )
{
	// 累加ID的低32位
	++m_uLowerID;
	// 计算超时时间
	GE::Uint32 uTouchTime = GEDateTime::Instance()->Seconds() + uTimeSec;
	// 构建ID，超时时间为高32位，低32位为累进计数，使得存储到Map中是按时间排序的
	GE::B8 uID(m_uLowerID, uTouchTime);
	Py_INCREF(pyData_BorrowRef);
	this->m_TimeDataMap.insert(std::make_pair(uID.UI64(), pyData_BorrowRef));
	return uID.UI64();
}

void GETimeData::RemoveData( GE::Uint64 uID )
{
	TimeDataMap::iterator _iter = this->m_TimeDataMap.find(uID);
	if (_iter == this->m_TimeDataMap.end())
	{
		return;
	}
	Py_DECREF(_iter->second);
	this->m_TimeDataMap.erase(_iter);
}

PyObject* GETimeData::FindData_NewRef( GE::Uint64 uID )
{
	PyObject* p = this->FindData_BorrowRef(uID);
	Py_INCREF(p);
	return p;
}

PyObject* GETimeData::FindData_BorrowRef( GE::Uint64 uID )
{
	TimeDataMap::iterator _iter = this->m_TimeDataMap.find(uID);
	if (_iter == this->m_TimeDataMap.end())
	{
		return Py_None;
	}
	else
	{
		return _iter->second;
	}
}

PyObject* GETimeData::FindAndRemoveData_NewRef( GE::Uint64 uID )
{
	TimeDataMap::iterator _iter = this->m_TimeDataMap.find(uID);
	if (_iter == this->m_TimeDataMap.end())
	{
		Py_RETURN_NONE;
	}
	else
	{
		/************************************************************************
		注意，这里在注册的时候增加了引用计数，此时有将这个Py从map中删除并返回引用，
		一加一减恰好抵消了，故没做引用计数的变化。
		************************************************************************/
		PyObject* p = _iter->second;
		this->m_TimeDataMap.erase(_iter);
		return p;
	}
}

void GETimeData::CallPerMinute()
{
	// 计数现在的超时时间
	GE::B8 _now(0, GEDateTime::Instance()->Seconds() + 1);
	TimeDataMap::iterator _cbegin = this->m_TimeDataMap.begin();
	TimeDataMap::iterator _cend = this->m_TimeDataMap.upper_bound(_now.UI64());
	// 是否超时的Python数据
	while(_cbegin != _cend)
	{
		Py_DECREF(_cbegin->second);
		this->m_TimeDataMap.erase(_cbegin++);
	}
}


