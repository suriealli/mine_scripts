#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumDayInt8")
#===============================================================================
# 角色Int8数组(每日清零)使用枚举
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
	assert uIdx < (Coding.RoleDayInt8Range[1] - Coding.RoleDayInt8Range[0])
	assert nMinValue >= CValue.MIN_INT8
	assert nMaxValue <= CValue.MAX_INT8
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumDayInt8 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	if sLogEvent: AutoLog.RegEvent(Coding.RoleDayInt8Range[0] + uIdx, sLogEvent)
	cRoleDataMgr.SetDayInt8Rule(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient, sLogEvent)

#===============================================================================
# 数组使用定义
#===============================================================================
ChatCnt = 0 #每天聊天次数
F(ChatCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, False)

TiLi_Buy_Times = 1 #购买体力次数
F(TiLi_Buy_Times, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True)

JJC_Buy_Cnt = 2 #竞技场购买次数
F(JJC_Buy_Cnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "竞技场购买次数")

Union_Rob_Gold_Box_Cnt = 3		#公会夺取金宝箱次数
Union_Rob_Silver_Box_Cnt = 4	#公会夺取银宝箱次数
Union_Rob_Copper_Box_Cnt = 5	#公会夺取铜宝箱次数
F(Union_Rob_Gold_Box_Cnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "公会夺取金宝箱次数")
F(Union_Rob_Silver_Box_Cnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "公会夺取银宝箱次数")
F(Union_Rob_Copper_Box_Cnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "公会夺取铜宝箱次数")

JJC_Score = 6 #竞技场积分
F(JJC_Score, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True, "竞技场积分")

PetLuckyDrawCnt = 7 #宠物转转乐次数
F(PetLuckyDrawCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "宠物转转乐次数")

FB_Times = 8 #今天参加副本的次数(注意有负数哦)
F(FB_Times, CValue.MIN_INT8, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True, "副本次数")

FB_BuyTimes = 9 #今天购买过的副本的次数
F(FB_BuyTimes, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

GoddessCardResetCnt = 10	#女神卡牌重置轮数
F(GoddessCardResetCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "女神卡牌重置轮数")

InviteFriendCnt = 11	#邀请好友个数
F(InviteFriendCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoIgnore, True)

MountEvolveCnt = 12   #每日坐骑普通培养次数
F(MountEvolveCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

PurgatoryCnt = 13		#心魔炼狱挑战次数
F(PurgatoryCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

DD_Lucky_Draw_Cnt = 14	#魔兽入侵抽奖次数
F(DD_Lucky_Draw_Cnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GoldHelpTimesDay = 15	#记录玩家每天协助炼金次数
F(GoldHelpTimesDay, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

SerachDrgonTimes = 16 #巨龙宝藏挖宝次数
F(SerachDrgonTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

SerachDrgonTimesReward = 17 #奖励获取的挖宝次数
F(SerachDrgonTimesReward, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

LuckSerachDrgonTimesReward = 18 #巨龙宝藏幸运挖宝次数(奖励的)
F(LuckSerachDrgonTimesReward, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GoldenkeyNumber = 19 #巨龙宝藏金钥匙个数
F(GoldenkeyNumber, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

UnionLaunchGold = 20		#开启公会金宝箱
UnionLaunchSilver = 21		#开启公会银宝箱
UnionLaunchCopper = 22		#开启公会铜宝箱
F(UnionLaunchGold, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "开启公会金宝箱")
F(UnionLaunchSilver, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "开启公会银宝箱")
F(UnionLaunchCopper, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "开启公会铜宝箱")

DayTaskCnt = 23 #日常任务已经完成的个数
F(DayTaskCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

TiLiTaskCnt = 24 #体力任务已经完成的个数
F(TiLiTaskCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

DukeDutyCDTimes = 25		#城主轮值加速CD次数
F(DukeDutyCDTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

UnionGodProgress = 26		#公会魔神进度
F(UnionGodProgress, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

FlowerCnt = 27		#每日送花记录
F(FlowerCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

Slave_PlayTimes = 28	#抓奴隶每日互动次数
F(Slave_PlayTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GloryWar_CampId = 29	#荣耀之战阵营ID
F(GloryWar_CampId, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

LuckTurntablecnt = 30	#今日已经参加幸运转盘的次数
F(LuckTurntablecnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoIgnore, True)

InviteQunCnt = 31	#邀请群个数
F(InviteQunCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

HeroTempCnt = 32	#英灵神殿挑战次数
F(HeroTempCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
HeroTempBuyCnt = 33	#英灵神殿购买次数
F(HeroTempBuyCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)


Slave_CatchTimes = 34	#奴隶系统抓捕次数
F(Slave_CatchTimes, CValue.MIN_INT8, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
Slave_BuyCatchTimes = 35	#奴隶系统购买抓捕次数
F(Slave_BuyCatchTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

Slave_SaveTimes = 36	#奴隶系统解救的次数
F(Slave_SaveTimes, CValue.MIN_INT8, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
Slave_BuySaveTimes = 37	#奴隶系统购买解救的次数
F(Slave_BuySaveTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

Slave_BattleTimes = 38	#奴隶系统反抗(求救)的次数
F(Slave_BattleTimes, CValue.MIN_INT8, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
Slave_BuyBattleTimes = 39	#奴隶系统购买反抗(求救)的次数
F(Slave_BuyBattleTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

ToSkyCnt = 40	#冲上云霄翻牌次数
F(ToSkyCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

BallFameASCheerCnt = 41	#一球成名全服喝彩次数
F(BallFameASCheerCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

BallFameUnionCheerCnt = 42	#一球成名帮派喝彩次数
F(BallFameUnionCheerCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

BallFameGoalsCnt = 43	#一球成名进球个数
F(BallFameGoalsCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoIgnore, True)

AsteroidFieldsBuyTimes = 44		 #魔域星宫行动力购买次数
F(AsteroidFieldsBuyTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "魔域星宫购买行动力次数")

AsteroidFieldsChallengeTimes = 45		 #魔域星宫进入魔域次数
F(AsteroidFieldsChallengeTimes, CValue.MIN_INT8, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "魔域星宫进入魔域次数")

GVEFBBuyCnt = 46		#GVE副本购买次数
F(GVEFBBuyCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

TwelvePalaceCnt = 47	#参加勇闯十二宫次数
F(TwelvePalaceCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

TwelvePalaceHelpCnt = 48		#勇闯十二宫协助次数
F(TwelvePalaceHelpCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

CouplesFBTimes = 49		#情缘副本收益次数
F(CouplesFBTimes, CValue.MIN_INT8, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

CouplesFBBuyTimes = 50	#情缘副本购买次数
F(CouplesFBBuyTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

MarryLibaoCntLimit = 51	#每日领取婚礼礼包个数
F(MarryLibaoCntLimit, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GoblinRewardCnt = 52	#劫宝奖励次数
F(GoblinRewardCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GVEFBCnt = 53	#GVE副本次数
F(GVEFBCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GoldChestCnt = 54	#已打开黄金宝箱的个数
F(GoldChestCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GoldDropAwardCnt_1 = 55	#金币副本1收益次数
F(GoldDropAwardCnt_1, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

GoldDropAwardCnt_2 = 56	#金币副本2收益次数
F(GoldDropAwardCnt_2, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

BraveHeroCnt = 57	#勇者英雄坛次数
F(BraveHeroCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

BraveHeroBuyCnt = 58	#勇者英雄坛购买次数
F(BraveHeroBuyCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

StrayFreshCnt = 59	#流浪商人刷新次数
F(StrayFreshCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

AF_LatteryFreeNumUsed = 60		#中秋搏饼---今日使用的免费次数
F(AF_LatteryFreeNumUsed, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

AF_LatteryDailyBoxNum = 61 		# 中秋搏饼---每日必做宝箱获取的次数剩余
F(AF_LatteryDailyBoxNum, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

AF_TodayMoonCakeUsedNum = 62	#中秋月饼今日使用次数
F(AF_TodayMoonCakeUsedNum, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

DragonTrainCollectSoulCnt = 63	#驯龙聚灵次数
F(DragonTrainCollectSoulCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

QQHZGift_OG_TodayTimes = 64		#黄钻献大礼 今日领奖次数
F(QQHZGift_OG_TodayTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

TT_RewradTimes = 65	#组队爬塔收益次数
F(TT_RewradTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "组队爬塔收益次数")

TT_BuyTimes = 66	#组队爬塔购买收益次数
F(TT_BuyTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

StarGirlNormalDivineCnt = 67	#星灵普通占星次数
F(StarGirlNormalDivineCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

StarGirlSuperDivineCnt = 68	#星灵虔诚占星次数
F(StarGirlSuperDivineCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

StarGirlLevelUpFreeCnt = 69	#星灵升级免费次数
F(StarGirlLevelUpFreeCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

KuaFuJJCFreeCnt = 70	#跨服竞技场海选免费次数
F(KuaFuJJCFreeCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

StarGirlBuyLoveCnt = 71	#星灵之力购买爱心值次数
F(StarGirlBuyLoveCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

HalloweenKillTimes = 72	#万圣节金币击杀鬼次数
F(HalloweenKillTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

DragonVeinLevelUpCnt = 73	#龙脉免费升级次数
F(DragonVeinLevelUpCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "龙脉免费升级次数")

JTDayFightTimes = 74	#组队竞技场每日战斗次数
F(JTDayFightTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

PartyBlessCnt = 75			#结婚Party祝福次数
F(PartyBlessCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

PartyStatus = 76			#结婚Party状态 0-未开始, 1-已预约, 2-已开始, 3-已完成
F(PartyStatus, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

QQLZGift_OG_TodayTimes = 77		#蓝钻献大礼 今日领奖次数
F(QQLZGift_OG_TodayTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

CutTurkeyNCnt = 78			#切普通火鸡次数
F(CutTurkeyNCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

CutTurkeyACnt = 79			#切高级火鸡次数
F(CutTurkeyACnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

### 狂欢感恩节-充值送豪礼
TGRechargeRewardRechargeTimes = 80		 #剩余充值奖励次数
F(TGRechargeRewardRechargeTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

TGRechargeRewardInviteTimes = 81 		#剩余邀请好友奖励次数
F(TGRechargeRewardInviteTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

TGRechargeRewardOnlineTimes = 82 		#剩余在线奖励次数
F(TGRechargeRewardOnlineTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

TGToDayInviteTimes = 83		#今日邀请好友次数
F(TGToDayInviteTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

### 狂欢感恩节-在线赢大礼
TGOnlineRewardRecord = 84		#今日已领取奖励记录
F(TGOnlineRewardRecord, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

KuaFuJJCFinalsFreeCnt = 85	#跨服竞技场决赛免费次数
F(KuaFuJJCFinalsFreeCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

ZumaBuyCnt = 86				#祖玛购买次数
F(ZumaBuyCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

EnumDayInt8_None = 87				#可以服用
F(EnumDayInt8_None, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

FeastWheelNomalTimes = 88				#盛宴摩天轮Nomal抽奖次数
F(FeastWheelNomalTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

LuckyCoinLotteryLevelRangeId = 89		#好运币专场 当前抽奖等级区段ID(一轮抽奖完毕 手动重置重新赋值)
F(LuckyCoinLotteryLevelRangeId, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

DI8_None = 90		#可复用
F(DI8_None, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

LuckyCoinLotteryCurrentTimes = 91		#好运币当前轮次已抽奖个数（1-12）for计算好运币消耗
F(LuckyCoinLotteryCurrentTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

LuckyCoinLotteryResetTimes = 92		#好运币今日神石重置转盘次数
F(LuckyCoinLotteryResetTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

DragonBuyedDigTimes = 93			#已购买巨龙宝藏挖宝次数
F(DragonBuyedDigTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

DragonCanDigTimes = 94			#通过购买巨龙宝藏获得的可挖宝次数
F(DragonCanDigTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

DragonBuyedLuckyDigTimes = 95			#已购买巨龙宝藏幸运挖宝次数
F(DragonBuyedLuckyDigTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

DragonCanLuckyDigTimes = 96			#通过购买巨龙宝藏获得的可挖宝次数
F(DragonCanLuckyDigTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ChristmasWishTreeRefreshCnt = 97	#圣诞许愿树今日手动刷新货架次数
F(ChristmasWishTreeRefreshCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ChristmasWingLotteryFreeTimes = 98	#圣诞羽翼转转乐剩余折扣次数 PS:有次数时候打折扣神石
F(ChristmasWingLotteryFreeTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ChristmasMountLotteryFreeTimes = 99	#圣诞坐骑转转乐剩余折扣次数 PS:有次数时候打折扣神石
F(ChristmasMountLotteryFreeTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ChristmasIncRecordWingLottery = 100		#圣诞羽翼转转乐免费次数获取记录
F(ChristmasIncRecordWingLottery, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ChristmasIncRecordMountLottery = 101	#圣诞坐骑转转乐免费次数获取记录
F(ChristmasIncRecordMountLottery, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

HolidayWishCnt = 102			#元旦祈福次数
F(HolidayWishCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

HolidayOnlineRewardRecord = 103		#元旦在线奖励领取记录
F(HolidayOnlineRewardRecord, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

UnionTaskCnt = 104	#公会任务次数
F(UnionTaskCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

UnionTaskHelpCnt = 105	#公会任务助人次数
F(UnionTaskHelpCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

HolidayWishFreeCnt = 106		#元旦祈福免费次数
F(HolidayWishFreeCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)
HolidayWishLimitCnt_1 = 107		#元旦祈福限购次数1
F(HolidayWishLimitCnt_1, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)
HolidayWishLimitCnt_2 = 108		#元旦祈福限购次数2
F(HolidayWishLimitCnt_2, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)
HolidayWishLimitCnt_3 = 109		#元旦祈福限购次数3
F(HolidayWishLimitCnt_3, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

NYearFreeTimes = 110		#新年活动免费抽奖数
F(NYearFreeTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

UnionShenShouChallenge = 111		#公会神兽挑战次数
F(UnionShenShouChallenge, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

UnionShenShouBuf = 112		#公会神兽祝福次数（公会神兽buff的购买次数）
F(UnionShenShouBuf, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, '公会神兽祝福次数')

JTStoreRefreshCnt = 113		#跨服竞技场金券兑换商店刷新次数
F(JTStoreRefreshCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

UnionExploreBuyCnt = 114	#公会魔域探秘购买行动力次数
F(UnionExploreBuyCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

#可复用
#KuaFuJJCFinalsRound = 115				#跨服个人竞技场决赛轮数
#KuaFuJJCElectionWinningStreak = 116		#跨服个人竞技场海选连胜次数
#KuaFuJJCFinalsWinningStreak = 117		#跨服个人竞技场决赛连胜次数
#F(KuaFuJJCFinalsRound, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)
#F(KuaFuJJCElectionWinningStreak, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)
#F(KuaFuJJCFinalsWinningStreak, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

LanternFestivalRiddleIndex = 118		#元宵节活动猜灯谜当前题号
F(LanternFestivalRiddleIndex, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

LanternFestivalRiddleTimes = 119		#元宵节活动猜灯谜当前猜谜次数
F(LanternFestivalRiddleTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

LanternFestivalRiddleBuyTimes = 120		#元宵节活动猜灯谜购买猜谜次数
F(LanternFestivalRiddleBuyTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

NianComingTimes = 121		#年兽来了开宝箱次数
F(NianComingTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, '年兽来了开宝箱次数')

HeroShengdianTodayBuyCnt = 122	#英雄圣殿今日购买次数
F(HeroShengdianTodayBuyCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

HeroShengdianFreeCnt = 123	#英雄圣殿免费挑战次数
F(HeroShengdianFreeCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

MoLingDrawCnt = 124 #魔灵大转盘次数
F(MoLingDrawCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "魔灵大转盘次数")

ZaiXianJiangLiLotteryTimes = 125 #新在线奖励_今日已抽奖次数
F(ZaiXianJiangLiLotteryTimes, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "新在线奖励_今日已抽奖次数")

YeYouJieDiscountRefreshCnt = 126 #页游节折扣汇每日刷新次数
F(YeYouJieDiscountRefreshCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "页游节折扣汇每日刷新次数")

KongJianDecennialExchangeCoin = 127 #空间十周年兑换币
F(KongJianDecennialExchangeCoin, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "空间十周年兑换币")

ZaiXianLuxuryRewardIndex = 128 #在线有豪礼_今日已领取的最大奖励索引
F(ZaiXianLuxuryRewardIndex, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "在线有豪礼_今日已领取的最大奖励索引")

WangZheZheKouHuiRefreshCnt = 129 #王者公测折扣汇每日刷新次数
F(WangZheZheKouHuiRefreshCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "王者公测折扣汇每日刷新次数")

PassionMarketRefreshCnt = 130		#激情卖场今日手动刷新次数
F(PassionMarketRefreshCnt, 0, Enum.DoIgnore, CValue.MAX_INT8, Enum.DoRound, True, "激情卖场今日手动刷新次数")

PassionOnlineGiftOnlineMin = 131	#激情活动在线有礼今日在线分钟数
F(PassionOnlineGiftOnlineMin, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

QiangHongBaoCnt = 132		#今日抢红包次数
F(QiangHongBaoCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "今日抢红包次数")

CTTRewardTimes = 133		#虚幻幻境收益次数
F(CTTRewardTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "虚幻幻境收益次数")

CTTFreshTimes = 134			#虚空幻境兑换商店刷新次数
F(CTTFreshTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

ShenshuRMBInc = 135			#神树密境神石增益档次
F(ShenshuRMBInc, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True)

TouchGoldFreeTimes = 136		#点石成金免费次数
F(TouchGoldFreeTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "点石成金免费次数")

TouchGoldFreeStones = 137		#点石成金免费领取原石次数
F(TouchGoldFreeStones, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "点石成金免费领取原石次数")

ThanksSignIn = 138						#感恩节签到 (1代表第一段时间，2代表第二段时间，4代表第三段时间,二进制表示哪个时间段)
F(ThanksSignIn, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "感恩节签到次数")

MDragonTimes = 139						#"魔龙降临挑战次数"
F(MDragonTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "魔龙降临挑战次数")

ElementalEssenceTimes = 140					#元素精炼的精炼次数
F(ElementalEssenceTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "元素精炼的精炼次数")

NewYearHammer = 141								#元旦锤子数量
F(NewYearHammer, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "元旦锤子数量")

Game2048BuyTimes = 142								#宝石2048每日已经购买次数
F(Game2048BuyTimes, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "宝石2048每日已经购买次数")

ChaosDivinityCnt = 143			#混沌神域参加次数
F(ChaosDivinityCnt, 0, Enum.DoNothing, CValue.MAX_INT8, Enum.DoNothing, True, "混沌神域参加次数")

QQLZBuffSlave = 144	#蓝钻特权抓奴隶每日互动次数+1
F(QQLZBuffSlave, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

KFZC_TurnTableCnt = 145	#跨服战场转盘
F(KFZC_TurnTableCnt, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "跨服战场转盘次数")


LLKanPlayTimes = 146	#连连看可玩次数
LLKanBuyTimes = 147		#连连看已购买次数
F(LLKanPlayTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "连连看可玩次数")
F(LLKanBuyTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "连连看已购买次数")

YuanXiaoHuaDengBuyTimes = 148	#花灯购买次数
F(YuanXiaoHuaDengBuyTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True, "花灯购买次数")
YuanXiaoLightHuaDengFreeTimes = 149			#提升花灯免费次数
F(YuanXiaoLightHuaDengFreeTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

CommonGashaponTimes = 150			#每日普通时装扭蛋参与次数
F(CommonGashaponTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

UseGMPower = 151					#使用GM禁言次数
F(UseGMPower, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)

CommonMountGashaponTimes = 152			#每日普通坐骑扭蛋参与次数
F(CommonMountGashaponTimes, 0, Enum.DoRound, CValue.MAX_INT8, Enum.DoNothing, True)
