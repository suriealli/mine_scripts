/************************************************************************
脚本管理
************************************************************************/
#pragma once
#include <vector>
#include "../GameEngine/GameEngine.h"

#define MAX_FLAG_SIZE 100

class ScriptMgr
	: public GEControlSingleton<ScriptMgr>
{
	typedef std::vector<GEPython::Object>		ObjVector;
	typedef std::vector<bool>					BoolVector;
	GE_DISABLE_BOJ_CPY(ScriptMgr);
public:
	ScriptMgr();
	~ScriptMgr();
		
public:
	// 载入python数据
	void								LoadPyData();
	// 打印Python栈
	void								StackWarn(const char* pWarn = NULL);

	// C++中检测标准位，触发Python更新
	GE::Uint16							AllotFlagIndex();
	void								DirtyFlag(GE::Uint16 uIdx);
	void								SetClearFun(GE::Uint16 uIdx, PyObject* callable_BorrowRef);
	void								CallPerSecond();

public:
	GEPython::Function					m_pyDebugOnDistriubte;		//显示接收的消息
	GEPython::Function					m_pyDebugDoSendObj;			//显示发送的消息
	GEPython::Function					m_pyDebugOnCallback;		//显示接收的回调消息
	GEPython::Function					m_pyDebugDoCallback;		//显示发送的回调消息
	GEPython::Function					m_pyWatchRoleDistribute;	//观察角色发生的消息

private:
	GEPython::Function					m_pyTraceback;				//打印当前Python堆栈
	GE::Int16							m_nMaxIdx;					//最大标识数组
	ObjVector							m_pyObjVector;				//标识清理函数
	BoolVector							m_FlagVector;				//标识位
};

