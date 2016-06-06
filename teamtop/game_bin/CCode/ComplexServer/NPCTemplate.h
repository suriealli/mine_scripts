#pragma once
#include <string.h>
#include "../GameEngine/GameEngine.h"

class Role;

//NPC模板
class NPCTemplate
{
public:
	NPCTemplate(GE::Uint16 uNPCType, GE::Uint16 uClickLen, const std::string& strNPCName, GE::Uint8 uClickType, GE::Uint8 uIsMovingNPC);
	~NPCTemplate();

public:
	GE::Uint16				GetNPCType() {return m_uNPCType;}
	std::string&			GetNPCName() {return m_strNPCName;}
	GE::Uint16				GetClickLen() {return m_uClickLen;}
	GE::Uint8				GetClickType() {return m_uClickType;}
	void					LoadClickFun(PyObject* pyFun_BorrowRef);

	bool					IsMovingNPC(){return m_bIsMovingNPC;}


public:
	GE::Uint16				m_uNPCType;			//NPC类型
	GE::Uint16				m_uClickLen;		//可点击距离
	GE::Uint8				m_uClickType;		//点击类型
	std::string				m_strNPCName;		//名字
	GEPython::Function		m_pyOnClickFun;		//服务器创建的NPC点击时调用的函数

	bool					m_bIsMovingNPC;		//是否是移动类型的NPC(服务器不做点击距离判断检测)
};

//配置表NPC(只有一个点击的功能，不会同步客户端)
class NPCConfigObj
{
public:
	NPCConfigObj(GE::Uint32 uID, GE::Uint32 uSceneID, GE::Uint16 uNPCType, GE::Uint16 uX, GE::Uint16 uY);
	~NPCConfigObj();

public:
	bool				CanClick(Role* pRole);					//判断是否可以点击
	GE::Uint16			GetType() {return m_uNPCType;}
	GE::Uint32			GetSceneID(){return m_uSceneID;}
	GE::Uint16			GetPosX(){return m_uX;}
	GE::Uint16			GetPosY(){return m_uY;}
private:
	GE::Uint32			m_uSceneID;
	GE::Uint16			m_uX;
	GE::Uint16			m_uY;
	GE::Uint32			m_uID;
	GE::Uint16			m_uNPCType;
	GE::Uint16			m_uClickLen;
	bool				m_bIsMovingNPC;
};

