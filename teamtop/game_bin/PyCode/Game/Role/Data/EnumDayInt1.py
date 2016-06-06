#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumDayInt1")
#===============================================================================
# 角色Int1数组(每日清零)使用枚举
#===============================================================================
import cRoleDataMgr
from Common import Coding
from ComplexServer.Log import AutoLog


if "_HasLoad" not in dir():
	checkEnumSet = set()

def F(uIdx, bSyncClient=False, sLogEvent=""):
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
	assert uIdx < (Coding.RoleDayInt1Range[1] - Coding.RoleDayInt1Range[0])
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumDayInt1 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	if sLogEvent: AutoLog.RegEvent(Coding.RoleDayInt1Range[0] + uIdx, sLogEvent)
	cRoleDataMgr.SetDayInt1Rule(uIdx, bSyncClient, sLogEvent)

#===============================================================================
# 数组使用定义
#===============================================================================
QQHZDailyReward = 0	#黄钻每日礼包
F(QQHZDailyReward, True)

UnionDayBox = 1		#公会每日宝箱
F(UnionDayBox, True, "公会领取每日宝箱")

LuckSerachDrgonTimes = 2 #每日一次幸运挖宝次数
F(LuckSerachDrgonTimes, True)

LegionRewardState = 3	#玩家每日第一次登录(登录奖励)
F(LegionRewardState, True)

GetLegionRewardState = 4	#当日是否领取了登录奖励
F(GetLegionRewardState, True)

IsFirstRuneWheel = 5		#当日是否第一次参加使用符文宝轮
F(IsFirstRuneWheel, True)

QAppPanelLogin = 6		#今日是否从QQ应用面板登陆
F(QAppPanelLogin, True)

Logion3366Reward = 7	#3366每日礼包
F(Logion3366Reward, True)

QQLZDailyReward = 8		#蓝钻每日礼包
F(QQLZDailyReward, True)

DayFirstPay = 9			#今天是否完成了每日首充
F(DayFirstPay, True)

DDJoin = 10				#今日是否参与了魔兽入侵
GloryWarJoin = 11		#今日是否参与了荣耀之战
QandAJoin = 12			#今日是否参与了答题
F(DDJoin, True)
F(GloryWarJoin, True)
F(QandAJoin, True)

GameUnionAiwanLog = 13		#今日是否已从游戏联盟爱玩登录过
F(GameUnionAiwanLog, True)

GameUnionQQGJLog = 14		#今日是否已从游戏联盟QQ管家登录过
F(GameUnionQQGJLog, True)

GameUnionAiwanLogAward = 15		#今日是否领取过游戏联盟爱玩登录礼包
F(GameUnionAiwanLogAward, True)

GameUnionQQGJLogAward = 16		#今日是否领取过游戏联盟QQ管家登录礼包
F(GameUnionQQGJLogAward, True)

IsDivorce = 17					#今日是否离婚
F(IsDivorce, True)

IsActGoldDrop = 18				#今日是否有未领奖的金币掉落玩法
F(IsActGoldDrop)

RuDayReward = 19				#删档测试登录奖励
F(RuDayReward, False, "删档测试登录奖励")

QQRoleBackRewardFlag = 20		#腾讯回流用户领取回流礼包的限制(防止出BUG刷)
F(QQRoleBackRewardFlag)

AFDailyLiBaoDay = 21	#今日是否领取中秋登陆礼包
F(AFDailyLiBaoDay,True)

WR3366_RewardFlag = 22	#今日 是否 领取3366一周豪礼标志
F(WR3366_RewardFlag, True)

FT_KaifuTili = 23		#今日是否领取过开服体力
F(FT_KaifuTili, True, sLogEvent="领取开服体力")

QQMiniClientDayReward = 24			#腾讯微端每日登录奖励
QQMiniClientStartRewrad = 25		#腾讯微端设置开机启动每日奖励
QQMiniClientReadyStartRewrad = 26	#腾讯微端已经设置开机启动每日奖励
F(QQMiniClientDayReward,True)
F(QQMiniClientStartRewrad,True)
F(QQMiniClientReadyStartRewrad,True)

GroupBuyCarnivalBuy = 27		# 团购嘉年华今日是否已购买(每日只有一种物品买一次 )
F(GroupBuyCarnivalBuy,True)

LuckyCoinResetFree = 28		#好运币专场 是否已经使用了免费重置装盘(每日仅有一次免费次数)
F(LuckyCoinResetFree,True)

GroupBuyPartyBuyItemOne = 29		#团购派对 是否购买第一个商品
F(GroupBuyPartyBuyItemOne,True)

GroupBuyPartyBuyItemTwo = 30		#团购派对 是否购买第二个商品
F(GroupBuyPartyBuyItemTwo,True)

IsMallBuy = 31				#今日是否在商城购物
F(IsMallBuy, True)

TimeLimitSupply_1 = 32 		#限时特供标签1奖励是否领取
TimeLimitSupply_2 = 33		#限时特供标签2奖励是否领取
TimeLimitSupply_3 = 34		#限时特供标签3奖励是否领取
F(TimeLimitSupply_1, True)
F(TimeLimitSupply_2, True)
F(TimeLimitSupply_3, True)

ChristmasWishTreeRefreshFlag = 35	#圣诞许愿树货架EnumInt16.ChristmasWishTreeRefreshDay那天中午是否已经刷新 0-未刷新 1-已刷新
F(ChristmasWishTreeRefreshFlag)

ChristmasHaoFlag = 36			#是否领取圣诞嘉年华-有钱就是任性积分奖励
F(ChristmasHaoFlag, True)

HolidayScore_1 = 37				#元旦积分奖励1是否领取
HolidayScore_2 = 38				#元旦积分奖励2是否领取
HolidayScore_3 = 39				#元旦积分奖励3是否领取
F(HolidayScore_1, True)
F(HolidayScore_2, True)
F(HolidayScore_3, True)

NewYearHaoFlag = 40			#新年我最壕奖励领取标志，春节最靓丽也借用此标志
F(NewYearHaoFlag, True)

ZumaRMBReward = 41			#祖玛神石掉落限制
F(ZumaRMBReward, True)

UnionShenShouFeed = 42		#今日是否喂养过公会神兽
F(UnionShenShouFeed, True)

GlamourRank_IsReward = 43		#今日是否领取魅力排行安慰奖
F(GlamourRank_IsReward, True)

TheMammon = 44				#是否领取过天降财神返利
F(TheMammon, True)

QingMingRank_IsReward = 45		#今日是否领取清明消费排行安慰奖
F(QingMingRank_IsReward, True)

QingMingQuanMingLianJin = 46			#清明节全民炼金是否领取过当日炼金buff
F(QingMingQuanMingLianJin, True, sLogEvent="清明节全民炼金是否领取过当日炼金buff")

FiveOneLoginState = 47		#五一活动玩家登录奖励领取状态
F(FiveOneLoginState, True)

SuperCardsReward = 48		#今日是否领取至尊周卡今日奖励
F(SuperCardsReward, True)

YeYouJieWarmupHasLoginToday = 49			#(腾讯页游节预热)判断玩家当天是否第一次登录
F(YeYouJieWarmupHasLoginToday, True)

YeYouJieWarmupHasGotRechargeRewards = 50	#(腾讯页游节预热)判断玩家当天是否领取过充值奖励
F(YeYouJieWarmupHasGotRechargeRewards, True)

KongJianFirstRechargeRewardFlag = 51				#是否领取了空间十周年首冲拿大礼奖励
F(KongJianFirstRechargeRewardFlag, True)	

KongJianLoginRewardFlag = 52				#是否领取了空间十周年登录领好礼奖励
F(KongJianLoginRewardFlag, True)	

WangZheRank_IsReward = 53		#今日是否领取王者积分榜安慰奖
F(WangZheRank_IsReward, True)


PassionGift_IsReward = 54		#激情有礼今日任务达成奖励领取标志
F(PassionGift_IsReward, True)

PassionGift_IsAccu = 55		#激情有礼今日完成任务是否累计到进度
F(PassionGift_IsAccu)

PassionRechargeRank_IsReward = 56		#今日是否领取激情活动安慰奖
F(PassionRechargeRank_IsReward, True)

ZhongQiuLianJin_IsReward = 57			#中秋节全民炼金是否领取过当日炼金buff
F(ZhongQiuLianJin_IsReward, True, sLogEvent="中秋节全民炼金是否领取过当日炼金buff")

ZhongQiuShouChong_IsRecord = 58			#中秋首冲-今日充值是否记录生效
F(ZhongQiuShouChong_IsRecord, True)

PassionConsumeRank_IsReward = 59		#今日是否领取激情活动消费排行安慰奖
F(PassionConsumeRank_IsReward, True)

PassionLianChongRec = 60		#今日是否已经增加过了充值天数
F(PassionLianChongRec, True)

LostSceneIsIn = 61					#今日是否参与迷失之境玩法
F(LostSceneIsIn, True)

DEGroupBuyFlag = 62				#是否购买了团购送神石
F(DEGroupBuyFlag, True)

ShenshuPeiyang = 63				#神树培养
F(ShenshuPeiyang, True, sLogEvent="神数秘境培养神树")

newQandARewardFlag = 64				#答题是否可以领奖
F(newQandARewardFlag, True)

Puzzle_IsPlay = 65					#是否进行过拼图
F(Puzzle_IsPlay, True)


PassionShouChong = 66				#感恩节首冲
F(PassionShouChong, True)

BuyPassionShouChong = 67			#首冲购买
F(BuyPassionShouChong, True)

PassionChunJieLoginAward = 68		#春节活跃有礼登陆奖励
PassionChunJieDailyDoReward = 69	#春节活跃有礼活跃度奖励
PassionChunJieRechargeReward = 70	#春节活跃有礼充值奖励
F(PassionChunJieLoginAward, True)
F(PassionChunJieDailyDoReward, True)
F(PassionChunJieRechargeReward, True)



LLKanFreeTimes = 71					#连连看免费次数
LLKanGetTimes = 72					#连连看是否领取首充次数
F(LLKanFreeTimes, True, "连连看免费次数")
F(LLKanGetTimes, True, "连连看是否领取首充次数")

ChunJieYuanXiaoChongZhi1 = 73		#春节元宵活动充值活动1
ChunJieYuanXiaoChongZhi2 = 74		#春节元宵活动充值活动2
F(ChunJieYuanXiaoChongZhi1, True)
F(ChunJieYuanXiaoChongZhi2, True)

ChaosDivinityReward = 75
F(ChaosDivinityReward, True)

LuckyGashponFashion = 76
F(LuckyGashponFashion, True)	#时装扭蛋每日参与标识字段

LuckyGashponMount = 77
F(LuckyGashponMount, True)		#坐骑扭蛋高级扭蛋每日参与标识字段
