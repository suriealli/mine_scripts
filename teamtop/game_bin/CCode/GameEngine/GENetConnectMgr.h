/************************************************************************
网络连接管理
************************************************************************/
#pragma once
#include <vector>
#include <boost/unordered_map.hpp>
#include "GENetConnect.h"
#include "GEIndex.h"

class GENetConnectMgr
{
	GE_DISABLE_BOJ_CPY(GENetConnectMgr);
	typedef GENetConnect*														ConnectPtr;
	typedef boost::unordered_map<GE::Uint32, GENetConnect::ConnectSharedPtr>	HoldMap;
	typedef std::vector<boost::mutex*>											MutexVector;
public:
	GENetConnectMgr(GE::Uint32 uMaxConnect);
	~GENetConnectMgr(void);

public:
	bool				AddConnect(GENetConnect::ConnectSharedPtr& spConnect, GE::Uint32& uID);	//增加一个连接
	bool				DelConnect(GE::Uint32 uID);												//删除一个连接
	bool				HasConnect(GE::Uint32 uID);												//是否有某个连接
	GENetConnect*		FindConnect(GE::Uint32 uID);											//查找一个连接（通过ID）
	GENetConnect*		FindConnectForHasData(GE::Uint32 uID);									//查找一个连接（为了发送数据）
	GENetConnect*		NextConnect();															//获取下一个连接（内部循环迭代，增删连接迭代依然有效）
	GE::Uint32			ConnectCnt() {return m_IndexMgr.Size();}								//连接的个数
	void				Lock(GE::Uint32 uID);													//锁住某个连接
	void				Unlock(GE::Uint32 uID);													//释放某个连接
	bool				DriverAsyncSendBlock();													//驱动所以的连接异步发送消息，返回是否有连接发送的数据量很大
	void				DelAllConnect();														//删除所有的连接

private:
	GEIndex				m_IndexMgr;			//索引ID分配器
	ConnectPtr*			m_pDataArr;			//连接数组
	bool*				m_pHasData;			//是否有未发送的数据
	HoldMap				m_pDataMap;			//用来hold智能指针的map
	MutexVector			m_pMutexVector;		//用来管理每个连接的锁（多锁，减少碰撞）
};

