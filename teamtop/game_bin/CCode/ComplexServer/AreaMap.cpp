#include "AreaMap.h"
#include "MapMgr.h"

GlobalAreaDataArray::GlobalAreaDataArray()
	: m_uVisiblePlayerEndIndex(0)
	, m_uUnVisiblePlayerEndIndex(0)
	, m_uVisibleNPCEndIndex(0)
	, m_uUnVisibleNPCEndIndex(0)
{
}

GlobalAreaDataArray::~GlobalAreaDataArray()
{
	this->Clear();
}

void GlobalAreaDataArray::Clear()
{
	GE::Uint32 uMax = GE_MAX(this->m_uVisiblePlayerEndIndex, this->m_uUnVisiblePlayerEndIndex);
	// 清除所有的缓存，等待插入新的迭代数据
	for (GE::Uint32 i = 0; i < uMax; ++i)
	{
		this->m_pRoleArray[i] = NULL;
	}
	// 下标设置为0
	this->m_uVisiblePlayerEndIndex = 0;
	this->m_uUnVisiblePlayerEndIndex = 0;


	uMax = GE_MAX(this->m_uVisibleNPCEndIndex, this->m_uUnVisibleNPCEndIndex);
	// 清除所有的缓存，等待插入新的迭代数据
	for (GE::Uint32 i = 0; i < uMax; ++i)
	{
		this->m_pNPCArray[i] = NULL;
	}
	// 下标设置为0
	this->m_uVisibleNPCEndIndex = 0;
	this->m_uUnVisibleNPCEndIndex = 0;

}

// 同步初始化函数
// 因为数据是分2段存储在数组中，所以需要2个下标来标记数据段
// 在插入后两段数据时就要改变其实下标了
void GlobalAreaDataArray::InitUnVisibleArea()
{
	this->m_uUnVisiblePlayerEndIndex = this->m_uVisiblePlayerEndIndex;

	this->m_uUnVisibleNPCEndIndex = this->m_uVisibleNPCEndIndex;
}

void GlobalAreaDataArray::BeginIteratorVisiblePlayer()
{
	// 开始迭代可视玩家，设置迭代下标
	this->m_uIterIndex = 0;
}

void GlobalAreaDataArray::BeginIteratorUnVisiblePlayer()
{
	// 迭代不可视玩家时，迭代下标是可视玩家的结束下标
	this->m_uIterIndex = this->m_uVisiblePlayerEndIndex;
}
// 获取数据
Role* GlobalAreaDataArray::GetNextVisiblePlayer()
{
	if(this->m_uIterIndex < this->m_uVisiblePlayerEndIndex)
	{
		return this->m_pRoleArray[this->m_uIterIndex++];
	}
	else
	{
		return NULL;
	}
}

Role* GlobalAreaDataArray::GetNextUnVisiblePlayer()
{
	if(this->m_uIterIndex < this->m_uUnVisiblePlayerEndIndex)
	{
		return this->m_pRoleArray[this->m_uIterIndex++];
	}
	else
	{
		return NULL;
	}
}

void GlobalAreaDataArray::BeginIteratorVisibleNPC()
{
	// 开始迭代可视玩家，设置迭代下标
	this->m_uIterIndex = 0;
}

void GlobalAreaDataArray::BeginIteratorUnVisibleNPC()
{
	// 迭代不可视玩家时，迭代下标是可视玩家的结束下标
	this->m_uIterIndex = this->m_uVisibleNPCEndIndex;
}
// 获取数据
NPC* GlobalAreaDataArray::GetNextVisibleNPC()
{
	if(this->m_uIterIndex < this->m_uVisibleNPCEndIndex)
	{
		return this->m_pNPCArray[this->m_uIterIndex++];
	}
	else
	{
		return NULL;
	}
}

NPC* GlobalAreaDataArray::GetNextUnVisibleNPC()
{
	if(this->m_uIterIndex < this->m_uUnVisibleNPCEndIndex)
	{
		return this->m_pNPCArray[this->m_uIterIndex++];
	}
	else
	{
		return NULL;
	}
}


bool GlobalAreaDataArray::InsertVisiblePlayer( Role* pRole )
{
	// 插入一个可视的玩家
	if(this->m_uVisiblePlayerEndIndex >= 0 && this->m_uVisiblePlayerEndIndex < GLOBAL_PLAYER_ARRAY_MAX_SIZE)
	{
		this->m_pRoleArray[this->m_uVisiblePlayerEndIndex] = pRole;
		++this->m_uVisiblePlayerEndIndex;// 移动下标
		return true;
	}
	else
	{	
		GE_EXC<<" over flow in GlobalAreaDataArray::InsertVisiblePlayer"<<GE_END;
		return false;
	}
}

bool GlobalAreaDataArray::InsertUnVisiblePlayer( Role* pRole )
{
	// 插入不可视玩家，插入第一次应该先调用同步初始化函数
	if(this->m_uUnVisiblePlayerEndIndex >= this->m_uVisiblePlayerEndIndex && this->m_uUnVisiblePlayerEndIndex < GLOBAL_PLAYER_ARRAY_MAX_SIZE)
	{
		this->m_pRoleArray[this->m_uUnVisiblePlayerEndIndex] = pRole;
		++this->m_uUnVisiblePlayerEndIndex;
		return true;
	}
	else
	{	
		GE_EXC<<" over flow in GlobalAreaDataArray::InsertUnVisiblePlayer"<<GE_END;
		return false;
	}
}


bool GlobalAreaDataArray::InsertVisibleNPC( NPC* pNPC )
{
	// 插入一个可视的NPC
	if(this->m_uVisibleNPCEndIndex >= 0 && this->m_uVisibleNPCEndIndex < GLOBAL_NONPLAYER_ARRAY_MAX_SIZE)
	{
		this->m_pNPCArray[this->m_uVisibleNPCEndIndex] = pNPC;
		++this->m_uVisibleNPCEndIndex;// 移动下标
		return true;
	}
	else
	{	
		GE_EXC<<" over flow in GlobalAreaDataArray::InsertVisibleNPC"<<GE_END;
		return false;
	}
}

bool GlobalAreaDataArray::InsertUnVisibleNPC( NPC* pNPC )
{
	// 插入不可视玩家，插入第一次应该先调用同步初始化函数
	if(this->m_uUnVisibleNPCEndIndex >= this->m_uVisibleNPCEndIndex && this->m_uUnVisibleNPCEndIndex < GLOBAL_NONPLAYER_ARRAY_MAX_SIZE)
	{
		this->m_pNPCArray[this->m_uUnVisibleNPCEndIndex] = pNPC;
		++this->m_uUnVisibleNPCEndIndex;
		return true;
	}
	else
	{	
		GE_EXC<<" over flow in GlobalAreaDataArray::InsertUnVisibleNPC"<<GE_END;
		return false;
	}
}

// 插入一个区域的数据到缓存中
// insertType：需要插入的数据类型
void GlobalAreaDataArray::InsertVisableArea(Area& area, InsertAreaDataType insertType)
{

	this->m_pTempRoleList = area.GetRoleList();
	if (NULL != this->m_pTempRoleList)
	{
		this->m_rml_iter = m_pTempRoleList->begin();
		for (; this->m_rml_iter != this->m_pTempRoleList->end(); ++this->m_rml_iter)
		{
			// 取一个区域的全部玩家，都放到数组缓存中
			if(!this->InsertVisiblePlayer(&*this->m_rml_iter))
			{
				break;
			}
		}
	}

	this->m_pTempNPCList = area.GetNPCList();
	if (NULL != this->m_pTempNPCList)
	{
		this->m_nml_iter = m_pTempNPCList->begin();
		for (; this->m_nml_iter != this->m_pTempNPCList->end(); ++this->m_nml_iter)
		{
			// 取一个区域的全部NPC，都放到数组缓存中
			if(!this->InsertVisibleNPC(&*this->m_nml_iter))
			{
				break;
			}
		}
	}
}

void GlobalAreaDataArray::InsertUnVisableArea(Area& area, InsertAreaDataType insertType )
{
	this->m_pTempRoleList = area.GetRoleList();
	if (NULL != this->m_pTempRoleList)
	{
		this->m_rml_iter = m_pTempRoleList->begin();
		for (; this->m_rml_iter != this->m_pTempRoleList->end(); ++this->m_rml_iter)
		{
			// 取一个区域的全部玩家，都放到数组缓存中
			if(!this->InsertUnVisiblePlayer(&*this->m_rml_iter))
			{
				break;
			}
		}
	}

	this->m_pTempNPCList = area.GetNPCList();
	if (NULL != this->m_pTempNPCList)
	{
		this->m_nml_iter = m_pTempNPCList->begin();
		for (; this->m_nml_iter != this->m_pTempNPCList->end(); ++this->m_nml_iter)
		{
			// 取一个区域的全部NPC，都放到数组缓存中
			if(!this->InsertUnVisibleNPC(&*this->m_nml_iter))
			{
				break;
			}
		}
	}
}
//////////////////////////////////////////////////////////////////////////
//AreaMap
//////////////////////////////////////////////////////////////////////////
AreaMap::AreaMap( MapTemplate* pMT, GE::Uint8 uAreaSize, bool bCanSeeOther)
	: m_pMapTemplate(pMT)
	, m_uAreaSize(uAreaSize)//区域边长格子数
	, m_uTotalPlayer(0)
	, m_uTotalNPC(0)
	, m_bCanSeeOther(bCanSeeOther)
{
	//计算边长(格子边长 * 一个区域边长格子数量)
	this->m_uAreaLength = pMT->XPix() * uAreaSize;


	//计算可以组成的区域
	this->m_uAreaWidthNum = pMT->Width() / uAreaSize;
	if ( pMT->Width() % uAreaSize > 0)
	{
		//多余的格子组成一个区域
		++this->m_uAreaWidthNum;
	}

	this->m_uAreaHightNum = pMT->Hight() / uAreaSize;
	if (pMT->Hight() % uAreaSize > 0)
	{
		//多余的格子组成一个区域
		++this->m_uAreaHightNum;
	}
	//总的区域数
	this->m_uTotalArea = this->m_uAreaWidthNum * this->m_uAreaHightNum;

	//区域数组
	this->m_pAreaArray = new Area[this->m_uTotalArea];
}

AreaMap::~AreaMap()
{
	delete [] m_pAreaArray;
}

GE::Uint8 AreaMap::GridProperty( GE::Uint16 uIndex )
{
	return this->m_pMapTemplate->Property(uIndex);
}

GE::Uint8 AreaMap::GridProperty( GE::Uint16 uX, GE::Uint16 uY )
{
	GE::Uint16 index = POS_2_GRID_INDEX(uX, uY, return 0);
	return this->m_pMapTemplate->Property(index);
}

GE::Uint16 AreaMap::Pos_2_Area_Index( GE::Uint16 uX, GE::Uint16 uY )
{
	//下标 = Y / 区域边长(像素) * 横向区域数 + X / 区域边长
	//从0开始
	return (uY / this->m_uAreaLength) * this->m_uAreaWidthNum + (uX / this->m_uAreaLength);
}


bool AreaMap::JoinRole_S( Role* pRole, GE::Uint16& uX, GE::Uint16& uY )
{
	if (this->JoinRole(pRole, uX, uY))
	{
		return true;
	}
	else
	{
		//传送到安全坐标
		uX = this->m_pMapTemplate->SafeX();
		uY = this->m_pMapTemplate->SafeY();
		return this->JoinRole(pRole, uX, uY);
	}
}

//内部方法
bool AreaMap::JoinRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
	GE::Uint16 uAreaIndex = POS_2_AREA_INDEX(uX, uY, GE_EXC<<"JoinRole, POS_2_AREA_INDEX error when on AreaMap("<<this->MapID()<<") (uX, uY)=("<<uX<<","<<uY<<")"<<GE_END; return false);
	GE::Uint16 uGridIndex = POS_2_GRID_INDEX(uX, uY, return false;);
	
	if (!AreaIndex_Vaile(uAreaIndex))
	{
		GE_EXC<<"JoinRole, uAreaIndex("<<uAreaIndex<<") error mapId, x y "<<this->MapID()<<uX<<uY<<GE_END;
		return false;
	}

	Area& area = this->m_pAreaArray[uAreaIndex];

	if (this->GridProperty(uGridIndex) == 0 && pRole->IsFlying() == false)
	{
		//尝试寻找一个可走的格子
		return false;
	}
	else
	{
		pRole->SetPos(uX, uY);
		pRole->ClearTargerPos();
		area.JoinPlayer(pRole);
		
		if (this->m_bCanSeeOther)
		{
			// 可视把需要迭代的玩家放到全局缓存数组中，等待迭代
			this->FindVisibleRect(uAreaIndex);
		}
		++this->m_uTotalPlayer;	//计算玩家数量
		return true;
	}
}

GE::Uint8 AreaMap::MoveRole( Role* pRole, GE::Uint16 uX, GE::Uint16 uY )
{
		// 目标位置
	GE::Uint16 index = POS_2_AREA_INDEX(uX, uY, return enCanNotMove);
	GE::Uint16 uGridIndex = POS_2_GRID_INDEX(uX, uY, return enCanNotMove;);

	//不可走格子，或者玩家不是飞行状态
	if (this->GridProperty(uGridIndex) == 0 && pRole->IsFlying() == false)
	{
		return enCanNotMove;//直接不给移动
	}

	// 玩家原来位置
	GE::Uint16 srcindex = POS_2_AREA_INDEX(pRole->GetPosX(), pRole->GetPosY(), return enCanNotMove);
	if(index == srcindex)
	{
		//没有走出当期的区域，不用同步其他人
		pRole->SetPos(uX, uY);
		return enMoveNotIterOther;
	}

	// 区域对象
	Area& area = this->m_pAreaArray[index];
	Area& src_area = this->m_pAreaArray[srcindex];

	pRole->SetPos(uX, uY);
	// 原来的区域把玩家移除
	src_area.LeavePlayer(pRole);
	// 加入新的区域内部
	area.JoinPlayer(pRole);
	
	if (this->m_bCanSeeOther)
	{
		// 迭代移动中的视野变化玩家
		this->FindByMove(srcindex, index);
	}
	return enMoveIter;
}

bool AreaMap::LeaveRole( Role* pRole )
{
	GE::Uint16 uAreaIndex = POS_2_AREA_INDEX(pRole->GetPosX(), pRole->GetPosY(), return false);
	Area& area = this->m_pAreaArray[uAreaIndex];
	
	area.LeavePlayer(pRole);
	if (this->m_bCanSeeOther)
	{
		//找出这个玩家附近九宫格的所有玩家，告诉他们这个玩家消失了
		this->FindVisibleRect(uAreaIndex);
	}
	--this->m_uTotalPlayer;
	return true;
}


bool AreaMap::JoinNPC( NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY )
{
	GE::Uint16 uAreaIndex = POS_2_AREA_INDEX(uX, uY, GE_EXC<<"JoinNPC, POS_2_AREA_INDEX error when on AreaMap("<<this->MapID()<<") (uX, uY)=("<<uX<<","<<uY<<")"<<GE_END; return false);
	Area& area = this->m_pAreaArray[uAreaIndex];

	pNPC->SetPos(uX, uY);
	area.JoinNPC(pNPC);
	// 可视把需要迭代的pNPC放到全局缓存数组中，等待迭代
	this->FindVisibleRect(uAreaIndex);
	++this->m_uTotalNPC;	//计算数量
	return true;
	
}


bool AreaMap::LeaveNPC( NPC* pNPC )
{
	GE::Uint16 uAreaIndex = POS_2_AREA_INDEX(pNPC->GetPosX(), pNPC->GetPosY(), return false);
	Area& area = this->m_pAreaArray[uAreaIndex];

	area.LeaveNPC(pNPC);
	//找出这个玩家附近九宫格的所有玩家，告诉他们这个玩家,pNPC消失了
	this->FindVisibleRect(uAreaIndex);
	--this->m_uTotalNPC;
	return true;
}

//////////////////////////////////////////////////////////////////////////
//逻辑计算相关
//////////////////////////////////////////////////////////////////////////
//

void AreaMap::FindVisibleRect(GE::Uint16 uX, GE::Uint16 uY)
{
	GE::Uint16 index = POS_2_AREA_INDEX(uX, uY, return);
	this->FindVisibleRect(index);
}


void AreaMap::FindVisibleRect( GE::Uint16 uAreaIndex, InsertAreaDataType dataType, GE::Uint16 uRectSize)
{
	//计算当期index所处的行列 从1开始
	GE::Int16 lines = uAreaIndex / this->m_uAreaWidthNum + 1;
	GE::Int16 rows = uAreaIndex - ((lines - 1) * this->m_uAreaWidthNum) + 1;

	GlobalAreaDataArray::Instance()->Clear();
	if(uRectSize == 0)
	{
		// 把这个矩形中的所有区域对象插入待迭代的数组
		this->InsertVisibleRect(this->BeginLines(lines), this->EndLines(lines), this->BeginRows(rows), this->EndRows(rows), dataType);
	}
	else
	{
		// 把这个矩形中的网格插入数组
		this->InsertVisibleRect(this->BeginLines(lines, uRectSize), this->EndLines(lines, uRectSize), this->BeginRows(rows, uRectSize), this->EndRows(rows, uRectSize), dataType);
	}
}

void AreaMap::FindUnVisibleRect( GE::Uint16 uAreaIndex )
{
	//计算当期index所处的行列 从1开始
	GE::Int16 lines = uAreaIndex / this->m_uAreaWidthNum + 1;
	GE::Int16 rows = uAreaIndex - ((lines - 1) * this->m_uAreaWidthNum) + 1;

	GlobalAreaDataArray::Instance()->Clear();
	// 把这个矩形中的网格插入数组
	GlobalAreaDataArray::Instance()->InitUnVisibleArea();
	this->InsertUnVisibleRect(this->BeginLines(lines), this->EndLines(lines), this->BeginRows(rows), this->EndRows(rows));
}

// 矩形迭代，移动玩家
// 枚举所有的移动类型
// uSrcAreaIndex 从0开始
void AreaMap::FindByMove( GE::Uint16 uSrcAreaIndex, GE::Uint16 uDesAreaIndex )
{
	GlobalAreaDataArray::Instance()->Clear();

	//原来的区域所在的行列(从1开始)
	GE::Int16 SrcLines = uSrcAreaIndex / this->m_uAreaWidthNum + 1;
	GE::Int16 SrcRows = uSrcAreaIndex - ((SrcLines - 1) * this->m_uAreaWidthNum) + 1;

	//目标区域所在的行列
	GE::Int16 DesLines = uDesAreaIndex / this->m_uAreaWidthNum + 1;
	GE::Int16 DesRows = uDesAreaIndex - ((DesLines - 1) * this->m_uAreaWidthNum) + 1;

	// 原来区域为中心的九宫格开始行
	GE::Int16 srcLinesBegin = this->BeginLines(SrcLines);
	GE::Int16 srcLinesEnd = this->EndLines(SrcLines);
	//结束列
	GE::Int16 srcRowsBegin = this->BeginRows(SrcRows);
	GE::Int16 srcRowsEnd = this->EndRows(SrcRows);

	// 目标区域为中心的九宫格开始行
	GE::Int16 desLinesBegin = this->BeginLines(DesLines);
	GE::Int16 desLinesEnd = this->EndLines(DesLines);
	//结束列
	GE::Int16 desRowsBegin = this->BeginRows(DesRows);
	GE::Int16 desRowsEnd = this->EndRows(DesRows);

	// 重叠范围计算
	GE::Int16 lineDistance = SrcLines - DesLines;		//行距
	GE::Int16 rowDistance = SrcRows - DesRows;			//列距

	if((abs(lineDistance) > AREA_VISIABLE_SIZE) || (abs(rowDistance) > AREA_VISIABLE_SIZE))
	{
		// 不重叠,跨区域移动,计算两个九宫格
		this->InsertVisibleRect(desLinesBegin, desLinesEnd, desRowsBegin, desRowsEnd);
		GlobalAreaDataArray::Instance()->InitUnVisibleArea();
		this->InsertUnVisibleRect(srcLinesBegin, srcLinesEnd, srcRowsBegin, srcRowsEnd);
		return;
	}

	if(lineDistance == 0)	// 行距差值为0， 则为左右移动，计算左中右3个矩形
	{
		if(rowDistance == 0)
		{
			// 没有移动
			return;
		}
		else if(rowDistance < 0)// 右移动
		{
			if(srcRowsEnd < this->m_uAreaWidthNum)
			{
				this->InsertVisibleRect(srcLinesBegin, srcLinesEnd, srcRowsEnd + 1, desRowsEnd);
			}
			GlobalAreaDataArray::Instance()->InitUnVisibleArea();
			this->InsertUnVisibleRect(srcLinesBegin, srcLinesEnd, srcRowsBegin, desRowsBegin - 1);
		}
		else					// 左移动
		{
			if(srcRowsBegin > 1)
			{
				this->InsertVisibleRect(srcLinesBegin, srcLinesEnd, desRowsBegin, srcRowsBegin - 1);
			}
			GlobalAreaDataArray::Instance()->InitUnVisibleArea();
			this->InsertUnVisibleRect(srcLinesBegin, srcLinesEnd, desRowsEnd + 1, srcRowsEnd);
		}
	}
	else
	{
		//行距不是0

		if (rowDistance == 0)	// 列距是0，则上下移动,计算上中下3个矩形
		{
			if(lineDistance < 0)	// 下移动
			{
				if(srcLinesEnd < this->m_uAreaHightNum)
				{
					this->InsertVisibleRect(srcLinesEnd + 1, desLinesEnd, srcRowsBegin, srcRowsEnd);
				}
				GlobalAreaDataArray::Instance()->InitUnVisibleArea();
				this->InsertUnVisibleRect(srcLinesBegin, desLinesBegin - 1, srcRowsBegin, srcRowsEnd);
			}
			else		// 上移动
			{
				if(srcLinesBegin > 1)
				{
					this->InsertVisibleRect(desLinesBegin, srcLinesBegin - 1, srcRowsBegin, srcRowsEnd);
				}
				GlobalAreaDataArray::Instance()->InitUnVisibleArea();
				this->InsertUnVisibleRect(desLinesEnd + 1, srcLinesEnd, srcRowsBegin, srcRowsEnd);
			}
		}
		else	//斜线移动，对角移动，5个矩形
		{
			if(lineDistance < 0)
			{
				if(rowDistance < 0)	//右下
				{
					// 横切
					if(srcRowsEnd < this->m_uAreaWidthNum)
					{
						this->InsertVisibleRect(desLinesBegin, srcLinesEnd, srcRowsEnd + 1, desRowsEnd);
					}
					if(srcLinesEnd < this->m_uAreaHightNum)
					{
						this->InsertVisibleRect(srcLinesEnd + 1, desLinesEnd, desRowsBegin, desRowsEnd);
					}
					GlobalAreaDataArray::Instance()->InitUnVisibleArea();
					this->InsertUnVisibleRect(srcLinesBegin, desLinesBegin - 1, srcRowsBegin, srcRowsEnd);
					this->InsertUnVisibleRect(desLinesBegin, srcLinesEnd, srcRowsBegin, desRowsBegin - 1);
				}
				else				//左下
				{
					if(srcRowsBegin > 1)
					{
						this->InsertVisibleRect(desLinesBegin, srcLinesEnd, desRowsBegin, srcRowsBegin - 1);
					}
					if(srcLinesEnd < this->m_uAreaHightNum)
					{
						this->InsertVisibleRect(srcLinesEnd + 1, desLinesEnd, desRowsBegin, desRowsEnd);
					}
					GlobalAreaDataArray::Instance()->InitUnVisibleArea();
					this->InsertUnVisibleRect(srcLinesBegin, desLinesBegin - 1, srcRowsBegin, srcRowsEnd);	//相同
					this->InsertUnVisibleRect(desLinesBegin, srcLinesEnd, desRowsEnd + 1, srcRowsEnd);
				}
			}
			else
			{
				if(rowDistance < 0)		// 右上
				{
					if(srcLinesBegin > 1)
					{
						this->InsertVisibleRect(desLinesBegin, srcLinesBegin - 1, desRowsBegin, desRowsEnd);
					}
					if(srcRowsEnd < this->m_uAreaWidthNum)
					{
						this->InsertVisibleRect(srcLinesBegin, desLinesEnd, srcRowsEnd + 1, desRowsEnd);
					}
					GlobalAreaDataArray::Instance()->InitUnVisibleArea();
					this->InsertUnVisibleRect(srcLinesBegin, desLinesEnd, srcRowsBegin, desRowsBegin - 1);
					this->InsertUnVisibleRect(desLinesEnd + 1, srcLinesEnd, srcRowsBegin, srcRowsEnd);
				}
				else					//左上
				{
					if(srcLinesBegin > 1)
					{
						this->InsertVisibleRect(desLinesBegin, srcLinesBegin - 1, desRowsBegin, desRowsEnd);
					}
					if(srcRowsBegin > 1)
					{
						this->InsertVisibleRect(srcLinesBegin, desLinesEnd, desRowsBegin, srcRowsBegin - 1);
					}
					GlobalAreaDataArray::Instance()->InitUnVisibleArea();
					this->InsertUnVisibleRect(srcLinesBegin, desLinesEnd, desRowsEnd + 1, srcRowsEnd);
					this->InsertUnVisibleRect(desLinesEnd + 1, srcLinesEnd, srcRowsBegin, srcRowsEnd);
				}
			}
		}
	}
}


void AreaMap::InsertVisibleRect( GE::Int16 linesBegin, GE::Int16 linesEnd, GE::Int16 rowsBegin, GE::Int16 rowsEnd, InsertAreaDataType insertType)
{
	GE::Int16 rowsNum = rowsEnd - rowsBegin;
	for (GE::Int16 i = linesBegin; i <= linesEnd; ++i)
	{
		GE::Uint32 uStartIndex = (i - 1) * this->m_uAreaWidthNum + rowsBegin - 1;
		for (GE::Int16 j = 0; j <= rowsNum; ++j)
		{
			// 把格子内的数据放到数组
			GlobalAreaDataArray::Instance()->InsertVisableArea(this->m_pAreaArray[uStartIndex + j], insertType);
		}
	}
}

void AreaMap::InsertUnVisibleRect( GE::Int16 linesBegin, GE::Int16 linesEnd, GE::Int16 rowsBegin, GE::Int16 rowsEnd )
{
	GE::Int16 rowsNum = rowsEnd - rowsBegin;
	for (GE::Int16 i = linesBegin; i <= linesEnd; ++i)
	{
		GE::Uint32 uStartIndex = (i - 1) * this->m_uAreaWidthNum + rowsBegin - 1;
		for (GE::Int16 j = 0; j <= rowsNum; ++j)
		{
			// 把格子内的数据放到数组
			GlobalAreaDataArray::Instance()->InsertUnVisableArea(this->m_pAreaArray[uStartIndex + j]);
		}
	}
}

//////////////////////////////////////////////////////////////////////////
//迭代相关
//////////////////////////////////////////////////////////////////////////
// 新的可视玩家(看到出现)
void AreaMap::BeginIteratorNewVisiblePlayer()
{
	GlobalAreaDataArray::Instance()->BeginIteratorVisiblePlayer();
}

Role* AreaMap::GetNextNewVisiblePlayer()
{
	return GlobalAreaDataArray::Instance()->GetNextVisiblePlayer();
}

// 新的不可视玩家，这些玩家会看到触发迭代的玩家在他们视野内消失
void AreaMap::BeginIteratorNewUnvisiblePlayer()
{
	GlobalAreaDataArray::Instance()->BeginIteratorUnVisiblePlayer();
}

Role* AreaMap::GetNextNewUnvisiblePlayer()
{
	return GlobalAreaDataArray::Instance()->GetNextUnVisiblePlayer();
}

//迭代一个区域的玩家(九宫格)
void AreaMap::BeginIteratorRectPlayer( GE::Uint16 uX, GE::Uint16 uY)
{
	GE::Uint16 index = POS_2_AREA_INDEX(uX, uY, return);
	this->FindVisibleRect(index, enPlayer, AREA_VISIABLE_SIZE);
	GlobalAreaDataArray::Instance()->BeginIteratorVisiblePlayer();
}

Role* AreaMap::GetNextRectPlayer()
{
	return GlobalAreaDataArray::Instance()->GetNextVisiblePlayer();
}




// 新的可视NPC(看到出现)
void AreaMap::BeginIteratorNewVisibleNPC()
{
	GlobalAreaDataArray::Instance()->BeginIteratorVisibleNPC();
}

NPC* AreaMap::GetNextNewVisibleNPC()
{
	return GlobalAreaDataArray::Instance()->GetNextVisibleNPC();
}

// 新的不可视玩家，这些玩家会看到触发迭代的玩家在他们视野内消失
void AreaMap::BeginIteratorNewUnvisibleNPC()
{
	GlobalAreaDataArray::Instance()->BeginIteratorUnVisibleNPC();
}

NPC* AreaMap::GetNextNewUnvisibleNPC()
{
	return GlobalAreaDataArray::Instance()->GetNextUnVisibleNPC();
}

//迭代一个区域的玩家
void AreaMap::BeginIteratorRectNPC( GE::Uint16 uX, GE::Uint16 uY, GE::Uint16 uRectSize)
{
	GE::Uint16 index = POS_2_AREA_INDEX(uX, uY, return);
	// 可改进此处
	this->FindVisibleRect(index, enPlayer, uRectSize);

	GlobalAreaDataArray::Instance()->BeginIteratorVisibleNPC();
}

NPC* AreaMap::GetNextRectNPC()
{
	return GlobalAreaDataArray::Instance()->GetNextVisibleNPC();
}
//////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////
// 区域迭代查找辅助函数
//
GE::Int16 AreaMap::BeginLines(GE::Int16 lines, GE::Uint16 uRectSize)
{
	if(lines > uRectSize)
	{
		return lines - uRectSize + 1;
	}
	else
	{
		//开始行超出
		return 1;
	}
}
GE::Int16 AreaMap::EndLines(GE::Int16 lines, GE::Uint16 uRectSize)
{
	if (this->m_uAreaHightNum - lines >= uRectSize)
	{
		//没有超出地图范围
		return lines + uRectSize - 1;
	}
	else
	{
		//已经是最底下的一行了,取最大行
		return this->m_uAreaHightNum;
	}
}

GE::Int16 AreaMap::BeginRows(GE::Int16 rows, GE::Uint16 uRectSize)
{
	if (rows > uRectSize)
	{
		return rows - uRectSize + 1;
	}
	else
	{
		return 1;
	}
}

GE::Int16 AreaMap::EndRows(GE::Int16 rows, GE::Uint16 uRectSize)
{
	if (this->m_uAreaWidthNum - rows >= uRectSize)
	{
		return rows + uRectSize - 1;
	}
	else
	{
		return this->m_uAreaWidthNum;
	}
}

GE::Uint16 AreaMap::MapID()
{
	return m_pMapTemplate->MapId();
}

void AreaMap::SetCanSeeOther( bool b )
{
	this->m_bCanSeeOther = b;
}


//////////////////////////////////////////////////////////////////////////

