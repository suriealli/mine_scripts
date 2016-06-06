#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DailyDo.DailyDo")
#===============================================================================
# 每日必做
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.DailyDo import DailyDoConfig
from Game.Role.Data import EnumObj, EnumInt16, EnumDayInt8, EnumTempObj, EnumDayInt1, EnumInt8
from Game.Activity.AutumnFestival import AutumnFestivalMgr
from Game.ThirdParty.QQidip import QQEventDefine
from Game.Activity.DragonStele import DragonSteleMgr
from Game.Activity.DoubleTwelve import FeastWheelMgr
from Game.Activity.Christmas import ChristmasWishTreeMgr
from Game.Activity.Holiday import HolidayMoneyWish
from Game.Activity.HappyNewYear import NYearOnlineRewardMgr
from Game.Activity.ZhongQiu import HuoYueDaLiMgr

if "_HasLoad" not in dir():
	DailyDoData = AutoMessage.AllotMessage("DailyDoData", "每日必做数据")
	
	DailyReward_Log = AutoLog.AutoTransaction("DailyReward_Log", "每日必做日志")
	
#===============================================================================
# 每日必做任务索引
#===============================================================================
Daily_JJC = 1						#竞技场
Daily_Dati = 2						#答题
Daily_DD = 3						#魔兽入侵
Daily_GW = 4						#荣耀之战
Daily_FB = 5						#副本
Daily_DT = 6						#巨龙宝藏
Daily_P = 7							#心魔炼狱
Daily_UG = 8						#公会魔神
Daily_Gold = 9						#炼金
Daily_EH = 10						#恶魔深渊
Daily_Slave = 11					#奴隶互动
Daily_WildBoss = 12					#野外寻宝
Daily_StarGirlDivine = 13			#星灵普通占星
Daily_StarGirlLvUp = 14				#星灵升级
Daily_DragonTrain = 15				#神龙聚灵
Daily_DragonVeinLvUp = 16			#龙脉升级
Daily_UnionShenShou = 17			#公会神兽培养
Daily_ShenshumijingPeiyang = 18	#神数秘境培养
Daily_MDragonCome = 19				#魔龙降临

def DoDailyDo(role, param):
	'''
	做每日必做
	@param role:
	@param param:任务索引, 完成次数
	'''
	index, cnt = param
	
	cfg = DailyDoConfig.DailyDo_Dict.get(index)
	if not cfg:
		print "GE_EXC, DailyDo can not find index:(%s) in DailyDo_Dict" % index
		return
	if cfg.level_limit > role.GetLevel():
		return
	finish_cnt = role.GetObj(EnumObj.DailyDoDict)[1].get(index, 0)
	if finish_cnt >= cfg.max_cnt:
		return
		
	with DailyReward_Log:
		if cfg.max_cnt < cnt:
			cnt = cfg.max_cnt
		if finish_cnt + cnt > cfg.max_cnt:
			add_score_cnt = cfg.max_cnt - finish_cnt
			role.GetObj(EnumObj.DailyDoDict)[1][index] = cfg.max_cnt
		else:
			add_score_cnt = cnt
			role.GetObj(EnumObj.DailyDoDict)[1][index] = finish_cnt + cnt
		role.IncI16(EnumInt16.DailyDoScore, cfg.score * add_score_cnt)
	role.SendObj(DailyDoData, role.GetObj(EnumObj.DailyDoDict))
	
	#版本判断
	if Environment.EnvIsNA():
		#开服活动
		kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		kaifuActMgr.daily_do_score()
	
	if index == 3:
		Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_MoShouRuQin)
	elif index == 4:
		Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_GloyWar)
	
	#激情活动——激情有礼触发
	from Game.Activity.PassionAct import PassionGiftMgr
	if PassionGiftMgr.IS_START:
		dailyDoScore = role.GetI16(EnumInt16.DailyDoScore)
		isAccu = role.GetDI1(EnumDayInt1.PassionGift_IsAccu)
		#活动开启 && 今日积分够了 && 今日没有累计到总次数
		if (not isAccu) and dailyDoScore >= EnumGameConfig.PassionGift_TargetScore:
			role.IncI8(EnumInt8.PassionGiftAccuCnt, 1)
			role.SetDI1(EnumDayInt1.PassionGift_IsAccu, 1)
		
	
def Award(role, index):
	has_award_set = role.GetObj(EnumObj.DailyDoDict)[2]
	if index in has_award_set:
		return
	
	level = GetCloseValue(role.GetLevel(), DailyDoConfig.DailyDo_Reward_List)
	if not level:
		return
	
	cfg = DailyDoConfig.DailyDo_Reward_Dict.get((index, level))
	if not cfg:
		print "GE_EXC, DailyDo can not find index %s, level %s in DailyDo_Reward_Dict" % (index, level)
		return
	if role.GetI16(EnumInt16.DailyDoScore) < cfg.need_score:
		return
	
	tili, items, bindRMB, money, union_exp, union_contribution = cfg.getReward(role.GetAnti())
	
	has_award_set.add(index)
	with DailyReward_Log:
		role.GetObj(EnumObj.DailyDoDict)[2] = has_award_set
		tips = ''
		if tili:
			role.IncTiLi(tili)
			tips += GlobalPrompt.TiLi_Tips % tili
		#中秋搏饼开启：每日必做宝箱增加一次搏饼次数
		if AutumnFestivalMgr.IS_START_LATTERY:
			role.IncDI8(EnumDayInt8.AF_LatteryDailyBoxNum, 1)
		if items:
			for item in items:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
		if bindRMB:
			role.IncBindRMB(bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % bindRMB
		if money:
			role.IncMoney(money)
			tips += GlobalPrompt.Money_Tips % money
		if union_exp:
			unionObj = role.GetUnionObj()
			if unionObj:
				unionObj.IncUnionExp(union_exp)
				tips += GlobalPrompt.UnionExp_Tips %union_exp
				if union_contribution:
					role.IncContribution(union_contribution)
					tips += GlobalPrompt.UnionContribution_Tips % union_contribution
			
		#龙魂石碑开启状态下奖励金龙币
		jlbCnt = cfg.jlb
		if jlbCnt > 0 and DragonSteleMgr.IS_START:
			role.AddItem(EnumGameConfig.DragonStele_PrayPro_Special, jlbCnt)
			tips += GlobalPrompt.Item_Tips % (EnumGameConfig.DragonStele_PrayPro_Special, jlbCnt)
		
		#盛宴摩天轮增加普通抽奖次数
		feastWheelNomalTimes = cfg.feastWheelNomalTimes
		if feastWheelNomalTimes > 0 and FeastWheelMgr.IS_START:
			role.IncDI8(EnumDayInt8.FeastWheelNomalTimes, feastWheelNomalTimes)
			tips += GlobalPrompt.LoveTogether_Tips_FWTimes % feastWheelNomalTimes
			
		#圣诞许愿树袜子
		christmasStockings = cfg.christmasStockings
		if  christmasStockings > 0 and ChristmasWishTreeMgr.IS_START:
			role.AddItem(EnumGameConfig.ChristmasWishTree_SockCoding, christmasStockings)
			tips += GlobalPrompt.Item_Tips % (EnumGameConfig.ChristmasWishTree_SockCoding, christmasStockings)
			
		#元旦金币祈福次数
		holidayWishCnt = cfg.holidayWishCnt
		if holidayWishCnt > 0 and HolidayMoneyWish.IsOpen:
			role.IncDI8(EnumDayInt8.HolidayWishCnt, holidayWishCnt)
			tips += GlobalPrompt.HolidayOnlineReward_Tips_prayTimes % holidayWishCnt
		
		#新年冲冲冲免费抽奖次数
		newYearFreeTimes = cfg.newYearFreeTimes
		if newYearFreeTimes > 0 and NYearOnlineRewardMgr.IS_START:
			role.IncDI8(EnumDayInt8.NYearFreeTimes, newYearFreeTimes)
			tips += GlobalPrompt.NYEAR_ONLINE_FREE_TIMES_MSG % newYearFreeTimes
			
		#中秋活跃大礼有效前进步数
		huoYueDaLiSteps = cfg.huoYueDaLiSteps
		if huoYueDaLiSteps > 0 and HuoYueDaLiMgr.IS_START:
			role.IncI8(EnumInt8.HuoYueDaLi_EffectStep, huoYueDaLiSteps)
			tips += GlobalPrompt.HuoYueDaLi_Tips_Steps % huoYueDaLiSteps
			
	role.SendObj(DailyDoData, role.GetObj(EnumObj.DailyDoDict))
	if tips:
		role.Msg(2, 0, GlobalPrompt.Reward_Tips + tips)
	if role.GetAnti() == -1:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
def GetCloseValue(value, value_list):
	tmp_level = 0
	for i in value_list:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		#没有找到返回最后一个值
		return tmp_level
#===============================================================================
# 每日清理
#===============================================================================
def DayClear(role, param):
	role.SetObj(EnumObj.DailyDoDict, {1:{}, 2:set()})
	role.SendObj(DailyDoData, role.GetObj(EnumObj.DailyDoDict))
	role.SetI16(EnumInt16.DailyDoScore, 0)
	
def SyncData(role, param):
	role.SendObj(DailyDoData, role.GetObj(EnumObj.DailyDoDict))
#===============================================================================
# 客户端请求
#===============================================================================
def RequestAward(role, msg):
	'''
	请求领取积分奖励
	@param role:
	@param msg:
	'''
	if not msg:
		return
	
	if role.GetLevel() < EnumGameConfig.Daily_Level_Limit:
		return
	
	Award(role, msg)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, DayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_DoDailyDo, DoDailyDo)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DailyDo_Award", "请求领取每日必做积分奖励"), RequestAward)
		
