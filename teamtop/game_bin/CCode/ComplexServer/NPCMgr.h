/************************************************************************
我是UTF8编码文件
************************************************************************/
#pragma once
#include "../GameEngine/GameEngine.h"


class NPCTemplate;
class NPCConfigObj;
class NPC;
class Role;
class SceneBase;

//最大的配置NPC ID
#define MAX_CFG_NPC_ID		100000

class NPCMgr
	:public GEControlSingleton<NPCMgr>
{
	typedef boost::unordered_map<GE::Uint32, NPC*>						NPCMap;
	typedef boost::unordered_map<GE::Uint16, NPCTemplate*>				NPCTemplateMap;
	typedef boost::unordered_map<GE::Uint32, NPCConfigObj*>				NPCConfigObjMap;
public:
	NPCMgr();
	~NPCMgr();

public:
	// 载入Python数据
	void					LoadPyData();
	void					LoadNPCClickFun(GE::Uint16 uType, PyObject* pyFun_BorrowRef);
	// 每秒钟调用
	void					CallPerSecond();
	// NPC模板
	void					CreateNPCTemplate(GE::Uint16 uType, const char* name, GE::Uint16 uClickLen, GE::Uint8 uClickType, GE::Uint8 uIsMovingNPC);
	NPCTemplate*			GetNPCTemplate(GE::Uint16 uType);
	// NPC配置
	void					CreateNPCConfigObj(GE::Uint32 uID, GE::Uint16 uType, GE::Uint32 uSceneID, GE::Uint16 uX, GE::Uint16 uY);
	NPCConfigObj*			GetNPCConfigObj(GE::Uint32 uID);

	bool					GetFlyNPCPos(GE::Uint32 nNPCID, GE::Uint32& uSceneID, GE::Uint16 &uX, GE::Uint16 &uY);

public:
	// 创建NPC
	NPC*					CreateNPC(SceneBase* pScene, GE::Uint16 uTypeID, GE::Uint16 uX, GE::Uint16 uY, GE::Uint8 uDirection, bool bBroadCast, PyObject* py_BorrowRef);
	// 销毁NPC
	void					DestroyNPC(GE::Uint32 uGlobalID);
	void					DestroyNPC(NPC* pNPC);
	// 点击NPC
	void					ClickNPC(Role* pRole, NPC* pNPC);
	void					ClickCfgNPC(Role* pRole, GE::Uint32 uNPCID);
	void					ClickPrivateNPC(Role* pRole, GE::Uint32 uNPCID);
	void					ClickMirrorNPC(Role* pRole, GE::Uint32 uNPCID);
	// 查找NPC
	NPC*					SearchNPC(GE::Uint32 uNPCID);
	// 分配一个NPCID
	GE::Uint32				AllotGlobalID(); 

private:
	void					InsertNPCToMap(NPC* pNPC);

private:
	GE::Uint32				m_AlloGloBalID;

	//GEGUID32				m_AlloGloBalID;					//全局分配32位ID，高8位是进程ID的低8位
	GEPython::Function		m_pyClickNPCConfigFun;			//点击配置NPC对象调用函数
	GEPython::Function		m_pyClickPrivateNPCFun;			//点击玩家私有NPC对象调用函数
	GEPython::Function		m_pyClickMirrorNPCFun;			//点击副本私有NPC对象调用函数

	GEPython::Function		m_pyLoadClickFun;				//读入服务器创建的NPC的点击函数
	NPCMap					m_NPCMap;
	NPCTemplateMap			m_NPCTemplateMap;
	NPCConfigObjMap			m_NPCConfigObjMap;
};

