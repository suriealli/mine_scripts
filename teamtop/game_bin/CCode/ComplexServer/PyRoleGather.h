/************************************************************************
角色聚合接口（自动生成）
************************************************************************/
#pragma once
#include "../GameEngine/GameEngine.h"
#include "PyRole.h"

class ScriptHold
	: public GEControlSingleton<ScriptHold>
{
public:
	ScriptHold();
	~ScriptHold();

public:
	void							LoadPyData();

public:
	GEPython::Function				m_pyIncExp;
	GEPython::Function				m_pyGetExpCoef;
	GEPython::Function				m_pyGetAllHero;
	GEPython::Function				m_pyGetHero;
	GEPython::Function				m_pyIsLocalServer;
	GEPython::Function				m_pyGetPid;
	GEPython::Function				m_pyGotoLocalServer;
	GEPython::Function				m_pyGotoCrossServer;
	GEPython::Function				m_pyRegPersistenceTick;
	GEPython::Function				m_pyGetTeam;
	GEPython::Function				m_pyHasTeam;
	GEPython::Function				m_pyClientCommand;
	GEPython::Function				m_pyAddHero;
	GEPython::Function				m_pyGetUnionObj;
	GEPython::Function				m_pyAddWing;
	GEPython::Function				m_pyAddPet;
	GEPython::Function				m_pyAddTarotCard;
	GEPython::Function				m_pyTarotPackageIsFull;
	GEPython::Function				m_pyGetTarotEmptySize;
	GEPython::Function				m_pyActiveWeddingRing;
	GEPython::Function				m_pyAddTalentCard;
	GEPython::Function				m_pyAddMount;
	GEPython::Function				m_pyToLevel;
	GEPython::Function				m_pyGetOnLineTimeToday;
	GEPython::Function				m_pyGetJTObj;
	GEPython::Function				m_pyGetJTeamScore;
	GEPython::Function				m_pyGetTotalGemLevel;
	GEPython::Function				m_pyGetRoleZDL;
	GEPython::Function				m_pyGetHeroZDL;
	GEPython::Function				m_pyAddCardAtlas;
	GEPython::Function				m_pyCardAtlasPackageIsFull;
	GEPython::Function				m_pyCardAtlasPackageEmptySize;
	GEPython::Function				m_pyGetAnti;
	GEPython::Function				m_pyAddItem;
	GEPython::Function				m_pyDecPropCnt;
	GEPython::Function				m_pyDelItem;
	GEPython::Function				m_pyDelProp;
	GEPython::Function				m_pyFindGlobalProp;
	GEPython::Function				m_pyFindItem;
	GEPython::Function				m_pyFindPackProp;
	GEPython::Function				m_pyItemCnt;
	GEPython::Function				m_pyItemCnt_NotTimeOut;
	GEPython::Function				m_pyPackageEmptySize;
	GEPython::Function				m_pyPackageIsFull;
	GEPython::Function				m_pyAddCuiLian;
	GEPython::Function				m_pyChangeSex;
	GEPython::Function				m_pyDecBindRMB;
	GEPython::Function				m_pyDecContribution;
	GEPython::Function				m_pyDecDragonSoul;
	GEPython::Function				m_pyDecGongXun;
	GEPython::Function				m_pyDecKuaFuMoney;
	GEPython::Function				m_pyDecMoney;
	GEPython::Function				m_pyDecRMB;
	GEPython::Function				m_pyDecReputation;
	GEPython::Function				m_pyDecRongYu;
	GEPython::Function				m_pyDecStarLucky;
	GEPython::Function				m_pyDecUnbindRMB;
	GEPython::Function				m_pyDecUnbindRMB_Q;
	GEPython::Function				m_pyDecUnbindRMB_S;
	GEPython::Function				m_pyGetArtifactCuiLianHoleLevel;
	GEPython::Function				m_pyGetArtifactMgr;
	GEPython::Function				m_pyGetBindRMB;
	GEPython::Function				m_pyGetCampID;
	GEPython::Function				m_pyGetColorCode;
	GEPython::Function				m_pyGetConsumeQPoint;
	GEPython::Function				m_pyGetContribution;
	GEPython::Function				m_pyGetCuiLian;
	GEPython::Function				m_pyGetCuiLian_MaxCnt;
	GEPython::Function				m_pyGetDayBuyUnbindRMB_Q;
	GEPython::Function				m_pyGetDayConsumeUnbindRMB;
	GEPython::Function				m_pyGetDayWangZheJiFen;
	GEPython::Function				m_pyGetDragonCareerID;
	GEPython::Function				m_pyGetDragonSoul;
	GEPython::Function				m_pyGetEarningExpBuff;
	GEPython::Function				m_pyGetEarningGoldBuff;
	GEPython::Function				m_pyGetElementBrandMgr;
	GEPython::Function				m_pyGetElementSpiritSkill;
	GEPython::Function				m_pyGetEquipmentMgr;
	GEPython::Function				m_pyGetExp;
	GEPython::Function				m_pyGetFTVIP;
	GEPython::Function				m_pyGetFightType;
	GEPython::Function				m_pyGetGongXun;
	GEPython::Function				m_pyGetGrade;
	GEPython::Function				m_pyGetHallowsMgr;
	GEPython::Function				m_pyGetHistoryContribution;
	GEPython::Function				m_pyGetJTProcessID;
	GEPython::Function				m_pyGetJTeamID;
	GEPython::Function				m_pyGetJobID;
	GEPython::Function				m_pyGetKuaFuMoney;
	GEPython::Function				m_pyGetLevel;
	GEPython::Function				m_pyGetMFZSkill;
	GEPython::Function				m_pyGetMFZSkillPointDict;
	GEPython::Function				m_pyGetMagicSpiritMgr;
	GEPython::Function				m_pyGetMoFaZhen;
	GEPython::Function				m_pyGetMoney;
	GEPython::Function				m_pyGetPet;
	GEPython::Function				m_pyGetPortrait;
	GEPython::Function				m_pyGetRMB;
	GEPython::Function				m_pyGetReputation;
	GEPython::Function				m_pyGetRightMountID;
	GEPython::Function				m_pyGetRongYu;
	GEPython::Function				m_pyGetSex;
	GEPython::Function				m_pyGetStar;
	GEPython::Function				m_pyGetStarLucky;
	GEPython::Function				m_pyGetStationID;
	GEPython::Function				m_pyGetStationSoulSkill;
	GEPython::Function				m_pyGetTalentEmptySize;
	GEPython::Function				m_pyGetTalentMgr;
	GEPython::Function				m_pyGetTalentZDL;
	GEPython::Function				m_pyGetUnbindRMB;
	GEPython::Function				m_pyGetUnbindRMB_Q;
	GEPython::Function				m_pyGetUnbindRMB_S;
	GEPython::Function				m_pyGetUnionID;
	GEPython::Function				m_pyGetVIP;
	GEPython::Function				m_pyGetWeek;
	GEPython::Function				m_pyGetWingID;
	GEPython::Function				m_pyGetXinYueLevel;
	GEPython::Function				m_pyGetZDL;
	GEPython::Function				m_pyGetZhuanShengHaloAddi;
	GEPython::Function				m_pyGetZhuanShengHaloLevel;
	GEPython::Function				m_pyGetZhuanShengLevel;
	GEPython::Function				m_pyIncBindRMB;
	GEPython::Function				m_pyIncConsumeQPoint;
	GEPython::Function				m_pyIncContribution;
	GEPython::Function				m_pyIncDragonSoul;
	GEPython::Function				m_pyIncGongXun;
	GEPython::Function				m_pyIncHistoryContribution;
	GEPython::Function				m_pyIncKuaFuMoney;
	GEPython::Function				m_pyIncLevel;
	GEPython::Function				m_pyIncMoney;
	GEPython::Function				m_pyIncReputation;
	GEPython::Function				m_pyIncRongYu;
	GEPython::Function				m_pyIncStarLucky;
	GEPython::Function				m_pyIncTarotHP;
	GEPython::Function				m_pyIncTouchGoldPoint;
	GEPython::Function				m_pyIncUnbindRMB_Q;
	GEPython::Function				m_pyIncUnbindRMB_S;
	GEPython::Function				m_pyIsKongJianDecennialRole;
	GEPython::Function				m_pyIsMonthCard;
	GEPython::Function				m_pySetBindRMB;
	GEPython::Function				m_pySetCampID;
	GEPython::Function				m_pySetCanChatTime;
	GEPython::Function				m_pySetCanLoginTime;
	GEPython::Function				m_pySetConsumeQPoint;
	GEPython::Function				m_pySetContribution;
	GEPython::Function				m_pySetDragonCareerID;
	GEPython::Function				m_pySetDragonSoul;
	GEPython::Function				m_pySetEarningExpBuff;
	GEPython::Function				m_pySetEarningGoldBuff;
	GEPython::Function				m_pySetExp;
	GEPython::Function				m_pySetFightType;
	GEPython::Function				m_pySetGongXun;
	GEPython::Function				m_pySetGrade;
	GEPython::Function				m_pySetHistoryContribution;
	GEPython::Function				m_pySetJTeamID;
	GEPython::Function				m_pySetJobID;
	GEPython::Function				m_pySetKuaFuMoney;
	GEPython::Function				m_pySetMoney;
	GEPython::Function				m_pySetReputation;
	GEPython::Function				m_pySetRightMountID;
	GEPython::Function				m_pySetRongYu;
	GEPython::Function				m_pySetStarLucky;
	GEPython::Function				m_pySetStationID;
	GEPython::Function				m_pySetUnbindRMB_Q;
	GEPython::Function				m_pySetUnbindRMB_S;
	GEPython::Function				m_pySetUnionID;
	GEPython::Function				m_pySetVIP;
	GEPython::Function				m_pySetWeek;
	GEPython::Function				m_pySetWingID;
	GEPython::Function				m_pySetZDL;
	GEPython::Function				m_pySetZhuanShengHaloLevel;
	GEPython::Function				m_pySetZhuanShengLevel;
	GEPython::Function				m_pyUpdateAndSyncMFZSkillPassive;
	GEPython::Function				m_pyCreateHeroProperty;
	GEPython::Function				m_pyGetPropertyGather;
	GEPython::Function				m_pyGetPropertyMgr;
	GEPython::Function				m_pyPropertyIsValid;
	GEPython::Function				m_pyRemoveHeroProperty;
	GEPython::Function				m_pyResetAllTarotProperty;
	GEPython::Function				m_pyResetElementBrandBaseProperty;
	GEPython::Function				m_pyResetElementSpiritProperty;
	GEPython::Function				m_pyResetGlobalCardAtlasProperty;
	GEPython::Function				m_pyResetGlobalDragonProperty;
	GEPython::Function				m_pyResetGlobalFashionProperty;
	GEPython::Function				m_pyResetGlobalHelpStationProperty;
	GEPython::Function				m_pyResetGlobalMountAppProperty;
	GEPython::Function				m_pyResetGlobalMountProperty;
	GEPython::Function				m_pyResetGlobalQinmiGradeProperty;
	GEPython::Function				m_pyResetGlobalQinmiProperty;
	GEPython::Function				m_pyResetGlobalStationSoulItemProperty;
	GEPython::Function				m_pyResetGlobalWStationBaseProperty;
	GEPython::Function				m_pyResetGlobalWStationItemProperty;
	GEPython::Function				m_pyResetGlobalWStationThousandProperty;
	GEPython::Function				m_pyResetGlobalWeddingRingProperty;
	GEPython::Function				m_pyResetGlobalWeddingRingSProperty;
	GEPython::Function				m_pyResetGlobalWeddingRingSkillProperty;
	GEPython::Function				m_pyResetGlobalWingProperty;
	GEPython::Function				m_pyResetGlobalZhuanShengHaloBaseProperty;
	GEPython::Function				m_pyResetMarryRingProperty;
	GEPython::Function				m_pyResetSealProperty;
	GEPython::Function				m_pyResetStationSoulProperty;
	GEPython::Function				m_pyResetTitleProperty;
	GEPython::Function				m_pySyncAllProperty;
};

#define RoleGather_Methods \
	{"IncExp", (PyCFunction)IncExp, METH_VARARGS, "None "}, \
	{"GetExpCoef", (PyCFunction)GetExpCoef, METH_NOARGS, "None "}, \
	{"GetAllHero", (PyCFunction)GetAllHero, METH_NOARGS, "获取所有英雄 英雄id --> 英雄对象 "}, \
	{"GetHero", (PyCFunction)GetHero, METH_VARARGS, "根据英雄id获取英雄对象 返回英雄对象或者None "}, \
	{"IsLocalServer", (PyCFunction)IsLocalServer, METH_NOARGS, "是否是本服(包括合服的角色) "}, \
	{"GetPid", (PyCFunction)GetPid, METH_NOARGS, "获取角色原始进程ID "}, \
	{"GotoLocalServer", (PyCFunction)GotoLocalServer, METH_VARARGS, "None "}, \
	{"GotoCrossServer", (PyCFunction)GotoCrossServer, METH_VARARGS, "None "}, \
	{"RegPersistenceTick", (PyCFunction)RegPersistenceTick, METH_VARARGS, "None "}, \
	{"GetTeam", (PyCFunction)GetTeam, METH_NOARGS, "获取当前的组队对象 "}, \
	{"HasTeam", (PyCFunction)HasTeam, METH_NOARGS, "判断角色是否有队伍了 team "}, \
	{"ClientCommand", (PyCFunction)ClientCommand, METH_VARARGS, "命令很多话执行命令 "}, \
	{"AddHero", (PyCFunction)AddHero, METH_VARARGS, "直接增加一个英雄 "}, \
	{"GetUnionObj", (PyCFunction)GetUnionObj, METH_NOARGS, "获取公会对象 "}, \
	{"AddWing", (PyCFunction)AddWing, METH_VARARGS, "添加一个翅膀 "}, \
	{"AddPet", (PyCFunction)AddPet, METH_VARARGS, "None "}, \
	{"AddTarotCard", (PyCFunction)AddTarotCard, METH_VARARGS, "增加一个命魂 "}, \
	{"TarotPackageIsFull", (PyCFunction)TarotPackageIsFull, METH_NOARGS, "命魂背包是否已经满了 "}, \
	{"GetTarotEmptySize", (PyCFunction)GetTarotEmptySize, METH_NOARGS, "获取命魂背包格子数 "}, \
	{"ActiveWeddingRing", (PyCFunction)ActiveWeddingRing, METH_NOARGS, "激活婚戒 "}, \
	{"AddTalentCard", (PyCFunction)AddTalentCard, METH_VARARGS, "增加一个天赋卡 "}, \
	{"AddMount", (PyCFunction)AddMount, METH_VARARGS, "None "}, \
	{"ToLevel", (PyCFunction)ToLevel, METH_VARARGS, "直接升至多少级 "}, \
	{"GetOnLineTimeToday", (PyCFunction)GetOnLineTimeToday, METH_NOARGS, "获取当前累计在线时间 "}, \
	{"GetJTObj", (PyCFunction)GetJTObj, METH_NOARGS, "获取战队对象(本服逻辑进程专用) "}, \
	{"GetJTeamScore", (PyCFunction)GetJTeamScore, METH_NOARGS, "获取战队积分 "}, \
	{"GetTotalGemLevel", (PyCFunction)GetTotalGemLevel, METH_NOARGS, "None "}, \
	{"GetRoleZDL", (PyCFunction)GetRoleZDL, METH_NOARGS, "None "}, \
	{"GetHeroZDL", (PyCFunction)GetHeroZDL, METH_NOARGS, "None "}, \
	{"AddCardAtlas", (PyCFunction)AddCardAtlas, METH_VARARGS, "增加卡牌 "}, \
	{"CardAtlasPackageIsFull", (PyCFunction)CardAtlasPackageIsFull, METH_NOARGS, "卡牌图鉴背包是否满了 "}, \
	{"CardAtlasPackageEmptySize", (PyCFunction)CardAtlasPackageEmptySize, METH_NOARGS, "卡牌图鉴背包空格数 "}, \
	{"GetAnti", (PyCFunction)GetAnti, METH_NOARGS, "None "}, \
	{"AddItem", (PyCFunction)AddItem, METH_VARARGS, "将一个物品加入背包 (coding, cnt) "}, \
	{"DecPropCnt", (PyCFunction)DecPropCnt, METH_VARARGS, "None "}, \
	{"DelItem", (PyCFunction)DelItem, METH_VARARGS, "将一个物品从背包删除 (coding, cnt) 返回真正删除的个数 "}, \
	{"DelProp", (PyCFunction)DelProp, METH_VARARGS, "将一个道具从背包删除 (propId) 返回是否删除成功 "}, \
	{"FindGlobalProp", (PyCFunction)FindGlobalProp, METH_VARARGS, "根据道具id，查询一个全局的物品 "}, \
	{"FindItem", (PyCFunction)FindItem, METH_VARARGS, "根据道具coding，获取背包中的道具 返回道具对象或者None "}, \
	{"FindPackProp", (PyCFunction)FindPackProp, METH_VARARGS, "根据道具id，获取背包中的道具 返回道具对象或者None "}, \
	{"ItemCnt", (PyCFunction)ItemCnt, METH_VARARGS, "获取物品数量 (coding) 返回物品数量 "}, \
	{"ItemCnt_NotTimeOut", (PyCFunction)ItemCnt_NotTimeOut, METH_VARARGS, "获取物品数量 (coding) 返回还没有过期的物品数量   "}, \
	{"PackageEmptySize", (PyCFunction)PackageEmptySize, METH_NOARGS, "获取背包空格子数 "}, \
	{"PackageIsFull", (PyCFunction)PackageIsFull, METH_NOARGS, "判断背包是否满 "}, \
	{"AddCuiLian", (PyCFunction)AddCuiLian, METH_VARARGS, "	增加角色淬炼次数	 "}, \
	{"ChangeSex", (PyCFunction)ChangeSex, METH_NOARGS, "改变角色性别 "}, \
	{"DecBindRMB", (PyCFunction)DecBindRMB, METH_VARARGS, "减少绑定(魔晶) "}, \
	{"DecContribution", (PyCFunction)DecContribution, METH_VARARGS, "减少公会贡献 "}, \
	{"DecDragonSoul", (PyCFunction)DecDragonSoul, METH_VARARGS, "减少龙灵数量 "}, \
	{"DecGongXun", (PyCFunction)DecGongXun, METH_VARARGS, "减少功勋 "}, \
	{"DecKuaFuMoney", (PyCFunction)DecKuaFuMoney, METH_VARARGS, "减少跨服币 "}, \
	{"DecMoney", (PyCFunction)DecMoney, METH_VARARGS, "减少金钱 "}, \
	{"DecRMB", (PyCFunction)DecRMB, METH_VARARGS, "减少魔晶和神石 "}, \
	{"DecReputation", (PyCFunction)DecReputation, METH_VARARGS, "减少声望 "}, \
	{"DecRongYu", (PyCFunction)DecRongYu, METH_VARARGS, "减少荣誉 "}, \
	{"DecStarLucky", (PyCFunction)DecStarLucky, METH_VARARGS, "减少星运数量 "}, \
	{"DecUnbindRMB", (PyCFunction)DecUnbindRMB, METH_VARARGS, "减少非绑定(神石) "}, \
	{"DecUnbindRMB_Q", (PyCFunction)DecUnbindRMB_Q, METH_VARARGS, "减少非绑定(充值 神石) "}, \
	{"DecUnbindRMB_S", (PyCFunction)DecUnbindRMB_S, METH_VARARGS, "减少非绑定(系统 神石) "}, \
	{"GetArtifactCuiLianHoleLevel", (PyCFunction)GetArtifactCuiLianHoleLevel, METH_NOARGS, "获取角色神器淬炼光环等级 "}, \
	{"GetArtifactMgr", (PyCFunction)GetArtifactMgr, METH_NOARGS, "获取神器管理器 "}, \
	{"GetBindRMB", (PyCFunction)GetBindRMB, METH_NOARGS, "获取绑定(魔晶) "}, \
	{"GetCampID", (PyCFunction)GetCampID, METH_NOARGS, "获取阵营ID "}, \
	{"GetColorCode", (PyCFunction)GetColorCode, METH_NOARGS, "获取主角颜色编码 "}, \
	{"GetConsumeQPoint", (PyCFunction)GetConsumeQPoint, METH_NOARGS, "获取消费点 "}, \
	{"GetContribution", (PyCFunction)GetContribution, METH_NOARGS, "获取公会贡献 "}, \
	{"GetCuiLian", (PyCFunction)GetCuiLian, METH_NOARGS, "	返回角色淬炼次数	 "}, \
	{"GetCuiLian_MaxCnt", (PyCFunction)GetCuiLian_MaxCnt, METH_NOARGS, "	返回角色可以淬炼的最大次数	 "}, \
	{"GetDayBuyUnbindRMB_Q", (PyCFunction)GetDayBuyUnbindRMB_Q, METH_NOARGS, "获取每日充值神石 "}, \
	{"GetDayConsumeUnbindRMB", (PyCFunction)GetDayConsumeUnbindRMB, METH_NOARGS, "获取每日消费神石，包括充值神石和系统神石 "}, \
	{"GetDayWangZheJiFen", (PyCFunction)GetDayWangZheJiFen, METH_NOARGS, "返回玩家今日王者公测积分 "}, \
	{"GetDragonCareerID", (PyCFunction)GetDragonCareerID, METH_NOARGS, "获取神龙职业ID "}, \
	{"GetDragonSoul", (PyCFunction)GetDragonSoul, METH_NOARGS, "获取龙灵数量 "}, \
	{"GetEarningExpBuff", (PyCFunction)GetEarningExpBuff, METH_NOARGS, "获取城主经验加成buff "}, \
	{"GetEarningGoldBuff", (PyCFunction)GetEarningGoldBuff, METH_NOARGS, "获取城主金钱加成buff "}, \
	{"GetElementBrandMgr", (PyCFunction)GetElementBrandMgr, METH_NOARGS, "返回元素印记管理器 "}, \
	{"GetElementSpiritSkill", (PyCFunction)GetElementSpiritSkill, METH_NOARGS, "返回元素之灵技能 "}, \
	{"GetEquipmentMgr", (PyCFunction)GetEquipmentMgr, METH_NOARGS, "获取装备管理器 "}, \
	{"GetExp", (PyCFunction)GetExp, METH_NOARGS, "获取经验 "}, \
	{"GetFTVIP", (PyCFunction)GetFTVIP, METH_NOARGS, "获取繁体VIP "}, \
	{"GetFightType", (PyCFunction)GetFightType, METH_NOARGS, "获取当前临时的战斗类型 "}, \
	{"GetGongXun", (PyCFunction)GetGongXun, METH_NOARGS, "获取功勋 "}, \
	{"GetGrade", (PyCFunction)GetGrade, METH_NOARGS, "获取进阶 "}, \
	{"GetHallowsMgr", (PyCFunction)GetHallowsMgr, METH_NOARGS, "获取圣器管理器 "}, \
	{"GetHistoryContribution", (PyCFunction)GetHistoryContribution, METH_NOARGS, "获取公会历史贡献 "}, \
	{"GetJTProcessID", (PyCFunction)GetJTProcessID, METH_NOARGS, "获取组队竞技场是的本服进程ID "}, \
	{"GetJTeamID", (PyCFunction)GetJTeamID, METH_NOARGS, "获取战队id "}, \
	{"GetJobID", (PyCFunction)GetJobID, METH_NOARGS, "获取公会职位ID "}, \
	{"GetKuaFuMoney", (PyCFunction)GetKuaFuMoney, METH_NOARGS, "获取跨服币 "}, \
	{"GetLevel", (PyCFunction)GetLevel, METH_NOARGS, "获取角色等级 "}, \
	{"GetMFZSkill", (PyCFunction)GetMFZSkill, METH_NOARGS, "	获取当前携带的魔法阵技能 "}, \
	{"GetMFZSkillPointDict", (PyCFunction)GetMFZSkillPointDict, METH_NOARGS, "获取魔法阵技能点字典 "}, \
	{"GetMagicSpiritMgr", (PyCFunction)GetMagicSpiritMgr, METH_NOARGS, "获取魔灵管理器 "}, \
	{"GetMoFaZhen", (PyCFunction)GetMoFaZhen, METH_NOARGS, "返回魔法阵数据 "}, \
	{"GetMoney", (PyCFunction)GetMoney, METH_NOARGS, "获取金钱 "}, \
	{"GetPet", (PyCFunction)GetPet, METH_NOARGS, "获取角色佩戴的宠物 "}, \
	{"GetPortrait", (PyCFunction)GetPortrait, METH_NOARGS, "获取头像信息(性别, 职业, 进阶) "}, \
	{"GetRMB", (PyCFunction)GetRMB, METH_NOARGS, "获取魔晶和神石 "}, \
	{"GetReputation", (PyCFunction)GetReputation, METH_NOARGS, "获取声望 "}, \
	{"GetRightMountID", (PyCFunction)GetRightMountID, METH_NOARGS, "获取玩家当前骑乘坐骑ID "}, \
	{"GetRongYu", (PyCFunction)GetRongYu, METH_NOARGS, "获取荣誉 "}, \
	{"GetSex", (PyCFunction)GetSex, METH_NOARGS, "获取角色性别 "}, \
	{"GetStar", (PyCFunction)GetStar, METH_NOARGS, "获取主角星级 "}, \
	{"GetStarLucky", (PyCFunction)GetStarLucky, METH_NOARGS, "获取星运数量 "}, \
	{"GetStationID", (PyCFunction)GetStationID, METH_NOARGS, "获取阵位ID "}, \
	{"GetStationSoulSkill", (PyCFunction)GetStationSoulSkill, METH_NOARGS, "返回角色当前阵灵技能 "}, \
	{"GetTalentEmptySize", (PyCFunction)GetTalentEmptySize, METH_NOARGS, "获取天赋卡背包空余格子数 "}, \
	{"GetTalentMgr", (PyCFunction)GetTalentMgr, METH_NOARGS, "获取天赋卡管理器 "}, \
	{"GetTalentZDL", (PyCFunction)GetTalentZDL, METH_NOARGS, "获取玩家天赋卡技能战斗力（只有主角） "}, \
	{"GetUnbindRMB", (PyCFunction)GetUnbindRMB, METH_NOARGS, "获取非绑定(神石) "}, \
	{"GetUnbindRMB_Q", (PyCFunction)GetUnbindRMB_Q, METH_NOARGS, "获取非绑定(充值 神石) "}, \
	{"GetUnbindRMB_S", (PyCFunction)GetUnbindRMB_S, METH_NOARGS, "获取非绑定(系统 神石) "}, \
	{"GetUnionID", (PyCFunction)GetUnionID, METH_NOARGS, "获取公会ID "}, \
	{"GetVIP", (PyCFunction)GetVIP, METH_NOARGS, "获取VIP "}, \
	{"GetWeek", (PyCFunction)GetWeek, METH_NOARGS, "获取当前周数 "}, \
	{"GetWingID", (PyCFunction)GetWingID, METH_NOARGS, "获取翅膀ID "}, \
	{"GetXinYueLevel", (PyCFunction)GetXinYueLevel, METH_NOARGS, "心悦VIP等级 "}, \
	{"GetZDL", (PyCFunction)GetZDL, METH_NOARGS, "获取战斗力 "}, \
	{"GetZhuanShengHaloAddi", (PyCFunction)GetZhuanShengHaloAddi, METH_NOARGS, "获取角色转生光环加成 "}, \
	{"GetZhuanShengHaloLevel", (PyCFunction)GetZhuanShengHaloLevel, METH_NOARGS, "获取角色转生光环等级 "}, \
	{"GetZhuanShengLevel", (PyCFunction)GetZhuanShengLevel, METH_NOARGS, "获取角色转生等级 "}, \
	{"IncBindRMB", (PyCFunction)IncBindRMB, METH_VARARGS, "增加绑定(魔晶) "}, \
	{"IncConsumeQPoint", (PyCFunction)IncConsumeQPoint, METH_VARARGS, "增加消费点 "}, \
	{"IncContribution", (PyCFunction)IncContribution, METH_VARARGS, "增加公会贡献 "}, \
	{"IncDragonSoul", (PyCFunction)IncDragonSoul, METH_VARARGS, "增加龙灵数量 "}, \
	{"IncGongXun", (PyCFunction)IncGongXun, METH_VARARGS, "增加功勋 "}, \
	{"IncHistoryContribution", (PyCFunction)IncHistoryContribution, METH_VARARGS, "增加公会历史贡献 "}, \
	{"IncKuaFuMoney", (PyCFunction)IncKuaFuMoney, METH_VARARGS, "增加跨服币 "}, \
	{"IncLevel", (PyCFunction)IncLevel, METH_VARARGS, "提升角色等级 "}, \
	{"IncMoney", (PyCFunction)IncMoney, METH_VARARGS, "增加金钱 "}, \
	{"IncReputation", (PyCFunction)IncReputation, METH_VARARGS, "增加声望 "}, \
	{"IncRongYu", (PyCFunction)IncRongYu, METH_VARARGS, "增加荣誉 "}, \
	{"IncStarLucky", (PyCFunction)IncStarLucky, METH_VARARGS, "增加星运数量 "}, \
	{"IncTarotHP", (PyCFunction)IncTarotHP, METH_VARARGS, "增加命力 "}, \
	{"IncTouchGoldPoint", (PyCFunction)IncTouchGoldPoint, METH_VARARGS, "None "}, \
	{"IncUnbindRMB_Q", (PyCFunction)IncUnbindRMB_Q, METH_VARARGS, "增加非绑定(充值 神石) "}, \
	{"IncUnbindRMB_S", (PyCFunction)IncUnbindRMB_S, METH_VARARGS, "增加非绑定(系统 神石) "}, \
	{"IsKongJianDecennialRole", (PyCFunction)IsKongJianDecennialRole, METH_NOARGS, "判断玩家登录渠道是否为 空间、朋友网、 QQ游戏大厅、3366、官网 "}, \
	{"IsMonthCard", (PyCFunction)IsMonthCard, METH_NOARGS, "是否月卡 "}, \
	{"SetBindRMB", (PyCFunction)SetBindRMB, METH_VARARGS, "设置绑定(魔晶) "}, \
	{"SetCampID", (PyCFunction)SetCampID, METH_VARARGS, "设置阵营ID "}, \
	{"SetCanChatTime", (PyCFunction)SetCanChatTime, METH_VARARGS, "设置可发言的时间（解/禁 发言） "}, \
	{"SetCanLoginTime", (PyCFunction)SetCanLoginTime, METH_VARARGS, "设置可登录时间，并且T掉角色（封角色） "}, \
	{"SetConsumeQPoint", (PyCFunction)SetConsumeQPoint, METH_VARARGS, "设置消费点 "}, \
	{"SetContribution", (PyCFunction)SetContribution, METH_VARARGS, "设置公会贡献 "}, \
	{"SetDragonCareerID", (PyCFunction)SetDragonCareerID, METH_VARARGS, "设置神龙职业ID "}, \
	{"SetDragonSoul", (PyCFunction)SetDragonSoul, METH_VARARGS, "设置龙灵数量 "}, \
	{"SetEarningExpBuff", (PyCFunction)SetEarningExpBuff, METH_VARARGS, "设置城主经验加成buff "}, \
	{"SetEarningGoldBuff", (PyCFunction)SetEarningGoldBuff, METH_VARARGS, "设置城主金钱加成buff "}, \
	{"SetExp", (PyCFunction)SetExp, METH_VARARGS, "设置经验 （小心使用） "}, \
	{"SetFightType", (PyCFunction)SetFightType, METH_VARARGS, "设置当前临时的战斗类型 "}, \
	{"SetGongXun", (PyCFunction)SetGongXun, METH_VARARGS, "设置功勋 "}, \
	{"SetGrade", (PyCFunction)SetGrade, METH_VARARGS, "设置进阶 "}, \
	{"SetHistoryContribution", (PyCFunction)SetHistoryContribution, METH_VARARGS, "设置公会历史贡献 "}, \
	{"SetJTeamID", (PyCFunction)SetJTeamID, METH_VARARGS, "设置战队ID "}, \
	{"SetJobID", (PyCFunction)SetJobID, METH_VARARGS, "设置公会职位ID "}, \
	{"SetKuaFuMoney", (PyCFunction)SetKuaFuMoney, METH_VARARGS, "设置跨服币 "}, \
	{"SetMoney", (PyCFunction)SetMoney, METH_VARARGS, "设置金钱 "}, \
	{"SetReputation", (PyCFunction)SetReputation, METH_VARARGS, "设置声望 "}, \
	{"SetRightMountID", (PyCFunction)SetRightMountID, METH_VARARGS, "设置玩家当前骑乘坐骑ID "}, \
	{"SetRongYu", (PyCFunction)SetRongYu, METH_VARARGS, "设置荣誉 "}, \
	{"SetStarLucky", (PyCFunction)SetStarLucky, METH_VARARGS, "设置星运数量 "}, \
	{"SetStationID", (PyCFunction)SetStationID, METH_VARARGS, "设置阵位ID "}, \
	{"SetUnbindRMB_Q", (PyCFunction)SetUnbindRMB_Q, METH_VARARGS, "设置非绑定(充值 神石) "}, \
	{"SetUnbindRMB_S", (PyCFunction)SetUnbindRMB_S, METH_VARARGS, "设置非绑定(系统 神石) "}, \
	{"SetUnionID", (PyCFunction)SetUnionID, METH_VARARGS, "设置公会ID "}, \
	{"SetVIP", (PyCFunction)SetVIP, METH_VARARGS, "设置VIP "}, \
	{"SetWeek", (PyCFunction)SetWeek, METH_VARARGS, "设置当前周数 "}, \
	{"SetWingID", (PyCFunction)SetWingID, METH_VARARGS, "设置翅膀ID "}, \
	{"SetZDL", (PyCFunction)SetZDL, METH_VARARGS, "设置战斗力 "}, \
	{"SetZhuanShengHaloLevel", (PyCFunction)SetZhuanShengHaloLevel, METH_VARARGS, "设置角色转生光环等级 "}, \
	{"SetZhuanShengLevel", (PyCFunction)SetZhuanShengLevel, METH_VARARGS, "设置角色转生等级 "}, \
	{"UpdateAndSyncMFZSkillPassive", (PyCFunction)UpdateAndSyncMFZSkillPassive, METH_NOARGS, "更新当前魔法阵技能携带状态 "}, \
	{"CreateHeroProperty", (PyCFunction)CreateHeroProperty, METH_VARARGS, "创建一个英雄属性集合 "}, \
	{"GetPropertyGather", (PyCFunction)GetPropertyGather, METH_NOARGS, "获取主角属性集合 "}, \
	{"GetPropertyMgr", (PyCFunction)GetPropertyMgr, METH_NOARGS, "获取角色属性管理器 "}, \
	{"PropertyIsValid", (PyCFunction)PropertyIsValid, METH_NOARGS, "属性是否已经生效了 "}, \
	{"RemoveHeroProperty", (PyCFunction)RemoveHeroProperty, METH_VARARGS, "移除一个英雄的属性集合 "}, \
	{"ResetAllTarotProperty", (PyCFunction)ResetAllTarotProperty, METH_NOARGS, "设置所有的占卜属性重算(特殊) "}, \
	{"ResetElementBrandBaseProperty", (PyCFunction)ResetElementBrandBaseProperty, METH_NOARGS, "设置元素印记基本属性重算 "}, \
	{"ResetElementSpiritProperty", (PyCFunction)ResetElementSpiritProperty, METH_NOARGS, "设置元素之灵属性重算 "}, \
	{"ResetGlobalCardAtlasProperty", (PyCFunction)ResetGlobalCardAtlasProperty, METH_NOARGS, "重算卡牌图鉴属性 "}, \
	{"ResetGlobalDragonProperty", (PyCFunction)ResetGlobalDragonProperty, METH_NOARGS, "设置全局神龙属性重算 "}, \
	{"ResetGlobalFashionProperty", (PyCFunction)ResetGlobalFashionProperty, METH_NOARGS, "设置全局时装鉴定属性重算 "}, \
	{"ResetGlobalHelpStationProperty", (PyCFunction)ResetGlobalHelpStationProperty, METH_NOARGS, "设置全局助阵属性重算 "}, \
	{"ResetGlobalMountAppProperty", (PyCFunction)ResetGlobalMountAppProperty, METH_NOARGS, "设置全局坐骑外形品质属性重算 "}, \
	{"ResetGlobalMountProperty", (PyCFunction)ResetGlobalMountProperty, METH_NOARGS, "设置全局坐骑属性重算 "}, \
	{"ResetGlobalQinmiGradeProperty", (PyCFunction)ResetGlobalQinmiGradeProperty, METH_NOARGS, "设置全局亲密品阶属性重算 "}, \
	{"ResetGlobalQinmiProperty", (PyCFunction)ResetGlobalQinmiProperty, METH_NOARGS, "设置全局亲密等级属性重算 "}, \
	{"ResetGlobalStationSoulItemProperty", (PyCFunction)ResetGlobalStationSoulItemProperty, METH_NOARGS, "设置重算阵灵强化石属性 "}, \
	{"ResetGlobalWStationBaseProperty", (PyCFunction)ResetGlobalWStationBaseProperty, METH_NOARGS, "重算战阵基础属性 "}, \
	{"ResetGlobalWStationItemProperty", (PyCFunction)ResetGlobalWStationItemProperty, METH_NOARGS, "重算战阵战魂石属性 "}, \
	{"ResetGlobalWStationThousandProperty", (PyCFunction)ResetGlobalWStationThousandProperty, METH_NOARGS, "重算战阵万分比属性 "}, \
	{"ResetGlobalWeddingRingProperty", (PyCFunction)ResetGlobalWeddingRingProperty, METH_NOARGS, "设置全局婚戒属性重算 "}, \
	{"ResetGlobalWeddingRingSProperty", (PyCFunction)ResetGlobalWeddingRingSProperty, METH_NOARGS, "设置全局婚戒戒灵属性重算 "}, \
	{"ResetGlobalWeddingRingSkillProperty", (PyCFunction)ResetGlobalWeddingRingSkillProperty, METH_NOARGS, "设置全局夫妻技能属性重算 "}, \
	{"ResetGlobalWingProperty", (PyCFunction)ResetGlobalWingProperty, METH_NOARGS, "设置全局翅膀属性重算 "}, \
	{"ResetGlobalZhuanShengHaloBaseProperty", (PyCFunction)ResetGlobalZhuanShengHaloBaseProperty, METH_NOARGS, "重算转身光环基础 属性 "}, \
	{"ResetMarryRingProperty", (PyCFunction)ResetMarryRingProperty, METH_NOARGS, "设置订婚戒指属性重算 "}, \
	{"ResetSealProperty", (PyCFunction)ResetSealProperty, METH_NOARGS, "设置圣印属性重算 "}, \
	{"ResetStationSoulProperty", (PyCFunction)ResetStationSoulProperty, METH_NOARGS, "设置阵灵属性重算 "}, \
	{"ResetTitleProperty", (PyCFunction)ResetTitleProperty, METH_NOARGS, "设置称号属性重算 "}, \
	{"SyncAllProperty", (PyCFunction)SyncAllProperty, METH_NOARGS, "同步所有的属性 "}, \


namespace ServerPython
{
	PyObject*  IncExp(PyRoleObject* self, PyObject* arg);
	PyObject*  GetExpCoef(PyRoleObject* self, PyObject* arg);
	PyObject*  GetAllHero(PyRoleObject* self, PyObject* arg);
	PyObject*  GetHero(PyRoleObject* self, PyObject* arg);
	PyObject*  IsLocalServer(PyRoleObject* self, PyObject* arg);
	PyObject*  GetPid(PyRoleObject* self, PyObject* arg);
	PyObject*  GotoLocalServer(PyRoleObject* self, PyObject* arg);
	PyObject*  GotoCrossServer(PyRoleObject* self, PyObject* arg);
	PyObject*  RegPersistenceTick(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTeam(PyRoleObject* self, PyObject* arg);
	PyObject*  HasTeam(PyRoleObject* self, PyObject* arg);
	PyObject*  ClientCommand(PyRoleObject* self, PyObject* arg);
	PyObject*  AddHero(PyRoleObject* self, PyObject* arg);
	PyObject*  GetUnionObj(PyRoleObject* self, PyObject* arg);
	PyObject*  AddWing(PyRoleObject* self, PyObject* arg);
	PyObject*  AddPet(PyRoleObject* self, PyObject* arg);
	PyObject*  AddTarotCard(PyRoleObject* self, PyObject* arg);
	PyObject*  TarotPackageIsFull(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTarotEmptySize(PyRoleObject* self, PyObject* arg);
	PyObject*  ActiveWeddingRing(PyRoleObject* self, PyObject* arg);
	PyObject*  AddTalentCard(PyRoleObject* self, PyObject* arg);
	PyObject*  AddMount(PyRoleObject* self, PyObject* arg);
	PyObject*  ToLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  GetOnLineTimeToday(PyRoleObject* self, PyObject* arg);
	PyObject*  GetJTObj(PyRoleObject* self, PyObject* arg);
	PyObject*  GetJTeamScore(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTotalGemLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  GetRoleZDL(PyRoleObject* self, PyObject* arg);
	PyObject*  GetHeroZDL(PyRoleObject* self, PyObject* arg);
	PyObject*  AddCardAtlas(PyRoleObject* self, PyObject* arg);
	PyObject*  CardAtlasPackageIsFull(PyRoleObject* self, PyObject* arg);
	PyObject*  CardAtlasPackageEmptySize(PyRoleObject* self, PyObject* arg);
	PyObject*  GetAnti(PyRoleObject* self, PyObject* arg);
	PyObject*  AddItem(PyRoleObject* self, PyObject* arg);
	PyObject*  DecPropCnt(PyRoleObject* self, PyObject* arg);
	PyObject*  DelItem(PyRoleObject* self, PyObject* arg);
	PyObject*  DelProp(PyRoleObject* self, PyObject* arg);
	PyObject*  FindGlobalProp(PyRoleObject* self, PyObject* arg);
	PyObject*  FindItem(PyRoleObject* self, PyObject* arg);
	PyObject*  FindPackProp(PyRoleObject* self, PyObject* arg);
	PyObject*  ItemCnt(PyRoleObject* self, PyObject* arg);
	PyObject*  ItemCnt_NotTimeOut(PyRoleObject* self, PyObject* arg);
	PyObject*  PackageEmptySize(PyRoleObject* self, PyObject* arg);
	PyObject*  PackageIsFull(PyRoleObject* self, PyObject* arg);
	PyObject*  AddCuiLian(PyRoleObject* self, PyObject* arg);
	PyObject*  ChangeSex(PyRoleObject* self, PyObject* arg);
	PyObject*  DecBindRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  DecContribution(PyRoleObject* self, PyObject* arg);
	PyObject*  DecDragonSoul(PyRoleObject* self, PyObject* arg);
	PyObject*  DecGongXun(PyRoleObject* self, PyObject* arg);
	PyObject*  DecKuaFuMoney(PyRoleObject* self, PyObject* arg);
	PyObject*  DecMoney(PyRoleObject* self, PyObject* arg);
	PyObject*  DecRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  DecReputation(PyRoleObject* self, PyObject* arg);
	PyObject*  DecRongYu(PyRoleObject* self, PyObject* arg);
	PyObject*  DecStarLucky(PyRoleObject* self, PyObject* arg);
	PyObject*  DecUnbindRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  DecUnbindRMB_Q(PyRoleObject* self, PyObject* arg);
	PyObject*  DecUnbindRMB_S(PyRoleObject* self, PyObject* arg);
	PyObject*  GetArtifactCuiLianHoleLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  GetArtifactMgr(PyRoleObject* self, PyObject* arg);
	PyObject*  GetBindRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  GetCampID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetColorCode(PyRoleObject* self, PyObject* arg);
	PyObject*  GetConsumeQPoint(PyRoleObject* self, PyObject* arg);
	PyObject*  GetContribution(PyRoleObject* self, PyObject* arg);
	PyObject*  GetCuiLian(PyRoleObject* self, PyObject* arg);
	PyObject*  GetCuiLian_MaxCnt(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDayBuyUnbindRMB_Q(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDayConsumeUnbindRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDayWangZheJiFen(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDragonCareerID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetDragonSoul(PyRoleObject* self, PyObject* arg);
	PyObject*  GetEarningExpBuff(PyRoleObject* self, PyObject* arg);
	PyObject*  GetEarningGoldBuff(PyRoleObject* self, PyObject* arg);
	PyObject*  GetElementBrandMgr(PyRoleObject* self, PyObject* arg);
	PyObject*  GetElementSpiritSkill(PyRoleObject* self, PyObject* arg);
	PyObject*  GetEquipmentMgr(PyRoleObject* self, PyObject* arg);
	PyObject*  GetExp(PyRoleObject* self, PyObject* arg);
	PyObject*  GetFTVIP(PyRoleObject* self, PyObject* arg);
	PyObject*  GetFightType(PyRoleObject* self, PyObject* arg);
	PyObject*  GetGongXun(PyRoleObject* self, PyObject* arg);
	PyObject*  GetGrade(PyRoleObject* self, PyObject* arg);
	PyObject*  GetHallowsMgr(PyRoleObject* self, PyObject* arg);
	PyObject*  GetHistoryContribution(PyRoleObject* self, PyObject* arg);
	PyObject*  GetJTProcessID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetJTeamID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetJobID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetKuaFuMoney(PyRoleObject* self, PyObject* arg);
	PyObject*  GetLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  GetMFZSkill(PyRoleObject* self, PyObject* arg);
	PyObject*  GetMFZSkillPointDict(PyRoleObject* self, PyObject* arg);
	PyObject*  GetMagicSpiritMgr(PyRoleObject* self, PyObject* arg);
	PyObject*  GetMoFaZhen(PyRoleObject* self, PyObject* arg);
	PyObject*  GetMoney(PyRoleObject* self, PyObject* arg);
	PyObject*  GetPet(PyRoleObject* self, PyObject* arg);
	PyObject*  GetPortrait(PyRoleObject* self, PyObject* arg);
	PyObject*  GetRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  GetReputation(PyRoleObject* self, PyObject* arg);
	PyObject*  GetRightMountID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetRongYu(PyRoleObject* self, PyObject* arg);
	PyObject*  GetSex(PyRoleObject* self, PyObject* arg);
	PyObject*  GetStar(PyRoleObject* self, PyObject* arg);
	PyObject*  GetStarLucky(PyRoleObject* self, PyObject* arg);
	PyObject*  GetStationID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetStationSoulSkill(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTalentEmptySize(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTalentMgr(PyRoleObject* self, PyObject* arg);
	PyObject*  GetTalentZDL(PyRoleObject* self, PyObject* arg);
	PyObject*  GetUnbindRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  GetUnbindRMB_Q(PyRoleObject* self, PyObject* arg);
	PyObject*  GetUnbindRMB_S(PyRoleObject* self, PyObject* arg);
	PyObject*  GetUnionID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetVIP(PyRoleObject* self, PyObject* arg);
	PyObject*  GetWeek(PyRoleObject* self, PyObject* arg);
	PyObject*  GetWingID(PyRoleObject* self, PyObject* arg);
	PyObject*  GetXinYueLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  GetZDL(PyRoleObject* self, PyObject* arg);
	PyObject*  GetZhuanShengHaloAddi(PyRoleObject* self, PyObject* arg);
	PyObject*  GetZhuanShengHaloLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  GetZhuanShengLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  IncBindRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  IncConsumeQPoint(PyRoleObject* self, PyObject* arg);
	PyObject*  IncContribution(PyRoleObject* self, PyObject* arg);
	PyObject*  IncDragonSoul(PyRoleObject* self, PyObject* arg);
	PyObject*  IncGongXun(PyRoleObject* self, PyObject* arg);
	PyObject*  IncHistoryContribution(PyRoleObject* self, PyObject* arg);
	PyObject*  IncKuaFuMoney(PyRoleObject* self, PyObject* arg);
	PyObject*  IncLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  IncMoney(PyRoleObject* self, PyObject* arg);
	PyObject*  IncReputation(PyRoleObject* self, PyObject* arg);
	PyObject*  IncRongYu(PyRoleObject* self, PyObject* arg);
	PyObject*  IncStarLucky(PyRoleObject* self, PyObject* arg);
	PyObject*  IncTarotHP(PyRoleObject* self, PyObject* arg);
	PyObject*  IncTouchGoldPoint(PyRoleObject* self, PyObject* arg);
	PyObject*  IncUnbindRMB_Q(PyRoleObject* self, PyObject* arg);
	PyObject*  IncUnbindRMB_S(PyRoleObject* self, PyObject* arg);
	PyObject*  IsKongJianDecennialRole(PyRoleObject* self, PyObject* arg);
	PyObject*  IsMonthCard(PyRoleObject* self, PyObject* arg);
	PyObject*  SetBindRMB(PyRoleObject* self, PyObject* arg);
	PyObject*  SetCampID(PyRoleObject* self, PyObject* arg);
	PyObject*  SetCanChatTime(PyRoleObject* self, PyObject* arg);
	PyObject*  SetCanLoginTime(PyRoleObject* self, PyObject* arg);
	PyObject*  SetConsumeQPoint(PyRoleObject* self, PyObject* arg);
	PyObject*  SetContribution(PyRoleObject* self, PyObject* arg);
	PyObject*  SetDragonCareerID(PyRoleObject* self, PyObject* arg);
	PyObject*  SetDragonSoul(PyRoleObject* self, PyObject* arg);
	PyObject*  SetEarningExpBuff(PyRoleObject* self, PyObject* arg);
	PyObject*  SetEarningGoldBuff(PyRoleObject* self, PyObject* arg);
	PyObject*  SetExp(PyRoleObject* self, PyObject* arg);
	PyObject*  SetFightType(PyRoleObject* self, PyObject* arg);
	PyObject*  SetGongXun(PyRoleObject* self, PyObject* arg);
	PyObject*  SetGrade(PyRoleObject* self, PyObject* arg);
	PyObject*  SetHistoryContribution(PyRoleObject* self, PyObject* arg);
	PyObject*  SetJTeamID(PyRoleObject* self, PyObject* arg);
	PyObject*  SetJobID(PyRoleObject* self, PyObject* arg);
	PyObject*  SetKuaFuMoney(PyRoleObject* self, PyObject* arg);
	PyObject*  SetMoney(PyRoleObject* self, PyObject* arg);
	PyObject*  SetReputation(PyRoleObject* self, PyObject* arg);
	PyObject*  SetRightMountID(PyRoleObject* self, PyObject* arg);
	PyObject*  SetRongYu(PyRoleObject* self, PyObject* arg);
	PyObject*  SetStarLucky(PyRoleObject* self, PyObject* arg);
	PyObject*  SetStationID(PyRoleObject* self, PyObject* arg);
	PyObject*  SetUnbindRMB_Q(PyRoleObject* self, PyObject* arg);
	PyObject*  SetUnbindRMB_S(PyRoleObject* self, PyObject* arg);
	PyObject*  SetUnionID(PyRoleObject* self, PyObject* arg);
	PyObject*  SetVIP(PyRoleObject* self, PyObject* arg);
	PyObject*  SetWeek(PyRoleObject* self, PyObject* arg);
	PyObject*  SetWingID(PyRoleObject* self, PyObject* arg);
	PyObject*  SetZDL(PyRoleObject* self, PyObject* arg);
	PyObject*  SetZhuanShengHaloLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  SetZhuanShengLevel(PyRoleObject* self, PyObject* arg);
	PyObject*  UpdateAndSyncMFZSkillPassive(PyRoleObject* self, PyObject* arg);
	PyObject*  CreateHeroProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  GetPropertyGather(PyRoleObject* self, PyObject* arg);
	PyObject*  GetPropertyMgr(PyRoleObject* self, PyObject* arg);
	PyObject*  PropertyIsValid(PyRoleObject* self, PyObject* arg);
	PyObject*  RemoveHeroProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetAllTarotProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetElementBrandBaseProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetElementSpiritProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalCardAtlasProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalDragonProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalFashionProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalHelpStationProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalMountAppProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalMountProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalQinmiGradeProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalQinmiProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalStationSoulItemProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalWStationBaseProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalWStationItemProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalWStationThousandProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalWeddingRingProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalWeddingRingSProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalWeddingRingSkillProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalWingProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetGlobalZhuanShengHaloBaseProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetMarryRingProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetSealProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetStationSoulProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  ResetTitleProperty(PyRoleObject* self, PyObject* arg);
	PyObject*  SyncAllProperty(PyRoleObject* self, PyObject* arg);
};

