/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma
#include <boost/unordered_map.hpp>
#include "../GameEngine/GameEngine.h"
#include "SceneBase.h"

// 副本场景,此类副本当人数为0时则自动销毁
class MirrorBase
	: public SceneBase
{
public:
	MirrorBase(GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName);
	~MirrorBase();

public:
	virtual bool					CanDestory() {return true;};
	// 是否为空
	virtual bool					IsEmpty() {return true;}
	// 获取场景类型
	virtual SceneType				GetSceneType(){return enMirrorBase;}
	// 地图类型
	virtual GE::Uint16				MapID(){return m_uMapID;}
	// 全局ID
	virtual GE::Uint32				GlobalID(){return m_uGlobalID;}
	// 销毁场景
	virtual void					Destroy() = 0;
	// 点击NPC
	virtual void					OnClickNPC(Role* pRole, GE::Uint32 uNPCID);

	virtual void					SendToRect(GE::Uint16 uX, GE::Uint16 uY, MsgBase* pMsg) = 0;

	//此场景是否可以看到其他单位
	virtual bool					CanSeeOther() {return false;}

public:
	virtual bool					JoinRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY) = 0;
	virtual void					LeaveRole(Role* pRole) = 0;

	//以下函数都没用了
	virtual bool					MoveRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY) {return true;}
	virtual bool					JumpRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY) {return true;}
	// 创建NPC
	virtual NPC*					CreateNPC(GE::Uint16 uTypeID, GE::Uint16 uX, GE::Uint16 uY, GE::Uint8 uDirection, bool bBroadCast, PyObject* py_BorrowRef) {return NULL;}
	virtual void					DestroyNPC(NPC *pNPC) { }
	virtual void					DestroyNPC(GE::Uint32 uNPCID) { }

	bool							JoinNPC(NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY) {return false;}
	void							LeaveNPC(NPC* pNPC) {}
	bool							JumpNPC(NPC* pNPC, GE::Uint16 uX, GE::Uint16 uY) {return false;}

protected:
	GE::Uint32						m_uGlobalID;	// 全局唯一ID
	GE::Uint16						m_uMapID;		// 地图ID
};

// 单幅副本场景,此类副本当人数为0时则自动关闭
class SingleMirrorScene
	: public MirrorBase
{
public:
	SingleMirrorScene(GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName);
	~SingleMirrorScene();

public:
	virtual bool					CanDestory();
	// 是否为空
	virtual bool					IsEmpty();
	// 获取场景类型
	virtual SceneType				GetSceneType(){return enSingleMirror;}
	// 销毁场景
	virtual void					Destroy();

	virtual void					SendToRect(GE::Uint16 uX, GE::Uint16 uY, MsgBase* pMsg) { };
	virtual bool					MoveRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	virtual bool					JoinRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	virtual bool					JumpRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	virtual void					LeaveRole(Role* pRole);
	void							BeforeLeaveRole(Role* pRole);
	void							LoadBeforeLeaveRole(PyObject* pyFun_BorrowRef);

	void							RestoreRole(Role* pRole);
private:
	Role*							m_pRole;
	GEPython::Function				m_pyBeforeLevelRole;			//玩家退出场景前调用的函数
};

// 多人副本场景,此类副本当人数为0时则自动关闭
class MultiMirrorScene
	: public MirrorBase
{
	typedef boost::unordered_map<GE::Uint64, Role*>		tyRoleMap;
public:
	MultiMirrorScene(GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName, bool bAliveTimeFlag = false);
	~MultiMirrorScene();

public:
	void							ReadyToDestroy(){ m_bAliveTimeFlag = false;}
	virtual bool					CanDestory();
	// 是否为空
	virtual bool					IsEmpty();
	// 获取场景类型
	virtual SceneType				GetSceneType(){return enMultiMirror;}
	// 销毁场景
	virtual void					Destroy();
	virtual bool					JoinRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	virtual void					LeaveRole(Role* pRole);
	virtual bool					MoveRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	virtual bool					JumpRole(Role* pRole, GE::Uint16 uX, GE::Uint16 uY);
	
	//玩家恢复场景
	void							RestoreRole(Role* pRole);

	// 查找角色
	Role*							SearchRole(GE::Uint64 uRoleID);
	// 发送消息给所有人
	virtual void					SendToAllRole(MsgBase* pMsg);
	virtual void					SendToRect(GE::Uint16 uX, GE::Uint16 uY, MsgBase* pMsg);

	//此场景是否可以看到其他单位
	virtual bool					CanSeeOther() {return true;}
	void							LoadBeforeLeaveRole(PyObject* pyFun_BorrowRef);

	void							BeforeLeaveRole(Role* pRole);

	// 点击NPC
	virtual void					OnClickNPC(Role* pRole, GE::Uint32 uNPCID);

private:
	tyRoleMap						m_RoleMap;

	GEPython::Function				m_pyAfterJoinRole;				//玩家进入场景后调用的函数
	GEPython::Function				m_pyBeforeLevelRole;			//玩家退出场景前调用的函数

	bool							m_bAliveTimeFlag;
};


