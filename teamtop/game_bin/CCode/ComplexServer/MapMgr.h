/************************************************************************
地图模板:
@读配置生产的缓存数据，用于生产场景地图，原则上这些数据都不能被修改，
除了重新加载地图配置数据。

@同一个地图模板可以生成不同的场景地图
************************************************************************/
#pragma once
#include <string>
#include <boost/unordered_map.hpp>
#include "../GameEngine/GameEngine.h"

// 地图模板
class MapTemplate
{
public:
	MapTemplate(GE::Uint16 uMapId, const std::string& szFilePath);
	~MapTemplate();

public:
	void					Load();
	// 支持重加载
	void					Reload();
	bool					IsOK() {return NULL!= this->m_uGridPropertys;}
	GE::Uint16				MapId() {return m_uMapId;}
	GE::Uint16				Width() {return m_uWidth;}
	GE::Uint16				Hight() {return m_uHight;}
	GE::Uint32				GridNums() {return m_uNums;}
	GE::Uint32				Pos2Index(GE::Uint16 uX, GE::Uint16 uY);
	GE::Uint8				Property(GE::Uint16 uX, GE::Uint16 uY);
	GE::Uint8				Property(GE::Uint32 uIndex);

	GE::Uint16				MaxXPix(){ return m_uMaxXPix;}
	GE::Uint16				MaxYPix(){ return m_uMaxYPix;}
	GE::Uint16				XPix(){ return m_uXPix; }
	GE::Uint16				YPix(){ return m_uYPix; }

	GE::Uint16&				SafeX() {return m_uSafeX;}
	GE::Uint16&				SafeY() {return m_uSafeY;}
private:
	GE::Uint16				m_uXPix;			//格子宽像素
	GE::Uint16				m_uYPix;			//格子高像素
	GE::Uint16				m_uMapId;			//地图ID
	GE::Uint16				m_uWidth;			//横向格子数量
	GE::Uint16				m_uHight;			//竖向格子数量
	GE::Uint16				m_uMaxXPix;			//地图横向最大像素
	GE::Uint16				m_uMaxYPix;			//地图竖向最大像素
	bool					m_bIsRload;			//是否已经载入过
	GE::Uint32				m_uNums;			//格子总数量
	GE::Uint8*				m_uGridPropertys;	//格子属性
	std::string				m_szFilePath;		//地图文件路径
	GE::Uint16				m_uSafeX;			//安全坐标（X）
	GE::Uint16				m_uSafeY;			//安去坐标（Y)
};


// 地图管理器
class MapMgr
	:public GESingleton<MapMgr>
{
	typedef boost::unordered_map<GE::Uint16, MapTemplate*>		MapTemplateMap;
public:
	MapMgr();
	~MapMgr();

public:
	// 创建一个地图模板，暂时不读入格子属性，等需要创建场景时才读入一次数据到缓存中
	void					CreateMapTemplate(GE::Uint16 uMapId, const std::string& szFilePath);
	/*
	这里要注意下，ReloadMapTemplate 和 GetHasLoadMapTemplate 这两个函数返回的指针是可以被外部保存的，
	所有，在修改这个类的代码的时候要注意这个特性啊。
	*/
	// 读取配置载入地图模板数据
	MapTemplate*			ReloadMapTemplate(GE::Uint16 uMapId);
	// 根据mapId，获取一个已经载入数据了的地图模板
	MapTemplate*			GetHasLoadMapTemplate(GE::Uint16 uMapId);

	//设置安全坐标
	bool					SetSafePos(GE::Uint16 uMapId, GE::Uint16 uX, GE::Uint16 uY);
private:
	MapTemplateMap			m_MapTemplateMap;
};

