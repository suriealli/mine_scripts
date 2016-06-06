/************************************************************************
安全静态（编译期确定）字符串数组。
相比std::string, 本安全字符串数组支持bitcopy
相比GESafeArray<char>，本安全字符串数组兼容c格式的字符串
************************************************************************/
#pragma once
#include <string.h>
#include <string>
#include "GEInteger.h"

template<GE::Uint16 arrSize>
class GESafeString
{
public:
	GESafeString(): m_uCurSize(0), m_uMaxSize(arrSize - 1) {m_arrData[m_uMaxSize] = '\0';}
	~GESafeString() {}

	char& operator[](GE::Uint16 uIdx);				//索引（安全）
	char&					At(GE::Uint16 uIdx);	//索引（不安全）
	GE::Uint16				CurSize();				//当前字符串长度
	GE::Uint16				MaxSize();				//最大可以存储的字符串长度
	char*					HeadPrt();				//头指针
	void					Assign(const char* prt);					//字符串填充
	void					Assign(const char* ptr, GE::Uint16 uSize);	//字符串填充
	void					Assign(const std::string& szStr);			//字符串填充

private:
	GE::Uint16				m_uCurSize;
	GE::Uint16				m_uMaxSize;
	char					m_arrData[arrSize];
};

template<GE::Uint16 arrSize>
char& GESafeString<arrSize>::operator[]( GE::Uint16 uIdx )
{
	GE_ERROR(uIdx < arrSize);
	return m_arrData[uIdx];
}

template<GE::Uint16 arrSize>
char& GESafeString<arrSize>::At( GE::Uint16 uIdx )
{
	return m_arrData[uIdx];
}

template<GE::Uint16 arrSize>
GE::Uint16 GESafeString<arrSize>::CurSize()
{
	return m_uCurSize;
}

template<GE::Uint16 arrSize>
GE::Uint16 GESafeString<arrSize>::MaxSize()
{
	return arrSize;
}

template<GE::Uint16 arrSize>
char* GESafeString<arrSize>::HeadPrt()
{
	return m_arrData;
}

template<GE::Uint16 arrSize>
void GESafeString<arrSize>::Assign( const char* ptr )
{
	GE::Uint16 uSize = static_cast<GE::Uint16>(strnlen(ptr, arrSize));
	m_uCurSize = GE_MIN(arrSize, uSize);
	memcpy(m_arrData, ptr, m_uCurSize);
	m_arrData[m_uCurSize] = '\0';
}

template<GE::Uint16 arrSize>
void GESafeString<arrSize>::Assign( const char* ptr, GE::Uint16 uSize )
{
	m_uCurSize = GE_MIN(arrSize, uSize);
	memcpy(m_arrData, ptr, m_uCurSize);
	m_arrData[m_uCurSize] = '\0';
}

template<GE::Uint16 arrSize>
void GESafeString<arrSize>::Assign( const std::string& szStr )
{
	this->Assign(szStr.data(), static_cast<GE::Uint16>(szStr.length()));
}

