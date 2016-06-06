/************************************************************************
读取以Tab作为换行符的文件
************************************************************************/
#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include "GEInteger.h"

class GETabFile
{
public:
	GETabFile(const char* sFilePath);
	GETabFile(const std::string& szFilePath);
	virtual ~GETabFile(void);

public:
	bool IsEof();						//是否结束了
	void PassLine(long columnCnt);		//忽视一行

	// 获取下一个值
	template <typename T>
	T GetNextValue();

	/*
	注意，获取Uint8的值必须用下面这个函数
	因为Uint8 其实是unsigned char 如果用GetNextValue<GE::Uint8>则会按照unsigned char读取
	*/
	GE::Uint8	GetNextUint8() {return static_cast<GE::Uint8>(this->GetNextValue<GE::Uint16>());}

private:
	void CheckEmpty();					//检测文件

private:
	std::ifstream		fin;			//读取文件流
	std::string			m_szFilePath;	//文件路径
	bool				m_bEmpty;		//是否是空
};

template <typename T>
T GETabFile::GetNextValue()
{
	T val;
	fin>>val;
	return val;
}

// 将整个文件读取为一个值
template <typename VT>
bool GetFileValue(char* filePath, VT& vt)
{
	std::ifstream fin;
	fin.open(filePath);
	if (fin.peek() == EOF)
	{
		return false;
	}
	fin>>vt;
	fin.close();
	return true;
}

