/************************************************************************
角色日志
************************************************************************/
#pragma once
#include <stack>
#include "../GameEngine/GameEngine.h"

class LogTransaction
	: public GEControlSingleton<LogTransaction>
{
	struct __SI
	{
		GE::Uint16			uTransaction;
		GE::Int64			nLogID;
	};

public:
	LogTransaction();
	~LogTransaction();
	void					LoadPyData();
public:
	void					StartTransaction(GE::Uint16 uTransaction);
	void					EndTransaction();

	bool					HasTransaction();
	void					GetTransaction(GE::Uint16& uTransaction, GE::Int64& nLogID);
	void					GetTransactionForEvent(GE::Uint16& uTransaction, GE::Int64& nLogID);

	void					CallPerSecond();

	GE::Uint16				GetEvent() {return m_uEvents;}

	void					LogValue(GE::Int64 uRoleID, GE::Uint16 uEvent, GE::Int64 nOld, GE::Int64 nNew);

private:
	GE::Uint16				m_uCnt;
	GE::Uint16				m_uEvents;
	std::stack<__SI>		m_Transactions;
	GEPython::Function		m_pyLogValue;
};

