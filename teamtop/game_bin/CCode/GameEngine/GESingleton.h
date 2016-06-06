/************************************************************************
单件定义相关
class C : public GESingleton<C>
************************************************************************/
#pragma once

template<typename T>
class GESingleton
{
public:
	static T*		Instance( void ) {return &m_pIntance;}

protected:
	GESingleton( void ){m_pIntance;}
	~GESingleton( void ){}

protected:
	static T m_pIntance;
};

template<typename T>
T GESingleton<T>::m_pIntance;

