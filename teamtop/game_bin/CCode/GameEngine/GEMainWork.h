/************************************************************************
工作检测，主要用于检测主线程是否卡或者死循环了
************************************************************************/
#pragma once
#include <boost/thread.hpp>
#include "GEControlSingleton.h"

class GEMainWork
	: public GEControlSingleton<GEMainWork>
{
public:
	GEMainWork();
	~GEMainWork();

public:
	void				Start();
	void				Stop();
	void				Loop();

private:
	bool				m_bIsRun;
	boost::thread*		m_pThread;
};

