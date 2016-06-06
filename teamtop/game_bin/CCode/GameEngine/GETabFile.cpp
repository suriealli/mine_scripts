/*读取Tab分隔符文件 */
#include "GETabFile.h"
#include "GEIO.h"

GETabFile::GETabFile(const char* sFilePath)
	: m_szFilePath(sFilePath)
	, m_bEmpty(false)
{
	this->fin.open(m_szFilePath.c_str());
	this->CheckEmpty();
}

GETabFile::GETabFile( const std::string& szFilePath )
	: m_szFilePath(szFilePath)
	, m_bEmpty(false)
{
	this->fin.open(m_szFilePath.c_str());
	this->CheckEmpty();
}

GETabFile::~GETabFile(void)
{
	this->fin.close();
}

bool GETabFile::IsEof()
{
	if (m_bEmpty)
	{
		return true;
	}
	return fin.eof();
}

void GETabFile::PassLine(long columnCnt)
{
	if (m_bEmpty)
	{
		return;
	}
	std::string temp;
	for (long idx = 0; idx < columnCnt; idx++)
	{
		fin>>temp;
	}
}

void GETabFile::CheckEmpty()
{
	if (this->fin.peek() == EOF)
	{
		m_bEmpty = true;
		GE_EXC<<"not exist file("<<m_szFilePath<<") or the file is empty!"<<GE_END;
	}
}

