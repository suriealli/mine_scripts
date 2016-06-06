/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "Role.h"
#include "NPC.h"
#include "Area.h"

// 根据一个像素坐标，返回一个对应的格子下标
#define POS_2_GRID_INDEX(uX, uY, dosomething)	\
	this->m_pMapTemplate->Pos2Index(uX, uY);	\
	if (uX >= this->m_pMapTemplate->MaxXPix() || uY >= this->m_pMapTemplate->MaxYPix()) {dosomething;}

// 根据一个像素坐标，返回一个对应的区域下标
#define POS_2_AREA_INDEX(uX, uY, dosomething)	\
	this->Pos_2_Area_Index(uX, uY);	\
	if (uX >= this->m_pMapTemplate->MaxXPix() || uY >= this->m_pMapTemplate->MaxYPix()) {dosomething;}


// 一些全局宏的定义
//地图格子最大数量
#define GLOBAL_MAP_GRID_MAX_ARRAY_SIZE		40000
//地图玩家最大数量
#define GLOBAL_PLAYER_ARRAY_MAX_SIZE		100000
//地图非玩家最大数量
#define GLOBAL_NONPLAYER_ARRAY_MAX_SIZE		100000

// 最大的格子基础属性(静态)，0-100，剩下的 101-255是动态格子属性
#define MAX_BASE_GRID_PROPERTY				100

//区域9宫格
#define AREA_VISIABLE_SIZE					2

enum MoveType
{
	enCanNotMove = 0,
	enMoveIter = 1,
	enMoveNotIterOther = 2,
};



// 地图格子类型
enum MapGridType
{
	enVisable,	//可视
	enUnVisable,//不可视
	enMove		//可走
};

// 有时候不用把区域里面的全部数据都放到迭代器里面，所以需要有选择
enum InsertAreaDataType
{
	enALL,
	enPlayer,
	enNonPlayer
};

class MapTemplate;
//////////////////////////////////////////////////////////////////////////
// 全局区域内容对象数组(玩家)(非玩家)
//////////////////////////////////////////////////////////////////////////
class GlobalAreaDataArray
	: public GESingleton<GlobalAreaDataArray>
{
	
public:
	GlobalAreaDataArray();
	~GlobalAreaDataArray();

	// 清理数据
	void					Clear();
	// 同步初始化数组下标，需在插入相关数据时初始化
	void					InitUnVisibleArea();
public:
	// 玩家迭代(对外接口)
	void					BeginIteratorVisiblePlayer();
	Role*					GetNextVisiblePlayer();

	void					BeginIteratorUnVisiblePlayer();
	Role*					GetNextUnVisiblePlayer();

	//NPC
	void					BeginIteratorVisibleNPC();
	NPC*					GetNextVisibleNPC();

	void					BeginIteratorUnVisibleNPC();
	NPC*					GetNextUnVisibleNPC();

public:
	// 把一个格子的数据全部插入到数组里面
	void					InsertVisableArea(Area& area, InsertAreaDataType insertType = enALL);

	void					InsertUnVisableArea(Area& area, InsertAreaDataType insertType = enALL);
private:
	// 插入一个数据到数组里
	bool					InsertVisiblePlayer(Role* pRole);
	bool					InsertUnVisiblePlayer(Role* pRole);

	// 
	bool					InsertVisibleNPC(NPC* pNPC);
	bool					InsertUnVisibleNPC(NPC* pNPC);
private:
	//临时缓存列表
	RoleMenberList*			m_pTempRoleList;
	NPCMemberList*			m_pTempNPCList;

	// 缓存迭代器
	RML_ITER				m_rml_iter;
	NML_ITER				m_nml_iter;

private:
	// 缓存数组
	Role*					m_pRoleArray[GLOBAL_PLAYER_ARRAY_MAX_SIZE];
	NPC*					m_pNPCArray[GLOBAL_NONPLAYER_ARRAY_MAX_SIZE];

	// 数组段已用下标
	GE::Uint32				m_uVisiblePlayerEndIndex;
	GE::Uint32				m_uUnVisiblePlayerEndIndex;


	GE::Uint32				m_uVisibleNPCEndIndex;
	GE::Uint32				m_uUnVisibleNPCEndIndex;

	// 对外迭代Index,用于迭代输出缓存数组的数据
	GE::Uint32				m_uIterIndex;
};



//////////////////////////////////////////////////////////////////////////
//正方形区域地图对象
//一个AreaMap对象有n个区域，每个区域由M个格子组成
class AreaMap
{
public:
	AreaMap(MapTemplate* pMT, GE::Uint8 uAreaSize, bool bCanSeeOther = false);
	~AreaMap();

public:

	//模板地图ID
	GE::Uint16				MapID();
	GE::Uint16				TotalRole(){return m_uTotalPlayer;}

	void					SetCanSeeOther(bool b);
public:
	//格子属性
	GE::Uint8				GridProperty(GE::Uint16 uIndex);
	GE::Uint8				GridProperty(GE::Uint16 uX, GE::Uint16 uY);
	//区域边长多少个格子
	GE::Uint8				AreaSize(){return m_uAreaSize;}
	//区域边长多少像素
	GE::Uint16				AreaLength(){return m_uAreaLength;}
	//坐标所在的区域下标
	GE::Uint16				Pos_2_Area_Index(GE::Uint16 uX, GE::Uint16 uY);

	//检查这个区域下标是否可用
	bool					AreaIndex_Vaile(GE::Uint16 uIndex){return uIndex < m_uTotalArea;}

public:
	//对外接口，玩家(安全)进入地图，移除地图，移动相关
	bool					JoinRole_S(Role* pRole, GE::Uint16& uX, GE::Uint16& uY);
	GE::Uint8				MoveRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	bool					LeaveRole(Role* pRole);

private:
	//内部实现进入地图
	bool					JoinRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);

public:
	bool					JoinNPC(NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY);
	bool					LeaveNPC(NPC* pNPC);

public:
	void					FindVisibleRect(GE::Uint16 uX, GE::Uint16 uY);

	// 根据下标迭代默认九宫格内容
	void					FindVisibleRect(GE::Uint16 uAreaIndex, InsertAreaDataType dataType = enALL, GE::Uint16 uRectSize = AREA_VISIABLE_SIZE);
	void					FindByMove(GE::Uint16 uSrcGridIndex, GE::Uint16 uDesGridIndex);
	void					FindUnVisibleRect(GE::Uint16 uAreaIndex);

	// 把一个矩形方块内的网格迭代出来
	void					InsertVisibleRect(GE::Int16 linesBegin, GE::Int16 linesEnd, GE::Int16 rowsBegin, GE::Int16 rowsEnd, InsertAreaDataType insertType = enALL);
	void					InsertUnVisibleRect(GE::Int16 linesBegin, GE::Int16 linesEnd, GE::Int16 rowsBegin, GE::Int16 rowsEnd);
	
	// 迭代新可视玩家
	void					BeginIteratorNewVisiblePlayer();
	Role*					GetNextNewVisiblePlayer();
	// 新的不可视玩家
	void					BeginIteratorNewUnvisiblePlayer();
	Role*					GetNextNewUnvisiblePlayer();

	// 迭代当前坐标九宫格内的所有玩家
	void					BeginIteratorRectPlayer(GE::Uint16 uX, GE::Uint16 uY);
	Role*					GetNextRectPlayer();


	// 迭代新可视NPC
	void					BeginIteratorNewVisibleNPC();
	NPC*					GetNextNewVisibleNPC();
	// 新的不可视NPC
	void					BeginIteratorNewUnvisibleNPC();
	NPC*					GetNextNewUnvisibleNPC();

	// 迭代当前坐标九宫格内的所有NPC
	void					BeginIteratorRectNPC(GE::Uint16 uX, GE::Uint16 uY, GE::Uint16 uRectSize = AREA_VISIABLE_SIZE);
	NPC*					GetNextRectNPC();
private:
	// 指定范围的矩形区域(默认九宫格)
	GE::Int16				BeginLines(GE::Int16 lines, GE::Uint16 uRectSize = AREA_VISIABLE_SIZE);
	GE::Int16				EndLines(GE::Int16 lines, GE::Uint16 uRectSize = AREA_VISIABLE_SIZE);
	GE::Int16				BeginRows(GE::Int16 rows, GE::Uint16 uRectSize = AREA_VISIABLE_SIZE);
	GE::Int16				EndRows(GE::Int16 rows, GE::Uint16 uRectSize = AREA_VISIABLE_SIZE);


private:
	Area*					m_pAreaArray;		//区域数组
	MapTemplate*			m_pMapTemplate;		//地图配置数据

	GE::Uint8				m_uAreaSize;		//区域边长(边长多少个格子)

	GE::Uint16				m_uAreaLength;		//区域边长(像素)

	GE::Uint16				m_uAreaWidthNum;	//横向区域数量
	GE::Uint16				m_uAreaHightNum;	//竖向区域数量

	GE::Uint16				m_uTotalArea;		//总的区域数
	GE::Uint32				m_uTotalPlayer;
	GE::Uint32				m_uTotalNPC;

	bool					m_bCanSeeOther;
};

