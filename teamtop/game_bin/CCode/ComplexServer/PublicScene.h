/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma 
#include <boost/unordered_map.hpp>
#include <boost/unordered_set.hpp>
#include "../GameEngine/GameEngine.h"
#include "SceneBase.h"


class Role;
class NPC;
class AreaMap;
class MapTemplate;

class PublicScene
	: public SceneBase
{
public:
	typedef boost::unordered_map<GE::Uint32, NPC*>						SceneNPCMap;
	typedef boost::unordered_map<GE::Uint64, Role*>						SceneRoleMap;
	typedef boost::unordered_set<NPC*>									BroadcastNPCSet;

public:
	PublicScene(GE::Uint32 uSceneID, const std::string& sSceneName, MapTemplate* pMT, GE::Uint8 uAreaSize, bool bIsSaveData = false, bool bCanSeeOther = false);
	~PublicScene();

public:
	virtual SceneType			GetSceneType() {return enScenePublic;}
	virtual void				SaveRoleSceneData(Role* pRole);
	virtual void				CallPerSecond();
	void						AfterCreate();
	SceneRoleMap&				GetSceneRoleMap() {return m_sceneRoleMap;}
	virtual bool				IsFlyingPos(Role *pRole);
	virtual bool				IsSave(){return m_bIsSave;}
	SceneNPCMap&				GetSceneNPCMap() {return m_sceneNPCMap;}
public:
	virtual NPC*				CreateNPC(GE::Uint16 uTypeID, GE::Uint16 uX, GE::Uint16 uY, GE::Uint8 uDirection, bool bBroadCast, PyObject* py_BorrowRef);
	virtual void				DestroyNPC(NPC *pNPC);
	virtual void				DestroyNPC(GE::Uint32 uNPCID);
	virtual void				OnClickNPC(Role* pRole, GE::Uint32 uNPCID);
	NPC*						SearchNPC( GE::Uint32 uNPCID );

public:
	bool						JoinRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	void						LeaveRole(Role* pRole);
	bool						MoveRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	bool						JumpRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	bool						JoinNPC(NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY);
	void						LeaveNPC(NPC* pNPC);
	bool						JumpNPC(NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY);

public:
	void						RestoreRole(Role* pRole);

	virtual void				SendToRect(GE::Uint16 uX, GE::Uint16 uY, MsgBase* pMsg);
	virtual void				SendToAllRole(MsgBase* pMsg);

	void						SetCanSeeOther(bool b);

	virtual bool				CanSeeOther() {return m_bCanSeeOther;}
	void						BroadToRect(Role* pAroundTheRole);
	void						BroadMsg();										//给场景中的所有角色发消息
	Role*						SearchRole(GE::Uint64 uRoleID);					//查找一个角色


	void						SetMoveTimeJap(GE::Int16 jap){ m_uMovingTimeJap = jap; }
	void						SetMoveDistanceJap(GE::Int16 jap) { m_uMoveDistanceJap = jap; }

private:
	void						InsertRole(Role* pRole);						//加入一个角色到角色Map
	void						RemoveRole(Role* pRole);						//从角色Map中删除一个角色
	
	void						InsertNPC(NPC* pNPC);							//加入一个NPC到NPC Map
	void						RemoveNPC(NPC* pNPC);							//从NPC Map中删除一个角色

	MsgBase*					GetBroadcastNPCMsg();							//获取广播NPC消息
	void						BroadcastNPC();									//广播给全场景的人
	void						BroadcastNPCToRole(Role* pRole);				//广播所有需要广播的NPC给一个刚刚进入场景的玩家

	void						AfterJoinRole(Role* pRole);
	void						BeforeLeaveRole(Role* pRole);
	void						AfterRestoreRole(Role* pRole);

	bool						CheckPosX(Role* pRole, GE::Uint16 uX);
	bool						CheckPosY(Role* pRole, GE::Uint16 uY);
	bool						IsIgnoreCheckMoveDistanceJap(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);

public:
	void						LoadAfterCreateFun(PyObject* pyFun_BorrowRef);
	void						LoadAfterJoinRole(PyObject* pyFun_BorrowRef);
	void						LoadBeforeLeaveRole(PyObject* pyFun_BorrowRef);
	void						LoadRestoreRole(PyObject* pyFun_BorrowRef);

private:
	bool						m_bIsSave;						//是否保存玩在这个场景内的坐标与场景ID
	bool						m_bCanSeeOther;					//能否看到其他
	AreaMap*					m_pAreaMap;						//区域地图指针

	bool						m_bBroadcastNPCChange;			//广播NPC是否改变
	bool						m_bNeedBroadcast;				//是否需要广播场景NPC
	std::string					m_pBroadcastNPCMsg;				//广播NPC消息缓存
	SceneNPCMap					m_sceneNPCMap;					//当前场景NPC Map
	SceneRoleMap				m_sceneRoleMap;					//当前场景角色Map
	BroadcastNPCSet				m_sceneBroadcastNPCSet;			//进场景就需要广播的NPC


	GEPython::Function			m_pyAfterCreate;				//场景创建时调用的函数
	GEPython::Function			m_pyAfterJoinRole;				//玩家进入场景前调用的函数
	GEPython::Function			m_pyBeforeLevelRole;			//玩家退出场景前调用的函数
	GEPython::Function			m_pyRestoreRole;				//玩家恢复场景前调用的函数

	//处理很多人的场景时，可以通关忽视移动来达到减少服务器同步消息量
	GE::Uint32					m_uMovingTimeJap;				//移动忽视时间
	GE::Uint16					m_uMoveDistanceJap;				//移动忽视距离
};

