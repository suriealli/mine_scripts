#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumInt32")
#===============================================================================
# 角色Int32数组使用枚举
#===============================================================================
import cRoleDataMgr
from Common import CValue, Coding
from ComplexServer.Log import AutoLog
from Game.Role.Data import Enum

if "_HasLoad" not in dir():
	checkEnumSet = set()
	
def F(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient = False, sLogEvent = ""):
	'''
	设置数值规范
	@param uIdx:下标索引
	@param nMinValue:最小值
	@param nMinAction:超过最小值的处理
	@param nMaxValue:最大值
	@param nMaxAction:超过最大值的处理
	@param bSyncClient:数值改变了是否同步客户端
	@param sLogEvent:数值改变了是否记录日志
	'''
	assert uIdx < (Coding.RoleInt32Range[1] - Coding.RoleInt32Range[0])
	assert nMinValue >= CValue.MIN_INT32
	assert nMaxValue <= CValue.MAX_INT32
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumInt32 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	if sLogEvent: AutoLog.RegEvent(Coding.RoleInt32Range[0] + uIdx, sLogEvent)
	cRoleDataMgr.SetInt32Rule(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient, sLogEvent)

#===============================================================================
# 数组使用定义
#===============================================================================
enOnlineTimesToday = 0 #今日在线时间 秒
F(enOnlineTimesToday, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoIgnore)

enLastPublicSceneID = 1 #退出场景时保存的场景ID
F(enLastPublicSceneID, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

WorldChatCD = 2 #下次次世界聊天时间
UnionChatCD = 3 #下次公会聊天时间
TeamChatCD = 4 #下次队伍聊天时间
F(WorldChatCD, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)
F(UnionChatCD, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)
F(TeamChatCD, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

LastLeaveUpTotalOnlineTimes = 5 #上次升级的总在线时间
F(LastLeaveUpTotalOnlineTimes, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, False)

enReputation = 6 #声望
F(enReputation, 0, Enum.DoNothing, 99999999, Enum.DoNothing, True, "改变声望")

DayConsumeUnbindRMB = 7 #今日消耗的神石数量(包括充值神石和系统神石)
F(DayConsumeUnbindRMB, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

UnionID = 8 #公会ID
F(UnionID, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "公会ID改变")

ChuanYinChatCD = 9 #下次传音时间
F(ChuanYinChatCD, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

UnionContribution = 10 #公会贡献
F(UnionContribution, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "公会贡献改变 ")

TiLiMinute = 11 #体力计算时间
F(TiLiMinute, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

AllotID = 12 # 自分配ID
F(AllotID, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

TaortAllotID = 13#占卜命魂分配id
F(TaortAllotID, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

TaortHP = 14#占卜命魂命力
F(TaortHP, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "占卜命魂命力")

TarotRingExp = 15 #占卜光环经验
F(TarotRingExp, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "占卜光环经验")

SceneChatCD = 16 #区域聊天时间
F(SceneChatCD, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoRound, False)

MountExp = 17	#玩家坐骑培养经验
F(MountExp, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoRound, True, "改变玩家坐骑培养经验值")

FB_EvilHoleLastTick = 18 #恶魔深渊调用最后一个tick
F(FB_EvilHoleLastTick, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoRound, False)

SkillPoint = 19#技能点
F(SkillPoint, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "技能点")

HuangZuanKaiTongVersion = 20 #黄钻开通活动版本号(每次活动开启都要给这个版本号加一)
F(HuangZuanKaiTongVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

SealingExpID = 21 #宝石封灵的经验值
F(SealingExpID, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "改变宝石封灵经验值")

ArtifactSealExp = 22 #神器封印的经验值
F(ArtifactSealExp, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "改变神器封印经验值")

OnLineRewardTime = 23 #在线奖励时间(单位 ：秒数， 每领取一次，就会和总在线时间同步)
F(OnLineRewardTime, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

WonderSingleFill = 24	#精彩活动单笔充值
F(WonderSingleFill, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

WonderTotalFill = 25	#精彩活动每日累计充值
F(WonderTotalFill, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

WeddingRingExp = 26		#婚戒经验
F(WeddingRingExp, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

TalentAllotId = 27	#天赋卡自动分配ID
F(TalentAllotId, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

WishPoolScore = 28	#许愿池积分
F(WishPoolScore, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

BraveHeroScore = 29	#勇者英雄坛积分
F(BraveHeroScore, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "勇者英雄坛积分")

WingCultivateTimes = 30	#翅膀培养次数，每日清零
F(WingCultivateTimes, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

PetCultivateTimes = 31	#宠物培养次数，每日清零
F(PetCultivateTimes, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

OnLineRewardTime_Beta = 32 #北美封测在线奖励时间
F(OnLineRewardTime_Beta, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

MountCultivateTimes = 33	#坐骑培养次数，每日清零
F(MountCultivateTimes, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

ProjectWishTimes = 34	#专题活动，每日许愿次数
F(ProjectWishTimes, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DayBuyUnbindRMB_Q = 35		#今日充值神石数
F(DayBuyUnbindRMB_Q, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DayExtraAFLatteryRecord = 36	#今日中秋搏饼额外次数领取记录 （id符合1,2,4,8...2**n）
F(DayExtraAFLatteryRecord, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

ProjectWingTimes = 37	#专题活动，每日羽翼培养次数
F(ProjectWingTimes, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DragonTrainSoul = 38	#驯龙系统龙灵数量
F(DragonTrainSoul, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "改变驯龙龙灵数量")

StarLucky = 39			#星灵系统星运
F(StarLucky, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

NationFBDayExp = 40		#国庆副本每日获取的经验
F(NationFBDayExp, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

OnLineTimeToday = 41	#每日累计在线时间(必须和总在线时间做逻辑才可以得出)
F(OnLineTimeToday, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

LanZuanKaiTongVersion = 42 #蓝钻开通活动版本号(每次活动开启都要给这个版本号加一)
F(LanZuanKaiTongVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

DailyMountLotteryTimes = 43 #每日天马行空抽奖次数（每日重置）
F(DailyMountLotteryTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "天马行空抽奖次数改变")

DailyMountLotteryAccTimes = 44 #每日天马行空未抽中特殊奖励累积次数（每日重置，抽中特殊奖励重置）
F(DailyMountLotteryAccTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "天马行空累积未抽中特殊奖励次数")

DayBuyUnbindRMB_Q_1 = 45	#版本修复后可复用（暂不可用）----------------------------------
F(DayBuyUnbindRMB_Q_1, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DayExtraQQHallRecord = 46	#今日大厅搏饼额外次数领取记录 （id符合1,2,4,8...2**n）
F(DayExtraQQHallRecord, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

Qinmi = 47					#亲密度
F(Qinmi, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "亲密度")

JTGold = 48#组队竞技场荣誉(旧，金券)
F(JTGold, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "组队竞技场荣誉(旧，金券)")

JTExp = 49#组队竞技场功勋
F(JTExp, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "组队竞技场功勋")

DragonHoleDailyExp = 50		#勇闯龙窟每日获得经验
F(DragonHoleDailyExp, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "勇闯龙窟每日获得经验")

TGRechargeRewardMaxToday = 51	#充值送豪礼今日最大单笔充值RMB(每日重置)
F(TGRechargeRewardMaxToday, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

TGRechargeRewardRecord = 52 	#充值送豪礼今日已领取次数记录(每日重置)
F(TGRechargeRewardRecord, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DayBuyUnbindRMB_Q_2 = 53	#版本修复后可复用（暂不可用）----------------------------------
F(DayBuyUnbindRMB_Q_2, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

LoveTogether_OnlineRewardRecord = 54	#爱在一起在线奖励领取记录(rewardIndex符合1,2,4,8...)
F(LoveTogether_OnlineRewardRecord, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

FeastWheel_RechargeRewardRecord = 55	#盛宴摩天轮充值次数兑换记录
F(FeastWheel_RechargeRewardRecord, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DayConsumeUnbindRMB_1 = 56 #版本修复后可复用（暂不可用）----------------------------------
F(DayConsumeUnbindRMB_1, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DayBuyUnbindRMB_Q_3 = 57	#版本修复后可复用（暂不可用）----------------------------------
F(DayBuyUnbindRMB_Q_3, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

HaoHuaLanZuanKaiTongVersion = 58 #豪华蓝钻开通活动版本号(每次活动开启都要给这个版本号加一)
F(HaoHuaLanZuanKaiTongVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

FashionHoleExp = 59		#时装光环经验
F(FashionHoleExp, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "时装光环经验")

ChristmasConsumeExp = 60	#圣诞嘉年华消费积分
F(ChristmasConsumeExp, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

UnionHistoryContribution = 61 #公会历史贡献
F(UnionHistoryContribution, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

EquipmentWashNum = 62	#装备洗练度
F(EquipmentWashNum, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DayBuyUnbindRMB_Q_4 = 63	#版本修复后可复用（暂不可用）----------------------------------
F(DayBuyUnbindRMB_Q_4, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

Holiday_RechargeRewardRecord = 64 	#元旦充值奖励_抽奖次数兑换记录（每日重置）
F(Holiday_RechargeRewardRecord, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

NewYearScore = 65		#新年乐翻天积分
F(NewYearScore, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "新年折扣汇积分")

NewYearConsume = 66		#新年乐翻天消费 
F(NewYearConsume, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "新年乐翻天消费")

QQHallLotteryVersion = 67 #大厅博饼开通活动版本号(每次活动开启都要给这个版本号加一)
F(QQHallLotteryVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

SuperVIPExp = 68			#超级VIP经验
F(SuperVIPExp, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "超级VIP经验")

SuperVIPPoint = 69			#超级VIP积分
F(SuperVIPPoint, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "超级VIP积分")

KuaFuJJCElectionScore = 70	#跨服竞个人技场海选积分
F(KuaFuJJCElectionScore, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "跨服竞技场海选积分")

KuaFuJJCFinalsScore = 71	#跨服个人竞技场决赛积分
F(KuaFuJJCFinalsScore, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "跨服竞技场决赛积分")

KuaFuMoney = 72			#跨服币
F(KuaFuMoney, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "改变跨服币")

LastChargeSeconds = 73	#最后一次充值的时间戳(必须更新后充值一下才会有数据，这个值才会有意义(此值为0时当作没有充值))
F(LastChargeSeconds, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "最后一次充值的时间戳")

LanternFestivalPoint = 74	#元宵节点灯积分
F(LanternFestivalPoint, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "元宵节点灯积分")

LanternFestivalPointDaily = 75	#元宵节点灯积分（当天获得的积分,每日重置 ）
F(LanternFestivalPointDaily, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

KuaFuJJCVersionID = 76	#跨服个人竞技场版本号
F(KuaFuJJCVersionID, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

DayGlamourExp = 77		#魅力情人节-今日魅力值
F(DayGlamourExp, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "今日魅力值")

HistoryGlamourExp = 78	#魅力情人节-历史总魅力值
F(HistoryGlamourExp, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "历史总魅力值")

DayConsumeUnbindRMB_Q = 79	#每日消耗的充值神石
F(DayConsumeUnbindRMB_Q, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

ValentineDayVersion = 80 	#魅力情人节活动版本号
F(ValentineDayVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

GMScore = 81		#GM积分
F(GMScore, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

LianChongRebateVersion = 82		#连充返利活动角色身上数据版本号
F(LianChongRebateVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

ShenWangBaoKuVersion = 83		#神王宝库角色身上数据版本号
F(ShenWangBaoKuVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "神王宝库活动版本号")

ShenWangBaoKuPoint = 84		#神王宝库积分
F(ShenWangBaoKuPoint, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "神王宝库积分")

ZaiXianJiangLiVersion = 85		#新在线奖励活动角色身上数据版本号
F(ZaiXianJiangLiVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

PetEvoTimes = 86		#宠物修行次数
F(PetEvoTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

FashionUpStarTimes = 87		#时装升星消耗时装精华
F(FashionUpStarTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

FashionUpOrderTimes = 88		#时装升阶消耗时装之魄
F(FashionUpOrderTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

StarGirlLevelUpTimes = 89		#星灵升级消耗次数
F(StarGirlLevelUpTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

StarGirlStarTimes = 90		#星灵升星消耗次数
F(StarGirlStarTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

DragonVeinLevelTimes = 91	#龙脉升级消耗次数
F(DragonVeinLevelTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

DragonVeinEvoTimes = 92	#龙脉升级消耗次数
F(DragonVeinEvoTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

TitleLevelUpTimes = 93	#称号升级消耗次数
F(TitleLevelUpTimes, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

YeYouJieRechareRMB = 94	#页游节充值返利活动当天充值的神石数量
F(YeYouJieRechareRMB, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

None_1 = 95	#可复用
F(None_1, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

MountTempExp = 96	#坐骑增加的临时经验值
F(MountTempExp, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

LatestFillRMB = 97	#每日充值的神石，领取完奖励须扣除对应的神石(这个版本又改成不扣了)
F(LatestFillRMB, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

ZheKouHuiUsedUnbindRMB = 98 #公测折扣汇抵用的今日消费神石数
F(ZheKouHuiUsedUnbindRMB, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

WZRRRefreshVersion = 99	#王者公测充值返利转盘刷新版本
F(WZRRRefreshVersion, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

KaifuTargetBuyRMB = 100	#七日目标累计充值
F(KaifuTargetBuyRMB, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

KaifuTargetConsume = 101	#七日目标累计消费
F(KaifuTargetConsume, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

ShenMiBaoXiangVersion = 102		#神秘宝箱活动角色身上数据版本号
F(ShenMiBaoXiangVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

PassionActVersion = 103 	#激情活动版本号
F(PassionActVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

PreciousStoreVersion = 104		#珍宝商店角色身上数据版本号
F(PreciousStoreVersion, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "珍宝商店版本号")

StationSoulTempExpLastSecs = 105	#阵灵进阶进度值超时时间戳
F(StationSoulTempExpLastSecs, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "阵灵进阶进度值超时时间戳")

AntiUnlockTimestamp = 106		#防沉迷离线超时解锁时间戳 跨天重置
F(AntiUnlockTimestamp, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

CTTPoint = 107		#虚空幻境幻境点
F(CTTPoint, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "虚空幻境幻境点")

AtifactHalo = 108		#神器淬炼光环经验
F(AtifactHalo, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "神器淬炼光环")

LostSceneScore = 109			#迷失之境冒险点
F(LostSceneScore, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "迷失之境冒险点")

TouchGoldPoint = 110			#点石成金积分
F(TouchGoldPoint, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "点石成金积分")

HallowsSealExp = 111 #圣器封印的经验值
F(HallowsSealExp, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "改变圣器封印经验值")

TJHC_ConsumeUnbindRMB_Q = 112	#天降横财累计消耗的充值神石  = TJHC_ConsumeUnbindRMB_Q + DayConsumeUnbindRMB_Q
F(TJHC_ConsumeUnbindRMB_Q, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

CatchingFish = 113				#捕鱼达人的积分
F(CatchingFish, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "捕鱼达人积分")

TempWedRingExp = 114			#临时婚戒经验
F(TempWedRingExp, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True)

CardAtlasChip = 115				#卡牌碎片
F(CardAtlasChip, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "卡牌碎片")

ElementalEssenceAmount = 116			#元素精华数量
F(ElementalEssenceAmount, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "元素精华数量")


ElementSpiritCultivateCnt = 118			#元素精华消耗总数
F(ElementSpiritCultivateCnt, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "元素精华消耗总数")


ElementBrandAllotID = 119				#元素印记分配id
F(ElementBrandAllotID, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

SealAmounts = 120						#圣印纹章数量
F(SealAmounts, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "圣印纹章数量")

SealLiLianAmounts = 121					#圣印历练值数量
F(SealLiLianAmounts, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "圣印历练值数量")


SpringHongBaoRMB = 122			#红包闹新春每日发红包神石数
F(SpringHongBaoRMB, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "公会每日发红包神石数")


ChunJieYuanXiaoHeight = 123				#春节元宵高度
F(ChunJieYuanXiaoHeight, 0, Enum.DoRound, CValue.MAX_INT32, Enum.DoRound, True, "春节元宵高度")

KuafuZhanchangChatCD = 124 #跨服战场阵营聊天
F(KuafuZhanchangChatCD, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoRound, False)

Hallows_Latest_Times = 125	#圣器洗练日洗练次数，每日清零
F(Hallows_Latest_Times, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoRound, True)

ElementSoul_EXP = 126			#铸灵总EXP
F(ElementSoul_EXP, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoRound, True, "铸灵总EXP")