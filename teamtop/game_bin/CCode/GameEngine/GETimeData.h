/************************************************************************
限时Python数据委托
************************************************************************/
#pragma once
#include <map>
#include "GEInteger.h"
#include "PyTimeData.h"


// 低精度python数据委托管理
class GETimeData
{
	typedef std::map<GE::Uint64, PyObject*>		TimeDataMap;
public:
	GETimeData();
	~GETimeData();

public:
	GE::Uint64					HoldData(GE::Uint32 uTimeSec, PyObject* pyData_BorrowRef);	//委托管理一份Python数据
	void						RemoveData(GE::Uint64 uID);									//删除委托的Python数据
	PyObject*					FindData_NewRef(GE::Uint64 uID);							//查找一个委托的Python数据（引用）
	PyObject*					FindData_BorrowRef(GE::Uint64 uID);							//查找一个委托的Python数据（借用）
	PyObject*					FindAndRemoveData_NewRef(GE::Uint64 uID);					//查找并删除一个委托的Python数据

	void						CallPerMinute();											//每分钟驱动的函数
	GEPython::Object			PySelf() {return m_pySelf;}									//获取对应的Python对象

private:
	GE::Uint32					m_uLowerID;													//自累加变量
	GEPython::Object			m_pySelf;													//自身Python对象
	TimeDataMap					m_TimeDataMap;												//委托数据的Map
};

