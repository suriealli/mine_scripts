#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumInt8")
#===============================================================================
# 角色Int8数组使用枚举
#===============================================================================
import cRoleDataMgr
from Common import CValue, Coding
from ComplexServer.Log import AutoLog
from Game.Role.Data import Enum

if "_HasLoad" not in dir():
	checkEnumSet = set()
	
def F(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient=False, sLogEvent=""):
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
	assert uIdx < (Coding.RoleInt8Range[1] - Coding.RoleInt8Range[0])
	assert nMinValue >= CValue.MIN_INT8
	assert nMaxValue <= CValue.MAX_INT8
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumInt8 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	
	if sLogEvent: AutoLog.RegEvent(Coding.RoleInt8Range[0] + uIdx, sLogEvent)
	cRoleDataMgr.SetInt8Rule(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient, sLogEvent)

#===============================================================================
# 数组使用定义
#===============================================================================
enStationID = 0 #阵位ID -- 初始化为3
F(enStationID, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

UnionJobID = 1 #公会职位ID
F(UnionJobID, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

JJC_Challenge_Cnt = 2 #竞技场挑战次数
F(JJC_Challenge_Cnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

InviteReward = 3 #之前的好友邀请和分享抽奖次数, 已移到I16中, 不再使用
F(InviteReward, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

UnionGetGold = 4			#领取公会金宝箱
UnionGetSilver = 5			#领取公会银宝箱
UnionGetCopper = 6			#领取公会铜宝箱
F(UnionGetGold, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(UnionGetSilver, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(UnionGetCopper, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

PackageOpenTimes = 7#背包扩充次数
F(PackageOpenTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "背包扩充")

TarotEquipmentPackageSize = 8 #塔罗牌当前可装备的最大数量
F(TarotEquipmentPackageSize, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True, "塔罗牌当前可装备的最大数量")

TarotIndex = 9 #当前占卜的Index
F(TarotIndex, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

Week = 10 #保存当前是第几周
F(Week, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore)

QTaskFinish = 11 #QQ交叉推广任务奖励步骤（第几bit表明第几个任务领取过奖励）
F(QTaskFinish, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore)

QQVIPLevelIndex = 12	#当前还未领取的QQvip等级礼包
F(QQVIPLevelIndex, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

LegionDays = 13		#玩家登录天数，用于登录奖励
F(LegionDays, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

QTaskReward = 14		#QQ交叉推广任务完成步骤（第几bit表明地几个任务已经完成）
F(QTaskReward, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore)

LastMountID = 15			#上一次骑乘的坐骑ID
F(LastMountID, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

SealingSpiritID = 16 #宝石封灵等级
F(SealingSpiritID, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True, "宝石封灵等级")

WingId = 17 #翅膀ID
F(WingId, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

UnionFBCnt = 18 #公会副本次数
F(UnionFBCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

InviteSuccess = 19		#成功邀请好友个数
F(InviteSuccess, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

EarningExpBuff = 20 #城主收益buff(经验加成)
F(EarningExpBuff, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

EarningGoldBuff = 21 #城主收益buff(金钱加成)
F(EarningGoldBuff, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

FiveGiftFirst = 22		#五重礼第一重奖励(首充)
FiveGiftSecond = 23		#五重礼第二重奖励(福缘抽奖)
FiveGiftThird = 24		#五重礼第三重奖励(升级)
FiveGiftForth = 25		#五重礼第四重奖励(月卡)
FiveGiftFifth = 26		#五重礼第五重奖励(购买礼包)
F(FiveGiftFirst, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(FiveGiftSecond, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(FiveGiftThird, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(FiveGiftForth, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(FiveGiftFifth, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

ArtifactSealingID = 27 #神器封印等级
F(ArtifactSealingID, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True, "神器封印等级")

TarotRingLevel = 28#占卜光环等级
F(TarotRingLevel, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True, "占卜光环等级")

OnLineRewardType = 29	#在线奖励类型
F(OnLineRewardType, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

UnionFBId = 30			#公会副本ID
F(UnionFBId, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

RushLevelTop = 31		#冲级排名第一名奖励
RushLevel44 = 32		#冲级排名44级奖励
RushLevel46 = 33		#冲级排名46级奖励
RushLevel48 = 34		#冲级排名48级奖励
F(RushLevelTop, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)
F(RushLevel44, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)
F(RushLevel46, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)
F(RushLevel48, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

PetType = 35		#宠物类型（改为宠物外观）
F(PetType, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

PetFollowType = 36	#宠物跟随类型
F(PetFollowType, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

AppPanelLoginDays = 37	#QQ应用面板登陆天数
F(AppPanelLoginDays, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

UnionFBBuyCnt = 38	#公会副本购买次数
F(UnionFBBuyCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

QQTipsFlag = 39	#QQ会员tips礼包状态   1：可以领取   ２：已经领取
F(QQTipsFlag, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

QQLZLevelIndex = 40	#当前还未领取的QQ蓝钻等级礼包
F(QQLZLevelIndex, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

DragonChangeJobCnt = 41	#神龙转职次数
F(DragonChangeJobCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

DragonCareerID = 42	#神龙职业ID
F(DragonCareerID, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

WeiboZoneIndex = 43	#微博空间分享索引
F(WeiboZoneIndex, -1, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

HeavenUnRMBIndex = 44	#天降神石当前可摇奖的档次
F(HeavenUnRMBIndex, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

MarryStatus = 45	#结婚状态(0-未婚, 1-订婚, 2-预定婚礼, 3-完婚, 4-婚礼开始)
F(MarryStatus, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

WedingRingSoulID = 46	#已激活的婚戒戒灵最大ID
F(WedingRingSoulID, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

DayFirstPayDays = 47		#每日首充的天数
F(DayFirstPayDays, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

DayFirstPayReward1 = 48		#每日首充1天奖励
DayFirstPayReward2 = 49		#每日首充2天奖励
DayFirstPayReward3 = 50		#每日首充3天奖励
DayFirstPayReward4 = 51		#每日首充4天奖励
DayFirstPayReward5 = 52		#每日首充5天奖励
F(DayFirstPayReward1, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(DayFirstPayReward2, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(DayFirstPayReward3, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(DayFirstPayReward4, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
F(DayFirstPayReward5, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GameUnionAiwan = 53		#游戏联盟爱玩登录天数
F(GameUnionAiwan, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoNothing, True)

GameUnionQQGJ = 54		#游戏联盟QQ管家登录天数
F(GameUnionQQGJ, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoNothing, True)

HeavenUnRMBIndex2 = 55	#天降神石2当前可摇奖的档次
F(HeavenUnRMBIndex2, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

OnLineRewardType_Beta = 56	#北美封测在线奖励类型
F(OnLineRewardType_Beta, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

AFDailyLiBaoID = 57 	#中秋登陆礼包领取id
F(AFDailyLiBaoID, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

AFLatterySpecialNum = 58 	#中秋当前搏饼次数--特殊次数(活动期间神石充值兑换)
F(AFLatterySpecialNum, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

QQHuangZuanKaiTongTimes = 59 	#黄钻开通次数
F(QQHuangZuanKaiTongTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "黄钻开通次数")

QQHZGift_UsedNum_Roll = 60	#黄钻转大礼 已领取奖励次数
F(QQHZGift_UsedNum_Roll, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "黄钻转大礼领奖次数")

QQHZGift_UsedNum_Offer = 61		#黄钻献大礼 已领取奖励次数
F(QQHZGift_UsedNum_Offer, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "黄钻献大礼领奖次数")

WR3366_RewardRecord = 62	# 3366一周豪礼 领取记录
F(WR3366_RewardRecord, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

StarGirlFollowId = 63	#星灵跟随ID
F(StarGirlFollowId, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

StarGirlFightId = 64	#出战的星灵ID
F(StarGirlFightId, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

QQLanZuanKaiTongTimes = 65 	#蓝钻开通次数
F(QQLanZuanKaiTongTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻开通次数")

QQLZKaiTong_UsedTimes_Roll = 66	#蓝钻转大礼 已领取奖励次数
F(QQLZKaiTong_UsedTimes_Roll, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻转大礼领奖次数")

QinmiGrade = 67					#亲密品阶
F(QinmiGrade, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "亲密度品阶")

QQLZGift_UsedNum_Offer = 68		#蓝钻献大礼 已领取奖励次数
F(QQLZGift_UsedNum_Offer, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻献大礼领奖次数")

StepByStepChestIndex = 69		#步步高升当前已经打开的最大宝箱index
F(StepByStepChestIndex, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "步步高升当前已经打开的最大宝箱index")

ZumaCnt = 70		#祖玛次数
F(ZumaCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "祖玛次数")

QQLZLuxuryGiftRewardRecord = 71		#蓝钻豪华六重礼领取记录
F(QQLZLuxuryGiftRewardRecord, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻豪华六重礼领取记录")

QQHaoHuaLanZuanKaiTongTimes = 72 	#豪华蓝钻开通次数
F(QQHaoHuaLanZuanKaiTongTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "豪华蓝钻开通次数")

ZumaCollectClearMonth = 73			#祖玛收集清理的月份
F(ZumaCollectClearMonth, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

FashionHaloLevel = 74			#时装光环等级
F(FashionHaloLevel, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "时装光环等级")

QQHK_Version = 75
F(QQHK_Version, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, False, "qq管家活动版本号")

QQLZLuxury_UsedTimes_Roll = 76	#豪华蓝钻转大礼——已抽奖次数
F(QQLZLuxury_UsedTimes_Roll, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "豪华蓝钻转大礼抽奖次数改变")

QQHZRoll_UsedTimes_Roll = 77	#黄钻兑好礼——已抽奖次数
F(QQHZRoll_UsedTimes_Roll, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "黄钻兑好礼抽奖次数")

GoddessCardTurnOverCnt = 78	#女神卡牌翻牌次数
F(GoddessCardTurnOverCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

QQXinYueVipLevel = 79	#qq心悦用户vip等级
F(QQXinYueVipLevel, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "qq心悦用户vip等级")

HoneymoonStatus = 80	#结婚蜜月状态(0-没有度蜜月, 1,2-蜜月档次, 3-完成蜜月)
F(HoneymoonStatus, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)


QQLZRoll_UsedTimes_Roll = 81	#蓝钻兑好礼——已抽奖次数
F(QQLZRoll_UsedTimes_Roll, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻兑好礼抽奖次数")

OpenYearContinueLoginDay = 82	#开年活动连续登陆天数
F(OpenYearContinueLoginDay, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

OpenYearTotalLoginDay = 83	#开年活动累计登陆天数
F(OpenYearTotalLoginDay, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

UnionExploreCnt = 84	#公会魔域探秘行动力
F(UnionExploreCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

OldServerVip = 85	#老服回流记录老服的VIP等级
F(OldServerVip, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "老玩家回流原VIP等级")

QQLZHappyDraw_UsedTimes = 86	#蓝钻转转乐已抽次数
F(QQLZHappyDraw_UsedTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻转转乐已抽次数")

QQHZHappyDraw_UsedTimes = 87	#黄钻转转乐已抽次数
F(QQHZHappyDraw_UsedTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "黄钻转转乐已抽次数")

ZaiXianJiangLiOnLineMins = 88 #新在线奖励_当前有效在线分钟
F(ZaiXianJiangLiOnLineMins, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

YeYouJieWarmupLoginDays = 89 #页游节预热活动期间角色累计登录天数
F(YeYouJieWarmupLoginDays, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ZaiXianLuxuryRewardOnLineMins = 90 #在线有豪礼_当前有效在线分钟
F(ZaiXianLuxuryRewardOnLineMins, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

WangZheRechargeRebateWaveIndex = 91 #公测充值返利转盘奖励波次
F(WangZheRechargeRebateWaveIndex, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

WangZheRechargeRebateLevelRangeId = 92 #公测充值返利转盘奖励等级段
F(WangZheRechargeRebateLevelRangeId, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

FTOldRoleBackSingUpRemedyCnt = 93 #【繁体版】老玩家回流补签到次数
F(FTOldRoleBackSingUpRemedyCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

WaiGua = 94 #使用外挂次数
F(WaiGua, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, False, "检测到使用外挂的次数")

DuanWuJieGoldZongzi = 95 #端午节黄金粽子的方案id
F(DuanWuJieGoldZongzi, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

QQLZBaoXiangTimes = 96 	#蓝钻宝箱开启次数
F(QQLZBaoXiangTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻宝箱开启次数")

PassionGiftAccuCnt = 97		#激情有礼 累计达成任务次数
F(PassionGiftAccuCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

QQLZTianMa = 98						#天马流星领取状态 0：宝箱未全部开启，1：可以领取，2：已有坐骑
F(QQLZTianMa, 0, Enum.DoNothing, 2, Enum.DoNothing, True)

ShenMiBaoXiang = 99						#神秘宝箱已经领取个数
F(ShenMiBaoXiang, 0, Enum.DoNothing, 4, Enum.DoNothing, True)

FashionWardrobeLevel = 100		#时装衣柜等级
F(FashionWardrobeLevel, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "时装衣柜等级")

DKCNewMaxLevel = 101		#新龙骑试炼历史最高关卡
F(DKCNewMaxLevel, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "新龙骑试炼历史最高关卡")

PassionTurntableTimes = 102		#激情活动幸运转盘当前次数
F(PassionTurntableTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "激情活动幸运转盘当前次数")

AntiVerifiedState = 103		#防沉迷状态 0-未验证 1-已提交未满18岁 2-已认证
F(AntiVerifiedState, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "防沉迷状态")

PassionOnlineGiftLeftCnt = 104		#激情活动在线有礼剩余翻牌子次数
F(PassionOnlineGiftLeftCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "激情活动在线有礼剩余翻牌子次数")

QQLZXunBao = 105			#蓝钻寻宝掷骰子次数
F(QQLZXunBao, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻寻宝掷骰子次数")

QQLZXunBaoStep = 106		#蓝钻寻宝走过的步数
F(QQLZXunBaoStep, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "蓝钻寻宝走过的步数")

HuoYueDaLi_EffectStep = 107		#活跃大礼可用步数
F(HuoYueDaLi_EffectStep, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "活跃大礼可用步数")

HuoYueDaLi_NowIndex = 108		#活跃大礼当前所处位置
F(HuoYueDaLi_NowIndex, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "活跃大礼当前所处位置")

ZhongQiuShouChong_RechargeDays = 109		#中秋首冲总天数
F(ZhongQiuShouChong_RechargeDays, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "中秋首冲总天数")

ZhongQiuShangYue_RewardSuitID = 110		#中秋赏月神石抽奖奖励套ID
F(ZhongQiuShangYue_RewardSuitID, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "中秋赏月神石抽奖奖励套ID")

AtifactHaloLevel = 111		#神器淬炼光环等级
F(AtifactHaloLevel, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "神器淬炼光环等级")

PassionLianChongGiftDays = 112		#激情活动连冲豪礼连充天数
F(PassionLianChongGiftDays, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "激情活动连冲豪礼连充天数")

DETopicTodayTopicId = 113		#专题转盘今日专题ID
F(DETopicTodayTopicId, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "专题转盘今日专题ID")

HallowsSealingSpiritID = 114 #圣器封灵等级
F(HallowsSealingSpiritID, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True, "圣器封灵等级")

ChongZhiDays = 115			# 感恩节期间累计充值天数
F(ChongZhiDays, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "充值累计天数")

ElementSpiritSkillType = 116		#元素之灵技能类型
F(ElementSpiritSkillType, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "元素之灵技能类型")

Game2048Cnt = 117			#2048次数
F(Game2048Cnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ElementSpiritFollow = 118		#元素之灵跟随
F(ElementSpiritFollow, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)


ChunJieYuanXiaoRaiseTimes = 119		#花灯提升次数
F(ChunJieYuanXiaoRaiseTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True,"花灯提升次数")

QQLZFeedBackTimes = 120 		#蓝钻回馈大礼抽奖次数
F(QQLZFeedBackTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

QQLZFeedBackRewardGroup = 121 	#蓝钻回馈大礼当前奖励组
F(QQLZFeedBackRewardGroup, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ElementSoulVisionId = 122		#元素幻化外形ID
F(ElementSoulVisionId, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "元素幻化外形ID")

ElementTalentSkillId = 123		#元素天赋技能ID
F(ElementTalentSkillId, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "元素天赋技能ID")

ElementVisionFollow = 124	#元素幻化跟随ID		依赖于  ElementSoulVisionId && EnumInt1.ElementFollowStatus
F(ElementVisionFollow, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "元素幻化跟随ID")
