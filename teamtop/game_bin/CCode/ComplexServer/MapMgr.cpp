#include "MapMgr.h"

//////////////////////////////////////////////////////////////////////////
// MapTemplate
//////////////////////////////////////////////////////////////////////////
MapTemplate::MapTemplate( GE::Uint16 uMapId, const std::string& szFilePath )
	: m_uMapId(uMapId)
	, m_uWidth(0)
	, m_uHight(0)
	, m_bIsRload(true)
	, m_uNums(0)
	, m_uGridPropertys(NULL)
	, m_szFilePath(szFilePath)
	, m_uSafeX(99)
	, m_uSafeY(99)
{

}

MapTemplate::~MapTemplate()
{
	if (NULL != this->m_uGridPropertys)
	{
		delete [] m_uGridPropertys;
	}
}

void MapTemplate::Load()
{
	if (!this->m_bIsRload)
	{
		// 只读入一次，可以支持重新读入
		return;
	}
	this->m_bIsRload = false;
	GETabFile TF(this->m_szFilePath);
	this->m_uXPix = TF.GetNextValue<GE::Uint16>();
	this->m_uYPix = TF.GetNextValue<GE::Uint16>();
	this->m_uWidth = TF.GetNextValue<GE::Uint16>();
	this->m_uHight = TF.GetNextValue<GE::Uint16>();
	this->m_uNums = this->m_uWidth * this->m_uHight;
	this->m_uMaxXPix = this->m_uXPix * this->m_uWidth;
	this->m_uMaxYPix = this->m_uYPix * this->m_uHight;
	GE::Uint8* pGT = new GE::Uint8[this->GridNums()];
	GE_ITER_UI32(idx, this->m_uNums)
	{
		if (TF.IsEof())
		{
			delete [] pGT;
			GE_EXC<<"error on load map("<<this->m_uMapId<<") from path("<<this->m_szFilePath<<")."<<GE_END;
			return;
		}
		pGT[idx] = TF.GetNextUint8();
	}
	if (NULL != this->m_uGridPropertys)
	{
		delete [] this->m_uGridPropertys;
	}
	this->m_uGridPropertys = pGT;
}

void MapTemplate::Reload()
{
	this->m_bIsRload = true;
	this->Load();
}

// 像素转换成格子数组下标
GE::Uint32 MapTemplate::Pos2Index( GE::Uint16 uX, GE::Uint16 uY )
{
	return (uY / this->m_uYPix) * this->m_uWidth + (uX / this->m_uXPix);
}

// 像素所在格子属性
GE::Uint8 MapTemplate::Property( GE::Uint16 uX, GE::Uint16 uY )
{
	return this->Property(this->Pos2Index(uX, uY));
}

GE::Uint8 MapTemplate::Property( GE::Uint32 uIndex )
{
	GE_ASSERT(uIndex < this->m_uNums);
	return this->m_uGridPropertys[uIndex];
}



//////////////////////////////////////////////////////////////////////////
// MapMgr
//////////////////////////////////////////////////////////////////////////
MapMgr::MapMgr()
{

}

MapMgr::~MapMgr()
{
	MapTemplateMap::iterator iter = this->m_MapTemplateMap.begin();
	for(; iter != this->m_MapTemplateMap.end(); ++iter)
	{
		delete iter->second;
		iter->second = NULL;
	}
	this->m_MapTemplateMap.clear();

}

void MapMgr::CreateMapTemplate( GE::Uint16 uMapId, const std::string& szFilePath )
{
	if (this->m_MapTemplateMap.find(uMapId) != this->m_MapTemplateMap.end())
	{
		GE_EXC<<"repeat create map("<<uMapId<<") template."<<GE_END;
		return;
	}
	// 只读入基本数据，暂时不读入格子属性，因为某些场景只配置在特定的逻辑服创建
	this->m_MapTemplateMap.insert(std::make_pair(uMapId, new MapTemplate(uMapId, szFilePath)));
}


MapTemplate* MapMgr::ReloadMapTemplate( GE::Uint16 uMapId )
{
	MapTemplateMap::iterator iter = this->m_MapTemplateMap.find(uMapId);
	if (iter == this->m_MapTemplateMap.end())
	{
		GE_EXC<<"can't find map("<<uMapId<<"). for reload"<<GE_END;
		return NULL;
	}
	MapTemplate* pMT = iter->second;
	pMT->Reload();
	return pMT;
}

MapTemplate* MapMgr::GetHasLoadMapTemplate( GE::Uint16 uMapId )
{
	MapTemplateMap::iterator iter = this->m_MapTemplateMap.find(uMapId);
	if (iter == this->m_MapTemplateMap.end())
	{
		return NULL;
	}
	MapTemplate* pMT = iter->second;
	pMT->Load();
	if (pMT->IsOK())
	{
		return pMT;
	}
	else
	{
		return NULL;
	}
}

bool MapMgr::SetSafePos( GE::Uint16 uMapId, GE::Uint16 uX, GE::Uint16 uY )
{
	MapTemplateMap::const_iterator citer = this->m_MapTemplateMap.find(uMapId);
	if (citer == this->m_MapTemplateMap.end())
	{
		return false;
	}
	MapTemplate* pMT = citer->second;
	pMT->SafeX() = uX;
	pMT->SafeY() = uY;
	return true;
}

