/************************************************************************
可控制生命周期的单件
************************************************************************/
#pragma once

template<class T>
class GEControlSingleton
{
public:
	static void		New() {m_pIntance = new T;}
	static void		Delete() {if(m_pIntance) {delete m_pIntance; m_pIntance = NULL;};}
	static T*		Instance( void ) {return m_pIntance;}

protected:
	GEControlSingleton( void ){m_pIntance = NULL;}
	~GEControlSingleton( void ){}

protected:
	static T* m_pIntance;
};

template<class T>
T* GEControlSingleton<T>::m_pIntance;

