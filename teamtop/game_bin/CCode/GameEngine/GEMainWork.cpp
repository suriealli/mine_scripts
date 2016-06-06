/*我是UTF8无签名编码 */
#include "GEMainWork.h"
#include "GEDateTime.h"

GEMainWork::GEMainWork()
	: m_bIsRun(false)
	, m_pThread(NULL)
{

}

GEMainWork::~GEMainWork()
{

}

void GEMainWork::Start()
{
	if (this->m_pThread)
	{
		return;
	}
	this->m_bIsRun = true;
	this->m_pThread = new boost::thread(boost::bind(&GEMainWork::Loop, this));
}

void GEMainWork::Stop()
{
	if (NULL == this->m_pThread)
	{
		return;
	}
	this->m_bIsRun = false;
	this->m_pThread->timed_join(boost::posix_time::seconds(5));
	delete this->m_pThread;
	this->m_pThread = NULL;
}

void GEMainWork::Loop()
{
	while(this->m_bIsRun)
	{
		GE::Uint64 time = GEDateTime::Instance()->MSeconds();
		GE::Int64 count = GEPython::Function::m_uCallCount;
		GEDateTime::Instance()->SleepMsec(2000);
	}
}

