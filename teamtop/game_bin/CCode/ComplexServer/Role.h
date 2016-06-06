/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include <boost/unordered_map.hpp>
#include "RoleData.h"
#include "SceneMgr.h"
#include "MessageDefine.h"
#include "AreaDefine.h"

class SceneBase;

class Role
	: public RoleData
{
	GE_DISABLE_BOJ_CPY(Role);
public:
	typedef boost::unordered_map<GE::Uint16, GE::Uint32>			MessageMap;

	Role(GE::Uint64 uRoleID, const std::string& sRoleName, const std::string& sOpenID, GE::Uint64 uClientKey, GE::Uint32 uObjID, GE::Uint32 uCommandSize, GE::Uint32 uCommandIndex);
	~Role();

/************************************************************************
对应的Python对象
************************************************************************/
public:
	GEPython::Object&				GetPySelf() {return m_pySelf;}					//获取对应的Python对象
private:
	GEPython::Object				m_pySelf;

/************************************************************************
对应的侵入式链表
************************************************************************/
public:
	bool							IsLink(){return member_hook_.is_linked();}		//是否在链表中
	void							UnLink(){member_hook_.unlink();}				//脱离链表
	ListMemberHook					member_hook_;									//链表钩子

/************************************************************************
1.和客户端和消息收发
2.每秒Update
3.踢掉的相关逻辑
************************************************************************/
public:
	bool							IsKick() {return m_pySelf.IsNone();}											//角色是否被踢了
	void							Kick();																			//踢掉角色（同时踢客户端，保存角色数，无原因）
	void							Kick(PyObject* isSave_BorrowRef, PyObject* res_BorrowRef);						//踢掉角色（isSave_BorrowRef, True 保存角色数据，False 不保存， res_BorrowRef：原因,如果为Py_True则不踢客户端）
	void							Save();																			//保存角色
	GE::Uint64						GetClientKey() {return m_uClientKey;}											//获取对应的客户端Key
	GEPython::Object&				GetPyClientKey() {return m_pyClientKey;}										//获取对应的客户端Key（Python对象）
	void							CallPerSecond();																//每秒调用
	void							CallAfterNewMinute();															//当新的一分钟后调用
	void							CallAfterNewDay();																//当新的一天后调用
	void							ClearPerDay();																	//每日清理
	void							SendMsg(MsgBase* pMsg);															//发送一个消息
	void							SendPyMsg(GE::Uint16 uMsgType, PyObject* msg_BorrowRef);						//发送一个对象（消息体是Python对象）
	void							SendPyMsgAndBack(GE::Uint16 uMsgType, PyObject* msg_BorrowRef, GE::Uint32 uSec,
														PyObject* cbfun_BorrowRef,PyObject* regparam_BorrowRef);	//发送一个对象并等待回调
	void							BroadMsg();																		//发送一个广播消息给客户端
	void							CallBackFunction(GE::Uint32 uFunID, PyObject* arg_BorrowRef);					//触发一个客户端的回调函数
	void							OnCallBackFunction(MsgBase* pMsg);												//客户端触发服务器的回调函数

	GESmallTick&					Tick() {return m_Tick;}

	void							Lost();
	bool							IsLost(){ return this->m_uClientKey == MAX_UINT64;}
	bool							ReLogin(GE::Uint64 uClientKey);
private:
	GE::Uint64						m_uClientKey;
	GEPython::Object				m_pyClientKey;
	GESmallTick						m_Tick;


/************************************************************************
和场景相关的函数
************************************************************************/
public:
	GE::Uint32						GetObjID() {return m_uObjID;}													//获取全局ID
	void							OnMovePos(GE::Uint16 uX, GE::Uint16 uY);										//每隔一段时间向服务器同步自己坐标
	void							ToTargetPos(GE::Uint16 uX, GE::Uint16 uY);										//直线终点
	bool							CheckTargetPos(GE::Uint16 uX, GE::Uint16 uY);									//检查客户端发来的目的坐标
	bool							CheckMovePos(GE::Uint16 uX, GE::Uint16 uY);										//检查客户端发来的移动坐标
	void							ClearTargerPos();																//清理终点坐标
	void							SetPos(GE::Uint16 uX, GE::Uint16 uY);											//设置角色当前位置
	void							SetPosEx(GE::Uint16 uX, GE::Uint16 uY);											//设置角色当前位置

	void							SetTargrtPos(GE::Uint16 uX, GE::Uint16 uY);										//设置角色终点
	void							DoIdle(GE::Uint8 uCode = 0);														//将角色拉到服务器认为正确的坐标
	MsgBase*						GetTPosMsg() {return &m_TPosMsg;}
	MsgBase*						GetNPosMsg() {return &m_NPosMsg;}
	MsgBase*						GetPosMsg();
	
	SceneBase*						GetScene() {return m_pScene;}
	void							SetScene(SceneBase *pScene) {m_pScene = pScene;}
	GE::Uint32						GetSceneID() { return m_uSceneID;}
	void							SetSceneID(GE::Uint32 uSceneID) { m_uSceneID = uSceneID;}
	GE::Uint16						GetPosX() {return m_uX;}
	GE::Uint16						GetPosY() {return m_uY;}
	GE::Uint16						GetPosZ() {return m_uZ;}

	GE::Uint32						GetLastSceneID();		
	void							SetLastSceneID(GE::Uint32 uSceneID);
	GE::Uint16						GetLastPosX();
	GE::Uint16						GetLastPosY();
	void							SetLastPosX(GE::Uint16 uPosX);
	void							SetLastPosY(GE::Uint16 uPosY);
	void							SetPosZ(GE::Uint16 uPosZ) {m_uZ = uPosZ;}

	bool							IsFlyingPos();
	GE::Uint32						GetMovingTime() {return m_uLastMovingTime;}
	void							UpdateMovingTime(GE::Uint32 uNowTime){ m_uLastMovingTime = uNowTime;}
	bool							IsIgnoreCheckMovingTime(GE::Uint32 uTimeJap);

private:
	GE::Uint32						m_uObjID;
	GE::Uint32						m_uSceneID;
	GE::Uint32						m_uLastMovingTime;//上一次移动的时间点，用于移动频繁的时候忽视移动信息
	GE::Uint16						m_uX;
	GE::Uint16						m_uY;
	GE::Uint16						m_uZ;
	GE::Uint16						m_uTX;
	GE::Uint16						m_uTY;
	GE::Uint16						m_uHpTime;
	SceneBase*						m_pScene;
	MsgSyncRoleTargerPos			m_TPosMsg;		//目的坐标和当前坐标(移动中)
	MsgSyncRoleNowPos				m_NPosMsg;		//当前坐标(静止)

/************************************************************************
角色外观、版本
************************************************************************/
public:
	GE::Uint16						GetVersion1() {return m_uVersion1;}
	GE::Uint16						GetVersion2() {return m_uVersion2;}

	void							ChangeVersion1();
	void							ChangeVersion2();

	void							SetApperance(PyObject* key_BorrowRef, PyObject* value_BorrowRef);
	void							SetAppStatus(GE::Uint16 uValue);

	MsgBase*						GetRoleSyncAppearanceMsg();
	MsgBase*						GetRoleSyncAppStatusMsg();
	
	PyObject*						GetRoleSyncAppearanceObj();

private:
	GEPython::Dict					m_ApperanceDict;	//外观字典
	std::string						m_ApperanceMsg;		//外观打包好的消息

	GE::Uint16						m_uVersion1;		//版本号
	GE::Uint16						m_uVersion2;		//版本号
	bool							m_bAppChangeFlag1;	//是否改变了外观
	bool							m_bAppChangeFlag2;

	MsgSyncRoleAppStatus			m_AppStatusMsg;
	
/************************************************************************
角色聊天信息
************************************************************************/
public:
	void							SetChatInfo(PyObject* key_BorrowRef, PyObject* value_BorrowRef);
	std::string&					GetRoleChatInfoMsg();
	void							SetCanChatTime(GE::Int32 nSecond);
	bool							CanChat();

private:
	GEPython::Dict					m_ChatInfoDict;
	std::string						m_ChatInfoMsg;
	bool							m_bChatInfoChange;

/************************************************************************
角色和逻辑相关的函数
************************************************************************/
public:
	void							SetFly(GE::Uint8 uCode);					//设置飞行状态
	bool							IsFlying();									//是否正在飞行状态
	void							SyncFlyState();
	bool							IsLockMove(){return m_bIsLockMove;}
	void							LockMove(){ m_bIsLockMove = true;}
	void							UnLockMove() { m_bIsLockMove = false;}

private:
	bool							m_bIsLockMove;								//是否禁止移动(转场景后锁定，通过客户端发送转场景成功来解锁)

/************************************************************************
角色属性
************************************************************************/
public:

	void							SetCareer(GE::Int32 uCareer);
	GE::Int32						GetCareer();


	void							SetNeedRecount(){m_bNeedRecount = true;}
	void							FinishRecount(){m_bNeedRecount = false;}
	void							CheckRecountProperty();
	bool							m_bNeedRecount;
/************************************************************************
角色体力
************************************************************************/
public:
	void							CountTiLi();

	GE::Int16						GetTiLi();
	void							SetTiLi(GE::Uint16 uValue);

	void							IncTiLi(GE::Uint16 uValue);
	void							DecTiLi(GE::Uint16 uValue);

/************************************************************************
角色消息统计
************************************************************************/
public:
	void							ClearMessage();
	void							SendOneMessage(GE::Uint16 uMsgType);
	void							RecvOneMessage(GE::Uint16 uMsgType);
	MessageMap&						GetSendMessage() {return this->m_SendMessageMap;}
	MessageMap&						GetRecvMessage() {return this->m_RecvMessageMap;}

private:
	MessageMap						m_SendMessageMap;
	MessageMap						m_RecvMessageMap;

/************************************************************************
角色移动速度
************************************************************************/
public:
	GE::Int16						GetNowSpeed();					//获取真正当前速度(优先取临时速度)(实际应用)
	//客户端每次移动速度（每秒移动3次， 修改为速度2倍）
	GE::Int16						GetClientSpeed() { return GetNowSpeed() * 2;}
	
	GE::Int16						GetTempSpeed();					//获取临时速度
	void							SetTempSpeed(GE::Uint16 uValue);//设置临时速度

	GE::Int16						GetMountSpeed();				//获取坐骑速度
	void							SetMountSpeed(GE::Uint16 uValue);//设置坐骑速度

	GE::Int16						GetMoveSpeed();					//获取实际移动速度(持久化)
	void							SetMoveSpeed(GE::Uint16 uValue);//设置移动速度

	GE::Int16						GetTempFly();					//获取临时速度
	void							SetTempFly(GE::Uint16 uValue);//设置临时速度
	
/************************************************************************
角色数据
************************************************************************/
public:
	void							SyncDataBase();
	void							SyncOK();

	void							SyncByReLogin();
	// Int64Array
	void							InitI64(PyObject* arg_BorrowRef);
	void							SyncI64();
	PyObject*						SeriI64_NewRef();
	GE::Int64						GetI64(GE::Uint16 uIdx);
	void							SetI64(GE::Uint16 uIdx, GE::Int64 val);
	void							IncI64(GE::Uint16 uIdx, GE::Int64 jap);
	void							DecI64(GE::Uint16 uIdx, GE::Int64 jap);
	// DisperseInt32 离散的I32
	void							InitDI32(PyObject* arg_BorrowRef);
	void							SyncDI32();
	PyObject*						SeriDI32_NewRef();
	GE::Int32						GetDI32(GE::Uint16 uIdx);
	GE::Int32&						GetDI32Ref(GE::Uint16 uIdx);
	void							SetDI32(GE::Uint16 uIdx, GE::Int32 val);
	void							IncDI32(GE::Uint16 uIdx, GE::Int32 jap);
	void							DecDI32(GE::Uint16 uIdx, GE::Int32 jap);
	// Int32
	void							InitI32(PyObject* arg_BorrowRef);
	void							SyncI32();
	PyObject*						SeriI32_NewRef();
	GE::Int32						GetI32(GE::Uint16 uIdx);
	void							SetI32(GE::Uint16 uIdx, GE::Int32 val);
	void							IncI32(GE::Uint16 uIdx, GE::Int32 jap);
	void							DecI32(GE::Uint16 uIdx, GE::Int32 jap);
	void							SyncI32(GE::Uint16 uIdx, GE::Int32 val);
	// Int16
	void							InitI16(PyObject* arg_BorrowRef);
	void							SyncI16();
	PyObject*						SeriI16_NewRef();
	GE::Int16						GetI16(GE::Uint16 uIdx);
	void							SetI16(GE::Uint16 uIdx, GE::Int16 val);
	void							IncI16(GE::Uint16 uIdx, GE::Int16 jap);
	void							DecI16(GE::Uint16 uIdx, GE::Int16 jap);
	// Int8
	void							InitI8(PyObject* arg_BorrowRef);
	void							SyncI8();
	PyObject*						SeriI8_NewRef();
	GE::Int8						GetI8(GE::Uint16 uIdx);
	void							SetI8(GE::Uint16 uIdx, GE::Int8 val);
	void							IncI8(GE::Uint16 uIdx, GE::Int8 jap);
	void							DecI8(GE::Uint16 uIdx, GE::Int8 jap);
	// DayInt8
	void							InitDI8(PyObject* arg_BorrowRef);
	void							SyncDI8();
	PyObject*						SeriDI8_NewRef();
	GE::Int8						GetDI8(GE::Uint16 uIdx);
	void							SetDI8(GE::Uint16 uIdx, GE::Int8 val);
	void							IncDI8(GE::Uint16 uIdx, GE::Int8 jap);
	void							DecDI8(GE::Uint16 uIdx, GE::Int8 jap);
	// Int1
	void							InitI1(PyObject* arg_BorrowRef);
	void							SyncI1();
	PyObject*						SeriI1_NewRef();
	bool							GetI1(GE::Uint16 uIdx);
	void							SetI1(GE::Uint16 uIdx, bool val);
	// DayInt1
	void							InitDI1(PyObject* arg_BorrowRef);
	void							SyncDI1();
	PyObject*						SeriDI1_NewRef();
	bool							GetDI1(GE::Uint16 uIdx);
	void							SetDI1(GE::Uint16 uIdx, bool val);
	// DynamicInt64
	void							InitDI64(PyObject* arg_BorrowRef);
	void							SyncDI64();
	PyObject*						SeriDI64_NewRef();
	GE::Int64						GetDI64(GE::Uint16 uIdx);
	void							SetDI64(GE::Uint16 uIdx, GE::Int64 val);
	void							IncDI64(GE::Uint16 uIdx, GE::Int64 jap);
	void							DecDI64(GE::Uint16 uIdx, GE::Int64 jap);
	// Obj
	void							InitObj(PyObject* arg_BorrowRef);
	PyObject*						SeriObj_NewRef();
	PyObject*						GetObj_NewRef(GE::Uint16 uIdx);
	PyObject*						GetObj_ReadOnly_NewRef(GE::Uint16 uIdx);
	void							SetObj(GE::Uint16 uIdx, PyObject* arg_BorrowRef);
	void							IncObVersion(GE::Uint16 uIdx);
	GE::Int32						GetObjVersion(GE::Uint16 uIdx);
	// ClientInt8
	void							InitCI8(PyObject* arg_BorrowRef);
	void							SyncCI8();
	PyObject*						SeriCI8_NewRef();
	GE::Int8						GetCI8(GE::Uint16 uIdx);
	void							SetCI8(GE::Uint16 uIdx, GE::Int8 val);
	// TempInt64(不保存到数据库，压缩发送网络消息)
	void							SyncTI64();
	GE::Int64						GetTI64(GE::Uint16 uIdx);
	void							SetTI64(GE::Uint16 uIdx, GE::Int64 val);
	void							IncTI64(GE::Uint16 uIdx, GE::Int64 jap);
	void							DecTI64(GE::Uint16 uIdx, GE::Int64 jap);
	// CD(cd数组)
	void							InitCD(PyObject* arg_BorrowRef);
	void							SyncCD();
	PyObject*						SeriCD_NewRef();
	GE::Int32						GetCD(GE::Uint16 uIdx);
	void							SetCD(GE::Uint16 uIdx, GE::Int32 val);
	// TempObj
	void							SetTempObj(GE::Uint16 uIdx, PyObject* obj_BorrowRef);
	PyObject*						GetTempObj_NewRef(GE::Uint16 uIdx);

private:
	GE::Int64						m_uAccumulateIncExp;
	GE::Int64						m_uAccumulateIncMoney;
	GE::Int64						m_uAccumulateDecMoney;
};

