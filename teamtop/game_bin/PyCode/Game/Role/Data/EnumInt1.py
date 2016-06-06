#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumInt1")
#===============================================================================
# 角色Int1数组使用枚举
#===============================================================================
import cRoleDataMgr
from Common import Coding
from ComplexServer.Log import AutoLog


if "_HasLoad" not in dir():
	#这个要保证一下，防止配置表填错了，角色登陆处理会有问题的
	StatusSet = set()
	checkEnumSet = set()
	
def F(uIdx, bSyncClient = False, sLogEvent = "", isStatus = False):
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
	assert uIdx < (Coding.RoleInt1Range[1] - Coding.RoleInt1Range[0])
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumInt1 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	if sLogEvent: AutoLog.RegEvent(Coding.RoleInt1Range[0] + uIdx, sLogEvent)
	cRoleDataMgr.SetInt1Rule(uIdx, bSyncClient, sLogEvent)
	
	if isStatus:
		StatusSet.add(uIdx)

#===============================================================================
# 数组使用定义,注意是状态管理的要isStatus = True
#===============================================================================
En_IsInitOk = 0					#是否第一次登陆的角色(用于角色数据初始化)
F(En_IsInitOk, True)

ST_FightStatus = 1				#[状态]是否在客户端播放战斗状态
F(ST_FightStatus, True, isStatus = True)

TeamAutoAcceptInvite = 2		#自动接受组队邀请
F(TeamAutoAcceptInvite, True)

Active_FightData = 3			#是否激活离线战斗数据缓存
F(Active_FightData)

UnionFBNotCost = 4			#公会副本不消耗次数
F(UnionFBNotCost, True)

ST_Team = 5					#[状态]是否在组队
F(ST_Team, True, isStatus = True)

JJCFirstChallenge = 6		#是否第一次挑战竞技场
F(JJCFirstChallenge, True)

ST_InMirror = 7				#[状态]是否在非组队副本中
F(ST_InMirror, True, isStatus = True)

ST_InTeamMirror = 8			#[状态]是否在组队相关玩法的副本中
F(ST_InTeamMirror, True, isStatus = True)

MianTaskEgg = 9			#是否已经领取主线任务砸蛋奖励
F(MianTaskEgg, True, "是否已经领取主线任务砸蛋奖励")

QSaveDeskTop_Flag = 10	#游戏保存到桌面，可以领取一次奖励
F(QSaveDeskTop_Flag, True, "游戏保存到桌面，可以领取一次奖励")

PetFastTrain = 11	#宠物快速培养
F(PetFastTrain, True)

ST_TP = 12						#[状态]传送状态
F(ST_TP, True, isStatus = True)

QQHZRewardStatus = 13			#是否已领取黄钻新手礼包
F(QQHZRewardStatus, True)

SlaveInitFlag = 14			#是否已经激活奴隶系统
F(SlaveInitFlag, True)

FirstPayBoxOpen = 15	#是否已经领取过超值首充宝箱奖励
F(FirstPayBoxOpen, True)

FiveGiftLucky1 = 16			#五重礼福缘抽奖1
FiveGiftLucky2 = 17			#五重礼福缘抽奖2
FiveGiftLucky3 = 18			#五重礼福缘抽奖3
F(FiveGiftLucky1, True)
F(FiveGiftLucky2, True)
F(FiveGiftLucky3, True)

QAppOnPanel = 19		#应用是否添加到QQ主面板标记
F(QAppOnPanel, True)

UnionFBElite = 20			#公会副本精英挑战次数
F(UnionFBElite, True)

LegionRewardState = 21		#是否激活了登录奖励(转盘)
F(LegionRewardState, True)

WeekCardFirst = 22			#首次购买周卡
F(WeekCardFirst, True)

MonthCardFirst = 23			#首次购买月卡
F(MonthCardFirst, True)

PetFarm = 24 					#可重复使用
F(PetFarm, True)

guibinlibao = 25				#是否使用过贵宾礼包的CDkey
F(guibinlibao, True)

tequanlibao = 26				#是否使用过特权礼包的CDkey
F(tequanlibao, True)

baijinlibao = 27				#是否使用过白金礼包的CDkey
F(baijinlibao, True)

zuanshilibao = 28				#是否使用过钻石礼包的CDkey
F(zuanshilibao, True)

haohuadalibao = 29				#是否使用过豪华大礼包的CDkey
F(haohuadalibao, True)

QQLZRewardStatus = 30			#是否已领取蓝钻新手礼包
F(QQLZRewardStatus, True)

WeiXinAttention = 31			#是否关注微信
F(WeiXinAttention, True)

TeamTowerNoReward = 32					#组队爬塔无奖励模式  0 关闭即使用次数    1开启  ，进入后不扣除奖励次数，不发奖
F(TeamTowerNoReward, True)

huangjinshuqitequanlibao = 33					#是否使用过黄金暑期特权礼包的CDkey
F(huangjinshuqitequanlibao, True)

shuijingshuqitequanlibao = 34					#是否使用过水晶暑期特权礼包的CDkey
F(shuijingshuqitequanlibao, True)

zuanshishuqitequanlibao = 35					#是否使用过钻石暑期特权礼包的CDkey
F(zuanshishuqitequanlibao, True)

ST_InCouplesFB = 36				#是否在情缘副本中
F(ST_InCouplesFB, True, isStatus = True)

ST_InWedding = 37				#是否在结婚场景中
F(ST_InWedding, True, isStatus = True)

GameUnionBuff_Aiwan = 38	#是否领取过对应平台的buff
GameUnionBuff_QQGJ = 39
F(GameUnionBuff_Aiwan, True)
F(GameUnionBuff_QQGJ, True)

GVEFBNotCost = 40			#GVE副本不消耗次数
F(GVEFBNotCost, True)

GMRoleLockFlag = 41			#gm号锁定标识，具体用法请搜索@GMRoleLockFlag
F(GMRoleLockFlag, False, "修改gm号锁定标识(封号了，或者重新解封了)")

xinshoulibao = 42					#是否使用过新手礼包的CDkey
F(xinshoulibao, True)

bahazhuanshulibao = 43					#是否使用过巴哈专属礼包的CDkey
F(bahazhuanshulibao, True)

qimozhuanshulibao = 44					#是否使用过奇摩专属礼包的CDkey
F(qimozhuanshulibao, True)

jidiCBzhuanshulibao = 45				#是否使用过基地CB专属礼包的CDkey
F(jidiCBzhuanshulibao, True)

jidiOBzhuanshulibao = 46				#是否使用过基地OB专属礼包的CDkey
F(jidiOBzhuanshulibao, True)

meitizhuanshulibao = 47					#是否使用过媒体专属礼包礼包的CDkey
F(meitizhuanshulibao, True)

aiwanjingyinglibao = 48                                 #是否使用过爱玩精英礼包的CDkey
F(aiwanjingyinglibao, True)

shengdianganenlibao = 49                                 #是否使用过圣殿感恩礼包的CDkey
F(shengdianganenlibao, True)

longqifensilibao = 50                                 #是否使用过龙骑粉丝礼包的CDkey
F(longqifensilibao, True)


FTTestRewradFlag = 51				#繁体删档测试首次登录奖励标识
F(FTTestRewradFlag)

PersonalInfoCommitStatus = 52					#是否填写过玩家个人真实信息（0：未填写 1：已填写）
F(PersonalInfoCommitStatus, True)

xingyundalibao = 53								#是否使用过幸运大礼包的CDkey
F(xingyundalibao, True)

yinyuejiezhuanshulibao = 54						#是否使用过音乐节专属礼包的CDkey
F(yinyuejiezhuanshulibao, True)

shengdianjidoulibao = 55						#是否使用过圣殿激斗礼包的CDkey
F(shengdianjidoulibao, True)

mlibao = 56										 #是否使用过m+礼包的CDkey
F(mlibao, True)

qibinglibao = 57								#是否使用过骑兵礼包的CDkey
F(qibinglibao, True)

chaojixinshoulibao = 58								#是否使用过超级新手礼包的CDkey
F(chaojixinshoulibao, True)

Fblibao = 59								#是否使用过FB礼包的CDkey
F(Fblibao, True)

huiyuanlibao = 60								#是否使用过会员礼包的CDkey
F(huiyuanlibao, True)

chaozhihaoli = 61								#是否使用过超值好礼的CDkey
F(chaozhihaoli, True)

FaceBookLike = 62								#FaceBook Like完成状态
F(FaceBookLike, True)

quanminzhongqiulibao = 63								#是否使用全民中秋礼包的CDkey
F(quanminzhongqiulibao, True)

geilizhongqiulibao = 64								#是否使用过给力中秋礼包的CDkey
F(geilizhongqiulibao, True)

yongzhelibao = 65								#是否使用过勇者礼包的CDkey
F(yongzhelibao, True)

yingxionglibao = 66								#是否使用过英雄礼包的CDkey
F(yingxionglibao, True)

huihuanglibao = 67								#是否使用过辉煌礼包的CDkey
F(huihuanglibao, True)

zunguilibao = 68								#是否使用过给尊贵礼包的CDkey
F(zunguilibao, True)

FashionState = 69								#时装--是否跟新后第一次点登陆
F(FashionState, True)

FashionViewState = 70							#显示或屏蔽时装
F(FashionViewState, True)

jueshihaobao = 71								#是否使用过绝世好包的CDkey
F(jueshihaobao, True)

tuhaolibao = 72								#是否使用过土豪礼包的CDkey
F(tuhaolibao, True)

baiyinxinshouka = 73								#是否使用过白银新手卡的CDkey
F(baiyinxinshouka, True)

ST_WildBoss = 74						#野外寻宝
F(ST_WildBoss, True, isStatus = True)

tuiguanglibao = 75								#是否使用过推廣禮包的CDkey
F(tuiguanglibao, True)

huangjinxinshouka = 76								#是否使用过黄金新手卡的CDkey
F(huangjinxinshouka, True)

zhizunka = 77								#是否使用过至尊卡的CDkey
F(zhizunka, True)

QQMiniClientDownLoadReward = 78				#腾讯微端下载礼包领取记录
F(QQMiniClientDownLoadReward, True, "腾讯微端下载礼包领取记录")

shenhaixunbaolibao = 79								#是否使用过深海寻宝礼包的CDkey
F(shenhaixunbaolibao, True)

jinlingjianglibao1 = 80								#是否使用过金翎奖初级礼包的CDkey
F(jinlingjianglibao1, True)

jinlingjianglibao2 = 81								#是否使用过金翎奖中级礼包的CDkey
F(jinlingjianglibao2, True)

jinlingjianglibao3 = 82								#是否使用过金翎奖高级礼包的CDkey
F(jinlingjianglibao3, True)

jinlingjianglibao4 = 83								#是否使用过金翎奖超级礼包的CDkey
F(jinlingjianglibao4, True)

manelihe = 84								#是否使用过MyCard滿額禮盒的CDkey
F(manelihe, True)

fengsihaolibao = 85								#是否使用过FB粉絲好禮禮包的CDkey
F(fengsihaolibao, True)

Fbhaokanglibao = 86								#是否使用过FB好康禮包的CDkey
F(Fbhaokanglibao, True)

ST_UnionFB = 87									#[状态]是否在公会副本中
F(ST_UnionFB, True, isStatus = True)

Okdujialihe = 88								#是否使用过ok独家礼盒的CDkey
F(Okdujialihe, True)

quanjiadujialihe = 89								#是否使用过全家独家礼盒的CDkey
F(quanjiadujialihe, True)

ST_Halloween = 90								#状态万圣节宴会中
F(ST_Halloween, True, isStatus = True)

huanlelibao = 91								#是否使用过欢乐礼包的CDkey
F(huanlelibao, True)

changshuanglibao = 92								#是否使用过畅爽礼包的CDkey
F(changshuanglibao, True)

dumenhaokanglihe = 93								#是否使用过獨門好康禮盒的CDkey
F(dumenhaokanglihe, True)

darentequanlibao = 94								#是否使用过达人特权礼包CDkey
F(darentequanlibao, True)

QQMiniRoleBacklibao = 95						#微端回流礼包
F(QQMiniRoleBacklibao, True)

jingyinghaohuadalibao = 96							#是否使用过精英豪华大礼包CDkey
F(jingyinghaohuadalibao, True)

ST_JTGoToCross = 97								#状态是否可以从本服到跨服组队竞技场
F(ST_JTGoToCross, True, isStatus=True)

ST_JTMatch = 98									#【状态】组队竞技场匹配中
F(ST_JTMatch, True, isStatus = True)

chaozhijingxuanhaoli = 99							#是否使用过超值精选好礼的CDkey
F(chaozhijingxuanhaoli, True)

PackageHasPasswd = 100								#背包是否有密码，1有，0 没有 
F(PackageHasPasswd, True, "背包是否有密码")

jididafangsonglihe = 101							#是否使用过基地大放送礼盒的CDkey
F(jididafangsonglihe, True)

wajuejihuangjinlibao = 102							#是否使用过挖掘机黄金新手礼包的CDkey
F(wajuejihuangjinlibao, True)

meitizhuanshuchujilibao = 103							#是否使用过媒体专属初级礼包的CDkey
F(meitizhuanshuchujilibao, True)

meitizhuanshuzhongjilibao = 104							#是否使用过媒体专属中级礼包的CDkey
F(meitizhuanshuzhongjilibao, True)

meitizhuanshugaojilibao = 105							#是否使用过媒体专属高级礼包的CDkey
F(meitizhuanshugaojilibao, True)

PartyIsHost = 106				#是否举办过普通结婚Party
F(PartyIsHost, True)

ST_MarryParty = 107				#在结婚Party中
F(ST_MarryParty, True, isStatus = True)

FirstPay = 108					#是否首充
F(FirstPay, True)

QQBaiduLibao = 109
F(QQBaiduLibao, False, "百度搜索礼包")

shengdanhuanlelihe = 110							#是否使用过圣诞欢乐礼盒的CDkey
F(shengdanhuanlelihe, True)

zhuanshulibao1 = 111							#是否使用过专属礼包1的CDkey
F(zhuanshulibao1, True)

zhuanshulibao3 = 112							#是否使用过专属礼包3的CDkey
F(zhuanshulibao3, True)

zhuanshulibao5 = 113							#是否使用过专属礼包5的CDkey
F(zhuanshulibao5, True)

DownloadMicroend = 114							#是否领取下载微端奖励
F(DownloadMicroend, True)

dujialihe1 = 115							#是否使用过独家礼盒1的CDkey
F(dujialihe1, True)

dujialihe2 = 116							#是否使用过独家礼盒2的CDkey
F(dujialihe2, True)

longhubanglibao1 = 117							#是否使用过265G龙虎榜高级礼包的CDkey
F(longhubanglibao1, True)

longhubanglibao2 = 118							#是否使用过265G龙虎榜中级礼包的CDkey
F(longhubanglibao2, True)

longhubanglibao3 = 119							 #是否使用过265G龙虎榜初级礼包的CDkey
F(longhubanglibao3, True)

fengyunbanglibao = 120							#是否使用过风云榜礼包的CDkey
F(fengyunbanglibao, True)

haokanglihe1 = 121							#是否使用过好康禮盒(1)的CDkey
F(haokanglihe1, True)

haokanglihe2 = 122							#是否使用过好康禮盒(2)的CDkey
F(haokanglihe2, True)

haokanglihe3 = 123							#是否使用过好康禮盒(3)的CDkey
F(haokanglihe3, True)

haokanglihe4 = 124							#是否使用过好康禮盒(4)的CDkey
F(haokanglihe4, True)

haokanglihe5 = 125							#是否使用过好康禮盒(5)的CDkey
F(haokanglihe5, True)

shengdanchujilihe = 126						#是否使用过圣诞初级礼盒的CDkey
F(shengdanchujilihe, True)

shengdanzhongjilihe = 127					#是否使用过圣诞中级礼盒的CDkey
F(shengdanzhongjilihe, True)

shengdangaojilihe = 128						#是否使用过圣诞高级礼盒的CDkey
F(shengdangaojilihe, True)

changqiguanzhulihe = 129					#是否使用过微信长期关注礼盒的CDkey
F(changqiguanzhulihe, True)

longqishidarentequanlibao = 130							#是否使用过龙骑士达人特权礼包的CDkey
F(longqishidarentequanlibao, True)

shengdanhuodonglibao = 131							#是否使用过圣诞活动礼包的CDkey
F(shengdanhuodonglibao, True)

shengdanlihe1 = 132							#是否使用过圣诞礼盒1的CDkey
F(shengdanlihe1, True)

shengdanlihe2 = 133							#是否使用过圣诞礼盒2的CDkey
F(shengdanlihe2, True)

shengdanlihe3 = 134							#是否使用过圣诞礼盒3的CDkey
F(shengdanlihe3, True)

shengdanlihe4 = 135							#是否使用过圣诞礼盒4的CDkey
F(shengdanlihe4, True)

shengdanlihe5 = 136							#是否使用过圣诞礼盒5的CDkey
F(shengdanlihe5, True)

shengdanlihe6 = 137							#是否使用过圣诞礼盒6的CDkey
F(shengdanlihe6, True)

yuandanhuodonglibao = 138					#是否使用过元旦活动礼包的CDkey
F(yuandanhuodonglibao, True)

jingxuanlihe1 = 139					#是否使用过精选礼盒1的CDkey
F(jingxuanlihe1, True)

jingxuanlihe2 = 140					#是否使用过精选礼盒2CDkey
F(jingxuanlihe2, True)

ST_Zuma = 141						#[状态]天天消龙珠游戏中
F(ST_Zuma, True, isStatus = True)

meirichoujianglibao1 = 142							#是否使用过每日抽奖一星礼包的CDkey
F(meirichoujianglibao1, True)

meirichoujianglibao2 = 143							#是否使用过每日抽奖二星礼包的CDkey
F(meirichoujianglibao2, True)

meirichoujianglibao3 = 144							#是否使用过每日抽奖三星礼包的CDkey
F(meirichoujianglibao3, True)

ST_DailyFB = 145									#[状态]是否勇者试炼场中
F(ST_DailyFB, True, isStatus = True)

InUnion = 146						#是否在公会中
F(InUnion, True)

GoddessCardTurnOverFinal = 147		#女神卡牌终极翻牌
F(GoddessCardTurnOverFinal, True)

chujilibao1 = 148							#是否使用过初级礼包的CDkey
F(chujilibao1, True)

zhongjilibao1 = 149							#是否使用过中级礼包的CDkey
F(zhongjilibao1, True)

guhuilibao1 = 150							#是否使用过骨灰礼包的CDkey
F(guhuilibao1, True)

ST_DKCFight = 151								#[状态]龙骑试炼战斗
F(ST_DKCFight, True, isStatus = True)

guanjialibao = 152							#是否使用过管家礼包的CDkey
F(guanjialibao, True)

chujixinchundalibao = 153							#是否使用过初级新春大礼包的CDkey
F(chujixinchundalibao, True)

zhongjixinchundalibao = 154							#是否使用过中级新春大礼包的CDkey
F(zhongjixinchundalibao, True)

gaojixinchundalibao = 155							#是否使用过高级新春大礼包的CDkey
F(gaojixinchundalibao, True)

chunjiedarenlibao = 156							#是否使用过龙骑春节达人礼包的CDkey
F(chunjiedarenlibao, True)

qiandaolibao5 = 157							#是否使用过龙骑签到5日的CDkey
F(qiandaolibao5, True)

qiandaolibao10 = 158							#是否使用过龙骑签到10日的CDkey
F(qiandaolibao10, True)

qiandaolibao15 = 159							#是否使用过龙骑签到15日的CDkey
F(qiandaolibao15, True)

qiandaolibao20 = 160							#是否使用过龙骑签到20日的CDkey
F(qiandaolibao20, True)

weixinxinchunlibao = 161							#是否使用过微信春节礼包的CDkey
F(weixinxinchunlibao, True)

OpenYearGift = 162							#是否领取过开年礼包
F(OpenYearGift, True)

ST_DukeOnDuty = 163							#[状态]是否在城主轮值
F(ST_DukeOnDuty, True, isStatus = True)

yuanxiaojiemeitilibao = 164							#是否使用过元宵节媒体礼包的CDkey
F(yuanxiaojiemeitilibao, True)

changshuangjingying = 165							#是否使用过畅爽精英礼包的CDkey
F(changshuangjingying, True)

changshuanghuangjin = 166							#是否使用过畅爽黄金礼包的CDkey
F(changshuanghuangjin, True)

GMRoleFlag = 167							#GM标示
F(GMRoleFlag, True)

IsOldServerBack = 168							#是否是从老服回流至新服的玩家
F(IsOldServerBack, True, "是否老玩家回流至新服")

IsLocalServerBack = 169							#是否是从本服回流的玩家
F(IsLocalServerBack, True, "是否老玩家回流至老服")

yurenjiekuailelibao = 170						#是否使用过愚人节快乐礼包的CDkey
F(yurenjiekuailelibao, True)

QQHZTitle = 171				#QQ黄钻称号
F(QQHZTitle, True)

longqishihaohualibao = 172						#是否使用过愚人节快乐礼包的CDkey
F(longqishihaohualibao, True)

longqishifangkejingying = 173						#是否使用过愚人节快乐礼包的CDkey
F(longqishifangkejingying, True)

longqishifangkehuangjin = 174						#是否使用过愚人节快乐礼包的CDkey
F(longqishifangkehuangjin, True)

eluosihuanlelibao = 175						#是否使用过俄罗斯快乐礼包的CDkey
F(eluosihuanlelibao, True)

tuerqiyongzhelibao = 176						#是否使用过土耳其勇者礼包的CDkey
F(tuerqiyongzhelibao, True)

eluosihuanlelibao2 = 177						#是否使用过俄罗斯快乐礼包的CDkey
F(eluosihuanlelibao2, True)

wantonglibao = 178						#是否使用过玩童礼包的CDkey
F(wantonglibao, True)

ertongbuyilibao = 179						#是否使用过儿童不宜礼包的CDkey
F(ertongbuyilibao, True)

ST_DemonDefense = 180							#[状态]魔兽入侵
F(ST_DemonDefense, True, isStatus = True)

ST_HunluanSpace = 181							#[状态]混乱时空
F(ST_HunluanSpace, True, isStatus = True)

ST_GloryWar = 182								#[状态]荣耀之战
F(ST_GloryWar, True, isStatus = True)

weixinjingyinglibao = 183						#是否使用过微信精英礼包的CDkey
F(weixinjingyinglibao, True)

weixingaojilingbao = 184						#是否使用过微信高级礼包的CDkey
F(weixingaojilingbao, True)

KongJianRegressRewardFlag = 185						#是否领取了空间回归礼包
F(KongJianRegressRewardFlag, True)

ST_ClashOfTitans = 186							#[状态]诸神之战
F(ST_ClashOfTitans, True, isStatus=True)

shanyaogongcelibao = 187						#是否使用过闪耀公测礼包的CDkey
F(shanyaogongcelibao, True)

rexuegongcelibao = 188						#是否使用过热血公测礼包的CDkey
F(rexuegongcelibao, True)

wangzhegongcelibao = 189						#是否使用过王者公测礼包的CDkey
F(wangzhegongcelibao, True)

tulonggongcelibao = 190						#是否使用过屠龙公测礼包的CDkey
F(tulonggongcelibao, True)

FT_OldRoleBack_HasGotLoginReward = 191			#繁体老玩家回流是否获取过登录邮件奖励
F(FT_OldRoleBack_HasGotLoginReward, True)

FT_OldRoleBack_HasGotChargeReward = 192			#繁体老玩家回流是否获取过首充奖励
F(FT_OldRoleBack_HasGotChargeReward, True)

Is_FT_OldRoleBack = 193			#是否回流老玩家(繁体版)
F(Is_FT_OldRoleBack, True)

yingxionglibao2 = 194						#是否使用过英雄礼包礼包的CDkey
F(yingxionglibao2, True)

gongceweibolibao = 195						#是否使用过公测微博礼包的CDkey
F(gongceweibolibao, True)

guanjiagongcelibao = 196						#是否使用过龙骑士管家特权公测礼包的CDkey
F(guanjiagongcelibao, True)

IsActGSMall = 197					#是否激活GS返利商城
F(IsActGSMall, True)

xiaoxuelibaolibao = 198						#是否使用过小学礼包的CDkey
F(xiaoxuelibaolibao, True)

zhongxuelibaolibao = 199						#是否使用过中学礼包的CDkey
F(zhongxuelibaolibao, True)

daxuelibaolibao = 200						#是否使用过大学礼包的CDkey
F(daxuelibaolibao, True)

IsQQSummer = 201							#是否qq空间暑期活动用户
F(IsQQSummer, True, "是否qq空间暑期活动用户")

kongjianshuqilibao = 202						#是否使用过暑期礼包CDkey
F(kongjianshuqilibao, True)

bolanfengcelibao = 203						#是否使用过波兰礼包CDKey
F(bolanfengcelibao, True)

ST_QiangHongBao = 204							#[状态]抢红包
F(ST_QiangHongBao, True, isStatus=True)

eluosizaixianlibao1 = 205						#是否使用过俄罗斯在线礼包1的CDkey
F(eluosizaixianlibao1, True)

eluosizaixianlibao2 = 206						#是否使用过俄罗斯在线礼包2的CDkey
F(eluosizaixianlibao2, True)

eluosizaixianlibao3 = 207						#是否使用过俄罗斯在线礼包3的CDkey
F(eluosizaixianlibao3, True)

eluosizaixianlibao4 = 208						#是否使用过俄罗斯在线礼包4的CDkey
F(eluosizaixianlibao4, True)

eluosizaixianlibao5 = 209						#是否使用过俄罗斯在线礼包5的CDkey
F(eluosizaixianlibao5, True)

CTTNoRewardState = 210							#虚空幻境无奖励模式
F(CTTNoRewardState, True)

xplibao1 = 211						#是否使用过俄罗斯礼包1的CDkey
F(xplibao1, True)

xplibao2 = 212						#是否使用过俄罗斯礼包2的CDkey
F(xplibao2, True)

xplibao3 = 213						#是否使用过俄罗斯礼包3的CDkey
F(xplibao3, True)

eslibao1 = 214						#是否使用过俄罗斯es礼包1的CDkey
F(eslibao1, True)

plxplibao1 = 215						#是否使用过波兰联运礼包1的CDkey
F(plxplibao1, True)

plxplibao2 = 216						#是否使用过波兰联运礼包2的CDkey
F(plxplibao2, True)

plxplibao3 = 217						#是否使用过波兰联运礼包3的CDkey
F(plxplibao3, True)

kgglibao1 = 218						#是否使用过KGG礼包1的CDkey
F(kgglibao1, True)

guanjiajianianhualibao = 219						#是否使用管家嘉年华礼包的CDkey
F(guanjiajianianhualibao, True)

crea1 = 220						#是否使用过俄罗斯礼包1的CDkey
F(crea1, True)

crea2 = 221						#是否使用过俄罗斯礼包2的CDkey
F(crea2, True)

ShenshuAutoAcceptInvite = 222	#神树密境自动接受组队
F(ShenshuAutoAcceptInvite, True)

crea3 = 223						#是否使用过俄罗斯礼包3的CDkey
F(crea3, True)

crea4 = 224						#是否使用过俄罗斯礼包4的CDkey
F(crea4, True)

crea5 = 225						#是否使用过俄罗斯礼包5的CDkey
F(crea5, True)

crea6 = 226						#是否使用过俄罗斯礼包6的CDkey
F(crea6, True)

crea7 = 227						#是否使用过俄罗斯礼包7的CDkey
F(crea7, True)

crea8 = 228						#是否使用过俄罗斯礼包8的CDkey
F(crea8, True)

crea9 = 229						#是否使用过俄罗斯礼包9的CDkey
F(crea9, True)

crea10 = 230					#是否使用过俄罗斯礼包10的CDkey
F(crea10, True)

crea11 = 231					#是否使用过俄罗斯社交礼包11的CDkey
F(crea11, True)

ST_Shenshumijing = 232			#[状态]神数秘境
F(ST_Shenshumijing, True, isStatus = True)

longhubangchuji = 233						#是否使用过龙虎榜初级礼包的CDkey
F(longhubangchuji, True)

longhubanggaoshou = 234						#是否使用过龙虎榜高级礼包的CDkey
F(longhubanggaoshou, True)

longhubangguhui = 235						#是否使用过龙虎榜骨灰礼包的CDkey
F(longhubangguhui, True)

ST_MDragonCome = 236							#[状态]魔龙降临
F(ST_MDragonCome, True, isStatus = True)

ST_DeepHell = 237						#状态_深渊炼狱
F(ST_DeepHell, True, isStatus = True)

DemonDefenseIn = 238							#参与魔兽入侵
F(DemonDefenseIn, True)

MDragonComeIn = 239								#参与魔龙降临
F(MDragonComeIn, True)

fengyunbangzunguilibao = 240						#是否使用过风云榜尊贵礼包的CDkey
F(fengyunbangzunguilibao, True)

longqiyongshilibao = 241						#是否使用过龙骑勇者礼包的CDkey
F(longqiyongshilibao, True)

longqizunguilibao = 242						#是否使用过龙骑豪华礼包的CDkey
F(longqizunguilibao, True)

longqihaohualibao = 243						#是否使用过龙骑尊贵礼包的CDkey
F(longqihaohualibao, True)

longqizhizunlibao = 244						#是否使用过龙骑至尊礼包的CDkey
F(longqizhizunlibao, True)

shuangdanlibao = 245						#是否使用过双旦礼包的CDkey
F(shuangdanlibao, True)

crea12 = 246						#是否使用过俄罗斯礼包12的CDkey
F(crea12, True)

crea13 = 247						#是否使用过俄罗斯礼包13的CDkey
F(crea13, True)

crea14 = 248					#是否使用过俄罗斯礼包14的CDkey
F(crea14, True)

tongyonglibao1 = 249                    #是否使用过北美us2的CDkey
F(tongyonglibao1, True)

tengxunfengyunban = 250						#是否使用过风云榜礼包的CDkey
F(tengxunfengyunban, True)

handonglibao = 251						#是否使用过寒冬礼包的CDkey
F(handonglibao, True)

xuedilibao = 252						#是否使用过雪地礼包的CDkey
F(xuedilibao, True)

baiseyuandanlibao = 253						#是否使用过白色元旦礼包的CDkey
F(baiseyuandanlibao, True)

xinnianlibao = 254						#是否使用过新年礼包的CDkey
F(xinnianlibao, True)

crea15 = 255						#是否使用过俄罗斯OK礼包1的CDkey
F(crea15, True)

crea16 = 256						#是否使用过俄罗斯OK礼包2的CDkey
F(crea16, True)

crea17 = 257						#是否使用过俄罗斯OK礼包3的CDkey
F(crea17, True)

crea18 = 258						#是否使用过俄罗斯OK礼包4的CDkey
F(crea18, True)

crea19 = 259						#是否使用过俄罗斯OK礼包5的CDkey
F(crea19, True)

crea20 = 260						#是否使用过俄罗斯OK礼包6的CDkey
F(crea20, True)

crea21 = 261						#是否使用过俄罗斯101xp新年礼包1的CDkey
F(crea21, True)

crea22 = 262						#是否使用过俄罗斯101xp新年礼包2的CDkey
F(crea22, True)

crea23 = 263						#是否使用过俄罗斯101xp新年礼包3的CDkey
F(crea23, True)

crea24 = 264					#是否使用过俄罗斯礼包18的CDkey
F(crea24, True)

crea25 = 265					#是否使用过俄罗斯礼包19的CDkey
F(crea25, True)

EnumInt1_None = 266				#可复用
F(EnumInt1_None, True)

bolanlianyunlibao = 267					#是否使用过波兰联运礼包的CDkey
F(bolanlianyunlibao, True)

ChaosDivinityNoReward = 268					#混沌神域无奖励模式  0 关闭即使用次数    1开启  ，进入后不扣除奖励次数，不发奖
F(ChaosDivinityNoReward, True)

crea26 = 269						#是否使用过101xp(4)的CDkey
F(crea26, True)

crea27 = 270					#是否使用过101xp(5)的CDkey
F(crea27, True)

crea28 = 271					#是否使用过101xp(6)的CDkey
F(crea28, True)

crea29 = 272						#是否使用过RBK(1)的CDkey
F(crea29, True)

crea30 = 273					#是否使用过RBK(2)的CDkey
F(crea30, True)

crea31 = 274					#是否使用过101xp(7)的CDkey
F(crea31, True)

crea32 = 275						#是否使用过101xp(8)的CDkey
F(crea32, True)

crea33 = 276					#是否使用过101xp(9)的CDkey
F(crea33, True)

wenxinhounianxinchunlibao = 277					#是否使用过微信猴年新春礼包的CDkey
F(wenxinhounianxinchunlibao, True)

YuanXiaoHuaDeng = 278							#是否能使用花灯
F(YuanXiaoHuaDeng, True)

TheFristTimeYuanXiaoHuaDeng = 279				#是否第一次参加元宵活动
F(TheFristTimeYuanXiaoHuaDeng, True)

jinfatiaojiangdujialibao = 280					#是否使用过金发条奖独家礼包的CDkey
F(jinfatiaojiangdujialibao, True)

crea34 = 281					#是否使用过101xp(10)的CDkey
F(crea34, True)

crea35 = 282						#是否使用过RBK礼包(3)的CDkey
F(crea35, True)

crea36 = 283					#是否使用过101xp(11)的CDkey
F(crea36, True)

crea37 = 284					#是否使用过俄罗斯Esprit礼包(20)的CDkey
F(crea37, True)

crea38 = 285					#是否使用过俄罗斯Esprit礼包(21)的CDkey
F(crea38, True)

crea39 = 286					#是否使用过俄罗斯Esprit礼包(22)的CDkey
F(crea39, True)

crea40 = 287					#是否使用过俄罗斯Esprit礼包(23)的CDkey
F(crea40, True)

crea41 = 288					#是否使用过俄罗斯Esprit礼包(24)的CDkey
F(crea41, True)

crea42 = 289					#是否使用过俄罗斯Esprit礼包(25)的CDkey
F(crea42, True)

crea43 = 290					#是否使用过俄罗斯Esprit礼包(26)的CDkey
F(crea43, True)

QQLzFeedBackFirstrecharge = 291 #是否蓝钻回馈活动期间首充
F(QQLzFeedBackFirstrecharge,False)

enxp1 = 292					#是否使用过英文版礼包（1）的CDkey
F(enxp1, True)

crea44 = 293					#是否使用过101xp礼包(12)的CDkey
F(crea44, True)

IsGM = 294					#是否GM
F(IsGM, True)

FaceBookDrawState = 295		#FaceBookLike分享成功是否领取抽奖次数
F(FaceBookDrawState, True)

crea45 = 296					#是否使用过101xp礼包(13)的CDkey
F(crea45, True)

crea46 = 297					#是否使用过101xp礼包(14)的CDkey
F(crea46, True)

crea47 = 298					#是否使用过101xp礼包(15)的CDkey
F(crea47, True)

crea48 = 299					#是否使用过101xp礼包(16)的CDkey
F(crea48, True)

ElementFollowStatus = 300		#元素幻化外形跟随状态
F(ElementFollowStatus, True)

YYAntiState = 301				#YY防沉迷状态
F(YYAntiState, True)

pcl1 = 302                #北美新手礼包
F(pcl1, True)

lyyy1 = 303					#是否使用过yy新手卡礼包的CDkey
F(lyyy1, True)

lyyy2 = 304					#是否使用过yy特权卡礼包的CDkey
F(lyyy2, True)

lyyy3 = 305					#是否使用过YY VIP认证礼包的CDkey
F(lyyy3, True)

lyyy4 = 306					#是否使用过yyVIP新游礼包的CDkey
F(lyyy4, True)

lyyy5 = 307					#是否使用过yyVIP节日礼包的CDkey
F(lyyy5, True)

lyyy6 = 308					#是否使用过yy等级礼包的CDkey
F(lyyy6, True)

ly7k1 = 309					#是否使用过龙骑新手卡礼包的CDkey
F(ly7k1, True)

ly7k2 = 310					#是否使用过龙骑推广礼包1的CDkey
F(ly7k2, True)

ly7k3 = 311					#是否使用过龙骑推广礼包2的CDkey
F(ly7k3, True)

ly7k4 = 312					#是否使用过龙骑VIP礼包的CDkey
F(ly7k4, True)