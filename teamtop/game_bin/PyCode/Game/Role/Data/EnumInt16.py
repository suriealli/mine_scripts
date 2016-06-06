#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumInt16")
#===============================================================================
# 角色Int16数组使用枚举
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
	assert nMinValue >= CValue.MIN_INT16
	assert nMaxValue <= CValue.MAX_INT16
	assert uIdx < (Coding.RoleInt16Range[1] - Coding.RoleInt16Range[0])
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumInt16 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	if sLogEvent: AutoLog.RegEvent(Coding.RoleInt16Range[0] + uIdx, sLogEvent)
	cRoleDataMgr.SetInt16Rule(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient, sLogEvent)

#===============================================================================
# 数组使用定义
#===============================================================================
enLastPosX = 0 #退出场景时保存的场景坐标 X
F(enLastPosX, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing)
enLastPosY = 1 #退出场景时保存的场景坐标 Y
F(enLastPosY, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing)

enMaxLoginDays = 2 #角色最大登录天数
F(enMaxLoginDays, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing)
enContinueLoginDays = 3 #角色最近连续登录天数
F(enContinueLoginDays, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing)
enMaxContinueLoginDays = 4 #角色最大连续登录天数
F(enMaxContinueLoginDays, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing)

UnionFBCntUpdateDays = 5	#公会副本次数刷新的时间(天数)
F(UnionFBCntUpdateDays, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

DayFirstPayIconShowTime = 6		#用来控制每日首充图标展示的时间(保存一个天数)
F(DayFirstPayIconShowTime, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

GoldDragonEggBreakCnt = 7	#砸金龙蛋次数
F(GoldDragonEggBreakCnt, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

TiLi = 8 #体力值
F(TiLi, 0, Enum.DoNothing, 9999, Enum.DoRound, True, "改变体力值")

FollowHero = 9 #跟随的英雄类型
F(FollowHero, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

MountEvolveID = 11 #坐骑进化ID(可以转换成坐骑星级和等级)
F(MountEvolveID, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "改变坐骑进化ID(可以转换成坐骑星级和等级)")

FB_Active_ID = 12 		#当前副本激活的ID (已经通关的最大ID)
F(FB_Active_ID, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "改变副本激活的ID")

DragonLevel = 13		#神龙等级
F(DragonLevel, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

FB_ZJActive_ID 	 = 14	#已通关的最大章节ID
F(FB_ZJActive_ID, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "改变普通副本开启ID")

KuaFuJJCBuyCnt = 15	#跨服个人竞技场购买次数
F(KuaFuJJCBuyCnt, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

GoldTimesDay = 16 #每日炼金次数
F(GoldTimesDay, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

DailyDoScore = 17 #每日必做积分
F(DailyDoScore, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

HeroTempleMaxIndex = 18 #英灵神殿最大索引
F(HeroTempleMaxIndex, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "英灵神殿最大索引")

WonderRoleGem = 19 #精彩活动每日购买宝石数
F(WonderRoleGem, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

WonderRoleTarot = 20 #精彩活动每日高级占卜数
F(WonderRoleTarot, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

DragonSkillPoint = 21 #神龙技能点(可以使用)
F(DragonSkillPoint, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

DragonAllSkillPoint = 22 #累计的神龙技能点
F(DragonAllSkillPoint, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

WeddingRingID = 23 #婚戒进化ID
F(WeddingRingID, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

StrayFreshDays = 24	#流浪商人刷新时间（天数）
F(StrayFreshDays, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

StarGirlLove = 25	#星灵爱心值
F(StarGirlLove, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

RuneWheelTimes = 26	#每日转动符文宝轮的次数
F(RuneWheelTimes, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

RightBuffStatus = 27	#万圣节变身卡当前使用的buff外形
F(RightBuffStatus, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

WishPoolDayCnt = 28	#许愿池每天次数
F(WishPoolDayCnt, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

QQHallLotteryEffectTimes = 29	#大厅搏饼有效次数
F(QQHallLotteryEffectTimes, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "大厅搏饼有效次数")

JTDayEndFightTimes = 30#组队竞技场日结周期比赛次数
F(JTDayEndFightTimes, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

KuaFuJJCChallengeCnt = 31	#跨服个人竞技场挑战行动力
F(KuaFuJJCChallengeCnt, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

JTMedalLevel = 32			#当前佩戴的勋章等级
F(JTMedalLevel, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "当前佩戴的跨服竞技场勋章等级")

QinmiLevel = 33			#亲密等级
F(QinmiLevel, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "亲密等级")

DragonSteleNomalTimes = 34	#龙魂石碑今日普通祈祷次数（每日重置）
F(DragonSteleNomalTimes, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)#, "龙魂石碑普通祈祷次数")

DragonSteleSpecialTime = 35	#龙魂石碑今日高级祈祷次数（每日重置）
F(DragonSteleSpecialTime, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)#, "龙魂石碑高级祈祷次数")

GodTreasureUpdateDays = 36	#众神秘宝刷新时间（天数）
F(GodTreasureUpdateDays, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

TGOnlineRewardOnlineMinute = 37		#狂欢感恩节-在线赢大礼 今日在线分钟数
F(TGOnlineRewardOnlineMinute, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

LoveTogetherOnLineMinutes = 38		#爱在一起今日在线分钟数
F(LoveTogetherOnLineMinutes, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

LuckyCoinLotteryRewardRecord = 39		#好运币专场 本轮抽奖已抽物品记录(每日重置 玩家花费神石重置)
F(LuckyCoinLotteryRewardRecord, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

FeastWheelRMBTimes = 40				#盛宴摩天轮RMB抽奖次数
F(FeastWheelRMBTimes, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

ChristmasWishTreeRefreshDay = 41	#圣诞许愿树上次系统刷新天数
F(ChristmasWishTreeRefreshDay, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

HolidayOnLineMinutes = 42		#元旦在线奖励--今日在线分钟数
F(HolidayOnLineMinutes, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

HolidayLotteryTimes = 43		#元旦充值抽奖--剩余有效次数
F(HolidayLotteryTimes, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

NYearOnLineMinutes = 44			#新年活动在线时间（分钟）
F(NYearOnLineMinutes, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

QQLZLuxuryRollCrystal = 45		#豪华蓝钻水晶 剩余数量
F(QQLZLuxuryRollCrystal, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "豪华蓝钻水晶数量改变")

QQHZRollCrystal = 46		#黄钻水晶 剩余数量
F(QQHZRollCrystal, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "黄钻水晶数量改变")

DKCPassedLevel = 47		#龙骑试炼最高通关
F(DKCPassedLevel, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "龙骑试炼通关")

RosePresentSendTimes = 48		#送人玫瑰-今日赠送99朵玫瑰数量
F(RosePresentSendTimes, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "送人玫瑰-今日赠送99朵玫瑰数量")

RosePresentLotteryTimesTwo = 49		#可复用
F(RosePresentLotteryTimesTwo, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "一朵玫瑰对应剩余抽奖次数")

DayGlamourExp = 50		#魅力情人节-今日魅力值 可复用
F(DayGlamourExp, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "今日魅力值")

HistoryGlamourExp = 51	#魅力情人节-历史总魅力值 可复用
F(HistoryGlamourExp, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "历史总魅力值")

QQLZRollCrystal = 52		#蓝钻水晶 剩余数量
F(QQLZRollCrystal, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "蓝钻水晶数量改变")

KuaFuJJCElectionRound = 53				#跨服个人竞技场海选轮数
KuaFuJJCFinalsRound = 54				#跨服个人竞技场决赛轮数
KuaFuJJCElectionWinningStreak = 55		#跨服个人竞技场海选连胜次数
KuaFuJJCFinalsWinningStreak = 56		#跨服个人竞技场决赛连胜次数
F(KuaFuJJCElectionRound, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)
F(KuaFuJJCFinalsRound, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)
F(KuaFuJJCElectionWinningStreak, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)
F(KuaFuJJCFinalsWinningStreak, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

InviteReward = 57			#邀请好友抽奖次数
F(InviteReward, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

OldPlayerBackVersion = 58	#老玩家回流活动版本号
F(OldPlayerBackVersion, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "老玩家回流活动版本号")

HeroShengdianMaxIndex = 59	#英雄圣殿最大索引
F(HeroShengdianMaxIndex, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True)

HeroShengdianBuyCnt = 60	#英雄圣殿购买次数
F(HeroShengdianBuyCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

QingMingOutingLotteryCnt = 61	#清明踏青今日翻牌次数
F(QingMingOutingLotteryCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

QQLZHappyDCrystal = 62		#蓝钻转转乐水晶 剩余数量
F(QQLZHappyDCrystal, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "蓝钻转转乐水晶")

QQHZHappyDCrystal = 63		#黄钻转转乐水晶 剩余数量
F(QQHZHappyDCrystal, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "黄钻转转乐水晶")

OldRoleBackFTVersion = 64	#繁体老玩家回流活动版本号
F(OldRoleBackFTVersion, 0, Enum.DoNothing, CValue.MAX_INT16, Enum.DoNothing, True, "繁体老玩家回流活动版本号")

WingTempTrainValue = 65	#羽翼的临时进度值
F(WingTempTrainValue, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

WarStationStarNum = 66	#战阵升星数
F(WarStationStarNum, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True, "战阵升星数")

WarStationTempValue = 67	#战阵突破进度
F(WarStationTempValue, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True, "战阵突破进度")

StationSoulId = 68		#阵灵Id
F(StationSoulId, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True, "阵灵Id")

StationSoulExp = 69		#阵灵突破进度条
F(StationSoulExp, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True, "阵灵突破进度条")

EquipmentWashNum = 70		#最新活动装备洗练次数
F(EquipmentWashNum, 0, Enum.DoRound, CValue.MAX_INT16, CValue.MAX_INT16, True)

UseStationItemCnt = 71	#战阵战魂石使用次数
F(UseStationItemCnt, 0, Enum.DoRound, CValue.MAX_INT16, CValue.MAX_INT16, True, "战阵战魂石使用次数")

StationSoulItemCnt = 72		#阵灵强化石使用数量
F(StationSoulItemCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True, "阵灵强化石使用数量")

AntiOnlineMinCnt = 73		#防沉迷今日在线分钟数 
F(AntiOnlineMinCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

CTTMaxLayer = 74		#虚空幻境爬的最高层
F(CTTMaxLayer, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

HuoYueDaLiOnLineMins = 75			#中秋活跃大礼在线分钟数
F(HuoYueDaLiOnLineMins, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

CTTDayPoint = 76		#每日获得的幻境点
F(CTTDayPoint, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

JTCheersCnt = 77		#跨服争霸赛每日喝彩次数
F(JTCheersCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

DETopicLotteryCnt = 78		#专题转盘今日抽奖次数
F(DETopicLotteryCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

TouchGoldBuyTimes = 79		#每日点石成金购买次数
F(TouchGoldBuyTimes, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True, "每日点石成金购买次数")



TJHC_ActivatedCnt = 80		#天降横财_已激活兑奖码次数
F(TJHC_ActivatedCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True, "天降横财_已激活兑奖码次数")

TouchGoldRewardCnt = 81		#点金大放送累计点金次数
F(TouchGoldRewardCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True)

ElementSpiritId = 82		#元素之灵ID
F(ElementSpiritId, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoNothing, True, "天降横财_已激活兑奖码次数")


Game2048Step = 83			#宝石2048剩余步数
F(Game2048Step, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoRound, True)

ChunJieYuanXiao = 84	#元宵活动花灯
F(ChunJieYuanXiao, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoRound, True,"元宵活动花灯")

YYAntiOnlineMinCnt = 85		#YY防沉迷在线时间（分钟）
F(YYAntiOnlineMinCnt, 0, Enum.DoRound, CValue.MAX_INT16, Enum.DoRound, True)