/************************************************************************
角色数据限制
************************************************************************/
#pragma once
#include <vector>
#include "../GameEngine/GameEngine.h"

enum RoleAction
{
	DoNothing,								//当超出范围时，啥也不做
	DoIgnore,								//当超出范围时，忽视这次操作
	DoRound,								//当超出范围时，截取超出范围的部分
	DoKick									//当超出范围时，忽视这次操作并踢掉角色
};

class DataRule
{
public:
	DataRule();
	~DataRule();

public:
	void					SetChangeFun(PyObject* pyobj_BorrowRef);

public:
	GE::Uint16				uCoding;		//编码
	GE::Uint8				bSyncClient;	//是否同步客户端
	GE::Uint8				bLogEvent;		//是否记录日志
	GE::Int64				nMinValue;		//最小值
	GE::Int64				nMaxValue;		//最大值
	GE::Uint16				nMinAction;		//超出最小值的处理
	GE::Uint16				nMaxAction;		//超出最大值的处理
	GE::Uint32				uOverTime;		//过期时间
	PyObject*				pyChangeFun;	//改变了通知脚本
};

class RoleDataMgr
	: public GEControlSingleton<RoleDataMgr>
{
	GE_DISABLE_BOJ_CPY(RoleDataMgr);
	typedef std::vector<DataRule>			RuleVector;
public:
	RoleDataMgr();
	~RoleDataMgr();

public:
	void					SetInt64Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetDisperseInt32Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetInt32Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetInt16Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetInt8Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetDayInt8Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetInt1Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetDayInt1Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetDynamicInt64Rule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetFlagRule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetCDRule(const GE::Uint16 uIdx, DataRule& DR);
	void					SetTempInt64Rule(const GE::Uint16 uIdx, DataRule& DR);

	DataRule&				GetInt64Rule(const GE::Uint16 uIdx) {return this->m_Int64Rules.at(uIdx);}
	DataRule&				GetDisperseInt32Rule(const GE::Uint16 uIdx) {return this->m_DisperseInt32Rules.at(uIdx);}
	DataRule&				GetInt32Rule(const GE::Uint16 uIdx) {return this->m_Int32Rules.at(uIdx);}
	DataRule&				GetInt16Rule(const GE::Uint16 uIdx) {return this->m_Int16Rules.at(uIdx);}
	DataRule&				GetInt8Rule(const GE::Uint16 uIdx) {return this->m_Int8Rules.at(uIdx);}
	DataRule&				GetDayInt8Rule(const GE::Uint16 uIdx) {return this->m_DayInt8Rules.at(uIdx);}
	DataRule&				GetInt1Rule(const GE::Uint16 uIdx) {return this->m_Int1Rules.at(uIdx);}
	DataRule&				GetDayInt1Rule(const GE::Uint16 uIdx) {return this->m_DayInt1Rules.at(uIdx);}
	DataRule&				GetDynamicInt64Rule(const GE::Uint16 uIdx) {return this->m_DynamicInt64Rules.at(uIdx);}
	DataRule&				GetFlagRule(const GE::Uint16 uIdx) {return this->m_FlagRules.at(uIdx);}
	DataRule&				GetCDRule(const GE::Uint16 uIdx) {return this->m_CDRules.at(uIdx);}
	DataRule&				GetTempInt64Rule(const GE::Uint16 uIdx) {return this->m_TempInt64Rules.at(uIdx);}

	const GE::Uint16		GetInt64Size() {return this->m_uMaxInt64Index + 1;}
	const GE::Uint16		GetDisperseInt32Size() {return this->m_uMaxDisperseInt32Index + 1;}
	const GE::Uint16		GetInt32Size() {return this->m_uMaxInt32Index + 1;}
	const GE::Uint16		GetInt16Size() {return this->m_uMaxInt16Index + 1;}
	const GE::Uint16		GetInt8Size() {return m_uMaxInt8Index + 1;}
	const GE::Uint16		GetDayInt8Size() {return m_uMaxDayInt8Index + 1;}
	const GE::Uint16		GetClientInt8Size() {return this->m_uMaxClientInt8Size;}
	const GE::Uint16		GetInt1Size() { if ((m_uMaxInt1Index + 1) % 8 == 0){return m_uMaxInt1Index + 1;} else {return (m_uMaxInt1Index + 1) / 8 * 8 + 8;}}
	const GE::Uint16		GetDayInt1Size() {if ((m_uMaxDayInt1Index + 1) % 8 == 0){return m_uMaxDayInt1Index + 1;} else {return (m_uMaxDayInt1Index + 1) / 8 * 8 + 8;}}
	const GE::Uint16		GetFlagSize() {return this->m_uMaxFlagIndex + 1;}
	const GE::Uint16		GetTempInt64Size() {return this->m_uMaxTempInt64Index + 1;}
	const GE::Uint16		GetDynamicInt64Size() {return this->m_uMaxDynamicInt64Size;}
	const GE::Uint16		GetCDSize() {return this->m_uMaxCDSize;}
	const GE::Uint16		GetTempObjSize() {return this->m_uMaxTempObjSize;}

private:
	void					InitRule(const char* sAttrName, RuleVector& RV);

private:
	RuleVector				m_Int64Rules;
	RuleVector				m_DisperseInt32Rules;
	RuleVector				m_Int32Rules;
	RuleVector				m_Int16Rules;
	RuleVector				m_Int8Rules;
	RuleVector				m_DayInt8Rules;
	RuleVector				m_Int1Rules;
	RuleVector				m_DayInt1Rules;
	RuleVector				m_DynamicInt64Rules;
	RuleVector				m_FlagRules;
	RuleVector				m_CDRules;
	RuleVector				m_TempInt64Rules;

	// 用来记录最大的使用下标
	GE::Uint16				m_uMaxInt64Index;
	GE::Uint16				m_uMaxDisperseInt32Index;
	GE::Uint16				m_uMaxInt32Index;
	GE::Uint16				m_uMaxInt16Index;
	GE::Uint16				m_uMaxInt8Index;
	GE::Uint16				m_uMaxDayInt8Index;
	GE::Uint16				m_uMaxClientInt8Size;
	GE::Uint16				m_uMaxInt1Index;
	GE::Uint16				m_uMaxDayInt1Index;
	GE::Uint16				m_uMaxFlagIndex;
	GE::Uint16				m_uMaxTempInt64Index;

	GE::Uint16				m_uMaxDynamicInt64Size;
	GE::Uint16				m_uMaxCDSize;
	GE::Uint16				m_uMaxTempObjSize;

public:
	void					LoadPyData();
	GE::Uint16				uLastSaveUnixTimeIndex;				//最后保存时间下标
	GE::Uint16				uLastSaveProcessIDIndex;			//最后保存进程下标
	GE::Uint16				uOnlineTimesIndex;					//总的在线时间下标
	GE::Uint16				uLastClearDaysIndex;				//最后清零时间下标
	GE::Uint16				uOnlineTimesTodayIndex;				//今天在线时间下标
	GE::Uint16				uLoginOnlineTimeIndex;				//本次登录在线时间下标
	GE::Uint16				uMaxLoginDaysIndex;					//最大登录天数下标
	GE::Uint16				uContinueLoginDaysIndex;			//持续登录天数下标
	GE::Uint16				uMaxContinueLoginDaysIndex;			//最大持续登录天数下标
	GE::Uint16				uWPEIndex;							//封包计数下标
	GE::Uint16				uTiLiIndex;							//体力下标
	GE::Uint16				uTiLiMinuteIndex;					//体力时间下标
	GE::Uint16				uMoveSpeedIndex;					//移动速度下标
	GE::Uint16				uTempSpeedIndex;					//临时移动速度下标
	GE::Uint16				uMountSpeedIndex;					//坐骑移动速度下标
	GE::Uint16				uTempFlyStateIndex;					//临时飞行下标
	GE::Uint16				uCanChatTimeIndex;					//禁言时间下标
	GE::Uint16				uWorldChatIndex;					//世界聊天下标
	GE::Uint16				uFightStatusIndex;					//客户端是否在播放战斗状态下标
	GE::Uint16				uEXPIndex;							//经验下标
	GE::Uint16				uMoneyIndex;						//金钱下标
	GE::Uint16				uLastSceneIDIndex;					//保存场景ID
	GE::Uint16				uLastPosXIndex;						//保存坐标
	GE::Uint16				uLastPosYIndex;						//保存坐标
	GE::Uint16				uRoleAppStatusIndex;				//角色外观状态下标

	GE::Uint16				uHuangZuanIndex;					//黄钻下标
	GE::Uint16				uLanZuanIndex;						//蓝钻下标

	GE::Uint16				uCareerIndex;						//职业下标

	//3个特殊的外观枚举，暂时放在这里吧
	GE::Uint16				uEnumAppStatus;
	GE::Uint16				uEnumAppVersion1;
	GE::Uint16				uEnumAppVersion2;

};


