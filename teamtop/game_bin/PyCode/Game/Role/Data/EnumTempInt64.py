#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumTempInt64")
#===============================================================================
# 角色临时Int64数组
#===============================================================================
import cRoleDataMgr
from Common import CValue, Coding
from Game.Role.Data import Enum


if "_HasLoad" not in dir():
	checkEnumSet = set()

def F(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient = False):
	'''
	设置数值规范
	@param uIdx:下标索引
	@param nMinValue:最小值
	@param nMinAction:超过最小值的处理
	@param nMaxValue:最大值
	@param nMaxAction:超过最大值的处理
	@param bSyncClient:数值改变了是否同步客户端
	'''
	assert uIdx < (Coding.RoleTempInt64Range[1] - Coding.RoleTempInt64Range[0])
	
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumTempInt64 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	
	cRoleDataMgr.SetTempInt64Rule(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient)

#===============================================================================
# 数组使用定义
#===============================================================================
enWPE = 0 #封包检测
F(enWPE, 0, Enum.DoIgnore, 10, Enum.DoKick)

MoveSpeed = 1 #原始速度
F(MoveSpeed, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

MountSpeed = 2 #坐骑速度(优先级低于临时速度，高于原始速度)
F(MountSpeed, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

TempSpeed = 3 #临时速度(最高优先级)(0：取下一级速度， 大于0： 临时速度)
F(TempSpeed, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

TempFlyState = 4 #临时飞行状态(0： 取正常飞行状态， 1：临时可以飞行， 2：临时不能飞行)
F(TempFlyState, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

RoleAppStatus = 5 #角色外观状态
F(RoleAppStatus, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

TempFightType = 6#临时战斗类型
F(TempFightType, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

ChatCnt = 7 #本次登录聊天次数
F(ChatCnt, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

QVIP = 8 #本次登录QQVIP
F(QVIP, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

LoginOnlineTime = 9#本次登录在线时间
F(LoginOnlineTime, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

SaoDangTickId = 10 #恶魔深渊扫荡临时记录tickID
F(SaoDangTickId, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

MainTaskFightStep = 11#临时主线任务战斗步骤
F(MainTaskFightStep, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

RoleLoginTimesSec = 12#角色登录的时间
F(RoleLoginTimesSec, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

Is3366 = 13#是否是3366平台的人
F(Is3366, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

GrowLevel3366 = 14#3366平台成长等级
F(GrowLevel3366, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)


TotalWingZDL = 15#临时的翅膀战斗
F(TotalWingZDL, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

TotalPetZDL = 16#临时的宠物战斗力
F(TotalPetZDL, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

IsGameUnoin = 17 #是否是游戏联盟的人
F(IsGameUnoin, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

IsGameUnionAiWan = 18#游戏联盟爱玩渠道
F(IsGameUnionAiWan, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

IsGameUnionQQGJ = 19#游戏联盟QQ管家渠道
F(IsGameUnionQQGJ, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

TotalWeddingRingZDL = 20#婚戒战斗力(基础属性， 洗练属性，夫妻技能)
F(TotalWeddingRingZDL, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

KickTickID = 21
F(KickTickID, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, False)

FashionClothes = 22	#时装衣服
F(FashionClothes, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, True)

FashionHat = 23	#时装帽子
F(FashionHat, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, True)

FashionWeapons = 24	#时装武器
F(FashionWeapons, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, True)

QQXinShouCardFlag = 25 #qq新手卡
F(QQXinShouCardFlag, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, True)

QQMiniClient = 26	#腾讯微端登录
F(QQMiniClient, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, True)

DragonTrainZDL = 27#临时的训龙战斗力
F(DragonTrainZDL, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

IsQQGame = 28	#QQ游戏大厅
F(IsQQGame, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

JT_ProcessID = 29#跨服组队竞技场专用 本服进程ID
F(JT_ProcessID, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

PackageIsUnlock = 30#背包是否解锁
F(PackageIsUnlock, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

TT_AutoInvite = 31#组队爬塔是否自动接受邀请
F(TT_AutoInvite, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

UnionKuaFuWarGateID = 32#公会跨服争霸门ID
F(UnionKuaFuWarGateID, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

ZaiXianJiangLiTickId = 33	#新在线奖励在线计时器
F(ZaiXianJiangLiTickId, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

IsQzone = 34 #是否是空间的人
F(IsQzone, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

IsPengYou = 35 #是否是朋友网的人
F(IsPengYou, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

ZaiXianLuxuryRewardTickId = 36	#在线有豪礼计时器
F(ZaiXianLuxuryRewardTickId, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, False)

IsWebsite = 37		#是否官网
F(IsWebsite, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, False)

None_38 = 38	#可以复用---
F(None_38, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

StationSoulExpTickId = 39	#阵灵突破进度值清理tickId
F(StationSoulExpTickId, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, False)

AntiTickId = 40				#防沉迷tickId
F(AntiTickId, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, False)

PassionOnlineGiftTickId = 41	#激情活动在线有礼tickId
F(PassionOnlineGiftTickId, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, False)

QiangHongBaoTickId = 42	#激情活动在线有礼tickId
F(QiangHongBaoTickId, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, False)

CTT_AutoInvite = 43	#虚空幻境是否自动组队
F(CTT_AutoInvite, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, True)

HuoYueDaLiTickId = 44	#中秋活跃大礼tickId
F(HuoYueDaLiTickId, 0, Enum.DoNothing, CValue.MAX_INT64, Enum.DoNothing, False)

IsDomesticType = 45		#国内联运类型（1.是YY联运）
F(IsDomesticType, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)

IsRumskOKGames = 46		#俄罗斯OK
F(IsRumskOKGames, 0, Enum.DoNothing, CValue.MAX_UINT32, Enum.DoNothing, True)
