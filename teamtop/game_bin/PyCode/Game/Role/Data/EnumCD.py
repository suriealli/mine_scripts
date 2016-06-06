#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumCD")
#===============================================================================
# 角色CD数组使用枚举
#===============================================================================
import cRoleDataMgr
from Common import Coding


if "_HasLoad" not in dir():
	checkEnumSet = set()

def F(uIdx, bSyncClient = False):
	'''
	设置数值规范
	@param uIdx:下标索引
	@param bSyncClient:数值改变了是否同步客户端
	'''
	assert uIdx < (Coding.RoleCDRange[1] - Coding.RoleCDRange[0])
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumCD rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	cRoleDataMgr.SetCDRule(uIdx, bSyncClient)

#===============================================================================
# 数组使用定义 同步给客户端时，是UNIX时间， GetCD 返回的是剩余秒数
#===============================================================================
En_None = 0 #占位
F(En_None, True)

Fight_Cool_Down = 1 #战斗CD
F(Fight_Cool_Down)

TeamTowerWorldCall = 2 #组队爬塔世界邀请CD 
F(TeamTowerWorldCall, True)

Social_Retry = 3 #刷新好友信息CD
F(Social_Retry)

JJC_Challenge_CD = 4 #竞技场挑战CD
F(JJC_Challenge_CD, True)

Social_Near_CD = 5 #请求附近玩家CD
F(Social_Near_CD)

ConfirmTeamFollowCD = 6 #请求确认跟随的队员的消息处理CD
F(ConfirmTeamFollowCD, True)

FB_GuaJiCD	 = 7 #副本挂机CD
F(FB_GuaJiCD, True)

EquipmentForintCD = 8 #记录玩家强化装备加的CD
F(EquipmentForintCD, True)

ForbidEquipmentCD = 9 #禁止玩家强化的CD
F(ForbidEquipmentCD, True)

Gold_Call_CD = 10#炼金招募CD
F(Gold_Call_CD, True)

GT_Rob_CD = 11 #劫宝战斗冷却CD
F(GT_Rob_CD, True)

GT_Occ_CD = 12 #劫宝占领
F(GT_Occ_CD, True)

Duty_CD = 13 #城主轮值战斗失败CD
F(Duty_CD, True)

DD_Fight_CD = 14 #魔兽入侵战斗CD
F(DD_Fight_CD, True)

JOIN_Duty_CD = 15 #进城主轮值的CD
F(JOIN_Duty_CD, True)

Card_Week = 16			#周卡
F(Card_Week, True)
Card_Month = 17			#月卡
F(Card_Month, True)
Card_HalfYear = 18		#半年卡
F(Card_HalfYear, True)

GloryWarFightCD = 19 #荣耀之战pvp战斗cd
F(GloryWarFightCD, True)

TwelvePalaceHelpCD = 20 #勇闯十二宫请求协助CD
F(TwelvePalaceHelpCD, True)

MarryFilterCD = 21	#筛选结婚对象CD
F(MarryFilterCD, True)

MarryLibaoCD = 22	#领取结婚礼包CD
F(MarryLibaoCD, True)

MarryInviteCD = 23	#婚礼邀请CD
F(MarryInviteCD, True)

Cou_ForbidMoveCD = 24	#情缘副本禁止移动CD
F(Cou_ForbidMoveCD, True)

Cou_MoveFB = 25		#情缘副本移动CD
F(Cou_MoveFB, True)

Cou_BuffCD = 26		#情缘副本buffCD
F(Cou_BuffCD, True)

HeroAltarDiscountCD = 27	#英雄祭坛折扣召唤CD
F(HeroAltarDiscountCD, True)

UnionJoinCD = 28		#加入公会CD
F(UnionJoinCD, True)

Card_Quarter = 29		#季度卡
F(Card_Quarter, True)
Card_Year = 30			#年卡
F(Card_Year, True)

GVEWorldCallCD = 31		#GVE世界邀请CD
F(GVEWorldCallCD, True)

FT_JJC_CD = 32			#繁体版竞技场挑战CD
F(FT_JJC_CD, True)

CardUMCD = 33			#月卡赠送返回公会成员CD
F(CardUMCD, True)

DailySeckillCD = 34		#天天秒杀的cd
F(DailySeckillCD, True)

WildBossFastFightCD = 35		#野外夺宝追杀CD
F(WildBossFastFightCD, True)

WildBossFightCD = 36			#野外寻宝战斗冷却cd
F(WildBossFightCD, True)

WildBossProtectCD = 37	#野外寻宝战斗保护cd
F(WildBossProtectCD, True)

StarGirlPower1 = 40		#星灵之力1
StarGirlPower2 = 41		#星灵之力2
StarGirlPower3 = 42		#星灵之力3
StarGirlPower4 = 43		#星灵之力4
StarGirlPower5 = 44		#星灵之力5
StarGirlPower6 = 45		#星灵之力6
StarGirlPower7 = 46		#星灵之力7
StarGirlPower8 = 47		#星灵之力8
StarGirlPower9 = 48		#星灵之力9
StarGirlPower10 = 49	#星灵之力10
StarGirlPower11 = 50	#星灵之力11
StarGirlPower12 = 51	#星灵之力12
F(StarGirlPower1, True)
F(StarGirlPower2, True)
F(StarGirlPower3, True)
F(StarGirlPower4, True)
F(StarGirlPower5, True)
F(StarGirlPower6, True)
F(StarGirlPower7, True)
F(StarGirlPower8, True)
F(StarGirlPower9, True)
F(StarGirlPower10, True)
F(StarGirlPower11, True)
F(StarGirlPower12, True)

KuaFuJJCFinalsRefreshCD = 52		#跨服个人竞技场决赛手动刷新CD
F(KuaFuJJCFinalsRefreshCD, True)

HunluanSpaceCD = 53				#混乱时空CD
F(HunluanSpaceCD, True)


JTMatchCD = 54			#组队竞技场匹配CD
F(JTMatchCD, True)

PartyInviteCD = 55				#结婚派对邀请伴侣cd
F(PartyInviteCD, True)

PartyWorldIvCD = 56				#结婚派对世界邀请cd
F(PartyWorldIvCD, True)

UnionTaskInviteCD = 57			#公会任务邀请提星CD
F(UnionTaskInviteCD, True)

UnionKuaFuWarFightCD = 58		#公会圣域争霸战斗CD
F(UnionKuaFuWarFightCD, True)

WaiGuaChance = 59					#第一次使用外挂提示5分钟
F(WaiGuaChance, False)

dengjiang4 = 60					#------------------可以复用
F(dengjiang4, True)

dengjiang5 = 61					#------------------可以复用
F(dengjiang5, True)

dengjiang6 = 62					#------------------可以复用
F(dengjiang6, True)

JTGroupSignUpCD = 63			#跨服争霸赛小组报名CD
F(JTGroupSignUpCD)

JTCrossZBChampionReward_1 = 64				#是否可以领取跨服争霸冠军奖励(天榜)
F(JTCrossZBChampionReward_1, True)

JTCrossZBChampionReward_2 = 65				#是否可以领取跨服争霸冠军奖励(地榜)
F(JTCrossZBChampionReward_2, True)

DailyFBFightDelta = 66		#勇者试炼场战斗CD
F(DailyFBFightDelta, True)

UnionMallGviingCD = 67		#商城赠送获取公会成员CD
F(UnionMallGviingCD, True)

HoneymoonSayCD = 68			#蜜月甜言蜜语cd
F(HoneymoonSayCD, True)

CrazyShoppingCD = 69		#疯狂抢购乐的cd
F(CrazyShoppingCD, True)


PartyKuafuWInviteCD = 70		#跨服派对世界邀请cd
F(PartyKuafuWInviteCD, True)

PartyKuafuMInviteCD = 71		#跨服派对伴侣邀请cd
F(PartyKuafuMInviteCD, True)

GloryWarClickFailCD = 72		#荣耀之战战败cd
F(GloryWarClickFailCD, True)

TarotSuperZhanbuCD = 73
F(TarotSuperZhanbuCD, True)

QingMingQuanMingLianJin = 74	#清明节活动全民炼金buff cd
F(QingMingQuanMingLianJin, True)

UnionDukeCD = 75				#退出公会24小时内不能参加城主轮值
F(UnionDukeCD, True)

ClashOfTitansFight = 76			#诸神之战战斗CD
F(ClashOfTitansFight, True)

WarStationCD = 77		#战阵系统CD
F(WarStationCD, True)

CrossTeamTower = 78		#虚空幻境世界邀请CD
F(CrossTeamTower, True)

CroSSTPCD = 79			#点击进入虚空幻境CD
F(CroSSTPCD, True)

ZhongQiuLianJinCD = 80	#中秋节活动全民炼金buff cd
F(ZhongQiuLianJinCD, True)

JTInviteToCrossCD = 81 #跨服组队竞技邀请进入CD
F(JTInviteToCrossCD, True)

CrossWorldChatCD = 82	#跨服世界聊天CD
F(CrossWorldChatCD, False)

LostSceneWorldInviteCD = 83	#迷失之境世界邀请cd
F(LostSceneWorldInviteCD, True)



DEQiangHongBaoCD = 84		#双十一抢红包CD
F(DEQiangHongBaoCD, True)


TouchGoldCD = 85	#点石成金获取原石CD
F(TouchGoldCD, True)

PuzzleCD = 86         #趣味拼图的cd
F(PuzzleCD,True)

MD_Fight_CD = 87 #魔龙入侵战斗CD
F(MD_Fight_CD, True)


DeepHellFightCD = 88			#深渊炼狱战斗冷却cd
F(DeepHellFightCD, True)

DeepHellProtectCD = 89			#深渊炼狱战斗保护cd
F(DeepHellProtectCD, True)

ChaosDivinityWorldCall = 90		#混沌神域世界邀请
F(ChaosDivinityWorldCall, True)

KFZC_Fight_CD = 91				#跨服战场点击cd
F(KFZC_Fight_CD, True)
