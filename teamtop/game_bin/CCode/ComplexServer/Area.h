/************************************************************************
我是UTF8编码文件
************************************************************************/
#include "../GameEngine/GameEngine.h"
#include "AreaDefine.h"
#include "Role.h"
#include "NPC.h"

//角色链表
typedef  boost::intrusive::member_hook< Role, ListMemberHook, &Role::member_hook_ >		RoleMemberOption;
typedef boost::intrusive::list< Role, RoleMemberOption, ConstantTimeSize >				RoleMenberList;
//NPC链表
typedef boost::intrusive::member_hook< NPC, ListMemberHook, &NPC::m_member_hook >		NPCMemberOption;
typedef boost::intrusive::list< NPC, NPCMemberOption, ConstantTimeSize >				NPCMemberList;
//迭代器
typedef RoleMenberList::iterator	RML_ITER;
typedef NPCMemberList::iterator		NML_ITER;

//一个格子(只用于判断该格子是否可走或者别的属性触发)
class Grid
{
public:
	Grid() : m_uGridProperty(0) {}
	Grid(GE::Uint8 uProperty) : m_uGridProperty(uProperty){}
	~Grid();
public:
	GE::Uint8	GetGridProperty() {return m_uGridProperty;}
	void		SetGridProperty(GE::Uint8 uP) {m_uGridProperty = uP;}

private:
	GE::Uint8 m_uGridProperty;
};


//区域(格子集合)
class Area
{
public:
	Area();
	~Area();

	RoleMenberList*		GetRoleList(){return &m_RoleList;}
	NPCMemberList*		GetNPCList(){return &m_NPCList;}

	RML_ITER			RoleListBegin() {return m_RoleList.begin();}
	RML_ITER			RoleListEnd() { return m_RoleList.end();}

	NML_ITER			NPCListBegin() {return m_NPCList.begin();}
	NML_ITER			NPCListEnd() { return m_NPCList.end();}

public:
	// 格子内部玩家操作
	void				JoinPlayer(Role* pRole);
	void				LeavePlayer(Role* pRole);

	void				JoinNPC(NPC* pNPC);
	void				LeaveNPC(NPC* pNPC);
private:
	RoleMenberList		m_RoleList;		//角色链表
	NPCMemberList		m_NPCList;		//NPC链表
};



