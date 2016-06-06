#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Common.Other.EnumSysData")
#===============================================================================
# 枚举系统数据
#===============================================================================

KaiFuKey = 1			#开服时间time
WorldLevelKey = 2		#世界等级(每小时更新)
CampLeftKey = 3			#左阵营人数
CampRightKey = 4		#右阵营人数
FBActiveID = 5			#全服通关副本最大ID
KaiFuDay = 6			#开服日期(开服第一天算1)
WorldBuffLevel = 7		#世界BUFF等级(每天0点更新,就是0点时候的世界等级)
WeiXinAttenionCnt = 8	#微信关注人数 
OpenLimitTimes = 9		#开放限制登录的时间戳
MarryCnt = 10			#全服结婚对数
HeFuKey = 11			#合服时间time
HeFuCnt = 12			#合服当前合了几个服
WishPoolCnt = 13		#许愿池许愿次数
GoldMirrorCnt_1 = 14	#第一个金币副本次数
GoldMirrorCnt_2 = 15	#第二个金币副本次数
HeFuDay = 16			#合服天数(合服第一天算1)
ServerName = 17			#服务器名字
GameServiceQQ = 18		#服务器客服QQ
HoilyShoppingScore = 19	#元旦购物节积分
KuaFuJJCZoneId = 20		#跨服个人竞技场区域ID
KuaFuJJCVersionId = 21	#跨服个人竞技场版本ID
LanternRankServerType = 22	#元宵节点灯高手服务器区域类型
SpringBRankServerType = 23	#春节活动最靓丽分区
GlamourRankServerType = 24	#魅力派对活动指定的服务器类型
QingMingRankServerType = 25	#清明消费排行活动指定的服务器类型
SuperCardsUnionFB = 26		#至尊周卡公会副本替身组队是否开启(0关闭，1开启)
WangZheRankServerType = 27	#王者公测积分榜活动指定的服务器类型
LocalServerIDs = 28			#合服后本服服务器id集合
ShenshuLevel = 29			#神树密境神树等级
ShenshuExp = 30				#神树密境神树经验
SuperTurnTableLotteryCount = 31		#超值转盘本服抽奖次数
ChunJieActiveDays = 32				#春节活跃有礼天数
SecretGardenServerCnt = 33			#秘密花园本服累计次数
#===============================================================================
#每次修改都要考虑合服情况  参考模块 PersisteneceMerge
#===============================================================================
