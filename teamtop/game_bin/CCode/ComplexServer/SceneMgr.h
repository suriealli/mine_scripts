/************************************************************************
场景管理
************************************************************************/
#pragma once
#include "../GameEngine/GameEngine.h"

// 全局场景对象
#define GLOBAL_OBJ_NUM				100000

enum SceneObjType
{
	enSceneObj_None,				//占位
	enSceneObj_Role,				//角色
	enSceneObj_NPC,					//NPC
	enScnenObj_Monster,				//怪物
};

enum SceneObjFlag
{
	enSceneObj_Observer = 1,		//观察者
	enSceneObj_Observable = 2		//可被观察
};

class SceneObjInfo
{
public:
	SceneObjInfo() {Reset();}
	~SceneObjInfo() {}
public:
	void					Reset() {uX = 0; uY = 0; uType = 0; uFlag = 0; pPTR = NULL;}
	void					SetObserver() {uFlag = uFlag | enSceneObj_Observer;}
	void					SetObservable() {uFlag = uFlag | enSceneObj_Observable;}
	GE::Uint16				IsObserver() {return uFlag & enSceneObj_Observer;}
	GE::Uint16				IsObservable() {return uFlag & enSceneObj_Observable;}
public:
	GE::Uint16				uX;
	GE::Uint16				uY;
	GE::Uint16				uType;
	GE::Uint16				uFlag;
	void*					pPTR;
};

class GlobalObj
	: public GESingleton<GlobalObj>
{
public:
	GlobalObj();
	~GlobalObj();
public:
	GE::Uint32				CreateSceneObj();
	void					DestroySceneObj(GE::Uint32 uID);
	bool					SetSceneObjInfo(GE::Uint32 uID, GE::Uint16 uType, GE::Uint16 uFlag, void* pPRT);
	bool					SetSceneObjPos(GE::Uint32 uID, GE::Uint16 uX, GE::Uint16 uY);
	bool					GetSceneObjPos(GE::Uint32 uID, GE::Uint16& uX, GE::Uint16& uY);

private:
	GEIndex					m_Index;
	SceneObjInfo			m_ObjInfs[GLOBAL_OBJ_NUM];
};

class Role;
class PublicScene;
class MirrorBase;
class SingleMirrorScene;
class MultiMirrorScene;

class SceneMgr
	: public GEControlSingleton<SceneMgr>
{
	typedef boost::unordered_map<GE::Uint32, PublicScene*>				PublicSceneMap;
	typedef boost::unordered_map<GE::Uint32, MirrorBase*>				MirrorSceneMap;

public:
	SceneMgr();
	~SceneMgr();
	void							LoadPyData();
	void							CreateAllPublicScene();
	void							CallPerSceond();
public:

	PublicScene*					CreatePublicScene(GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName, GE::Uint8 uAreaSize, GE::Uint8 uIsSave = 0, GE::Uint8 uCanSeeOther = 0, PyObject* pyAfterCreateFun = NULL, PyObject* pyAfterJoinRoleFun = NULL, PyObject* pyBeforeLeaveFun = NULL, PyObject* pyAfterRestoreFun = NULL);
	PublicScene*					SearchPublicScene(GE::Uint32 uSceneID);
	// 销毁场景
	void							DestroyPublicScene(GE::Uint32 uSceneID);

public:

	// 创建单人场景
	SingleMirrorScene*				CreateSingleMirrorScene(GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName, PyObject* pyBeforeLeaveFun = NULL);
	// 创建多人场景
	MultiMirrorScene*				CreateMultiMirrorScene(GE::Uint32 uGlobalID, GE::Uint16 uMapID, GE::Uint32 uSceneID, const char* pSceneName, PyObject* pyBeforeLeaveFun = NULL, bool bIsAlive = false);

private:
	PublicSceneMap					m_PublicSceneMap;

	GEPython::Function				m_pyCreatePublicScene;						// 场景创建

	// 动态场景管理类, 这部分场景支持动态创建和摧毁，适用于关卡副本等场景地图的创建(GM 工具可以创建和摧毁)
	MirrorSceneMap					m_MirrorSceneMap;
};

