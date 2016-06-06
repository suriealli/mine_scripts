/*我是UTF8无签名编码 */
#include "LogTransaction.h"

LogTransaction::LogTransaction()
	: m_uCnt(0)
	, m_uEvents(0)
{
	
}

LogTransaction::~LogTransaction()
{

}

void LogTransaction::StartTransaction( GE::Uint16 uTransaction )
{
	this->m_uEvents = 0;
	++m_uCnt;
	__SI SI;
	SI.uTransaction = uTransaction;
	GE::B8& b8 = GE_AS_B8(SI.nLogID);
	b8.UI16_3() = GEProcess::Instance()->ProcessID();
	b8.UI16_2() = m_uCnt;
	b8.UI32_0() = GEDateTime::Instance()->Seconds();
	this->m_Transactions.push(SI);
}

void LogTransaction::EndTransaction()
{
	if (this->m_Transactions.empty())
	{
		GE_EXC<<"no Transaction but end."<<GE_END;
	}
	else
	{
		this->m_Transactions.pop();
	}
	this->m_uEvents = 0;
}

bool LogTransaction::HasTransaction()
{
	return !this->m_Transactions.empty();
}

void LogTransaction::GetTransaction( GE::Uint16& uTransaction, GE::Int64& nLogID )
{
	if (this->m_Transactions.empty())
	{
		uTransaction = 0;
		++m_uCnt;
		GE::B8& b8 = GE_AS_B8(nLogID);
		b8.UI16_3() = GEProcess::Instance()->ProcessID();
		b8.UI16_2() = m_uCnt;
		b8.UI32_0() = GEDateTime::Instance()->Seconds();
	}
	else
	{
		const __SI& ST = this->m_Transactions.top();
		uTransaction = ST.uTransaction;
		nLogID = ST.nLogID;
	}
}

void LogTransaction::GetTransactionForEvent( GE::Uint16& uTransaction, GE::Int64& nLogID )
{
	this->GetTransaction(uTransaction, nLogID);
	++this->m_uEvents;
}

void LogTransaction::CallPerSecond()
{
	if (!this->m_Transactions.empty())
	{
		const __SI& ST = this->m_Transactions.top();
		GE_EXC<<"Transaction("<<ST.uTransaction<<") is not none when check."<<GE_END;
		this->m_Transactions.pop();
	}
}

void LogTransaction::LogValue( GE::Int64 uRoleID, GE::Uint16 uEvent, GE::Int64 nOld, GE::Int64 nNew )
{
	GE::Uint16 uTransaction = 0;
	GE::Int64 nLogID = 0;
	this->GetTransactionForEvent(uTransaction, nLogID);
	this->m_pyLogValue.Call("KKHHLL", nLogID, uRoleID, uTransaction, uEvent, nOld, nNew);
}

void LogTransaction::LoadPyData()
{
	this->m_pyLogValue.Load("ComplexServer.Log.AutoLog", "__LogValue");
}

