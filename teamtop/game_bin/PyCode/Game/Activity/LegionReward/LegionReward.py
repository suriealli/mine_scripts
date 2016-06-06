#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LegionReward.LegionReward")
#===============================================================================
# 七日礼包
#===============================================================================
import cRoleMgr
import cDateTime
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Util import Time
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumDayInt1, EnumInt8, EnumDisperseInt32, EnumInt1
from Game.Activity.LegionReward import LegionRewardConfig 
import Environment

if '_HasLoad' not in dir():
	MAX_LEGION_DAY = 8 #定义记录最大的登录天数
	SEVEN_REWARD_TIMES = 7 #七日礼包领取次数
	GET_REWARD_LEVEL = 32 #开启等级
	#消息
	Legion_Least_Seven_State = AutoMessage.AllotMessage("Legion_Least_Seven_State", "同步已领取七日奖励列表")
	Legion_Least_State = AutoMessage.AllotMessage("Legion_Least_State", "同步已领取登录奖励列表")
	Legion_Legion_CallBack = AutoMessage.AllotMessage("Legion_Legion_CallBack", "登录礼包转盘回调")
	
def RequestGetSevenReward(role, msg):
	'''
	请求获取七日礼包奖励
	@param role:
	@param msg:
	'''
	DayIndex = msg
	global GET_REWARD_LEVEL
	if role.GetLevel() < GET_REWARD_LEVEL:
		return
	#获取玩家已领取列表
	GetedRewards = role.GetObj(EnumObj.LEGION_REWARD)
	if not GetedRewards:
		return
	geted_list = GetedRewards.get(1)
	#已领取
	if DayIndex in geted_list:
		return
	
	#通过天数获取对应的配置文件
	cfg = LegionRewardConfig.LEGION_SEVEN_REWARD.get(DayIndex)
	if not cfg:
		print "GE_EXC, can not find LegionSevenReward index (%s)" % DayIndex
		#封包检测
		role.WPE()
		return
	
	#获取玩家的登录天数
	LegionNum = role.GetI8(EnumInt8.LegionDays)
	#登录次数不足
	if LegionNum < DayIndex:
		return

	#背包空间不足
	if role.PackageEmptySize() < len(cfg.rewards):
		role.Msg(2, 0, GlobalPrompt.NavicePackLessPackage)
		return
	#加入到已领取列表
	GetedRewards[1].add(DayIndex)
#	#激活登录奖励
#	rewardState = role.GetI1(EnumInt1.LegionRewardState)
#	if not rewardState:
#		if len(GetedRewards[1]) >= SEVEN_REWARD_TIMES and role.GetI8(EnumInt8.LegionDays) >= MAX_LEGION_DAY:
#			role.SetI1(EnumInt1.LegionRewardState, 1)
				
	with LegionSevenReward:
		role.Msg(2, 0, GlobalPrompt.Purgatory_Revive_Success)
		tips = ""
		for rd in cfg.rewards:
			role.AddItem(*rd)
			tips += GlobalPrompt.Item_Tips % (rd[0], rd[1])
		#玩家是否有月卡
		if role.IsMonthCard():
			if cfg.cardRewards:
				for crd in cfg.cardRewards:
					role.AddItem(*crd)
					tips += GlobalPrompt.Item_Tips % (crd[0], crd[1])
			if cfg.cardMoney:
				role.IncMoney(cfg.cardMoney)
				tips += GlobalPrompt.Money_Tips % cfg.cardMoney
		if cfg.addHero:
			role.AddHero(cfg.addHero)
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		if cfg.addTarot:
			role.AddTarotCard(cfg.addTarot, 1)
			tips += GlobalPrompt.Tarot_Tips % (cfg.addTarot, 1)
		role.Msg(2, 0, tips)
	role.SendObj(Legion_Least_Seven_State, GetedRewards.get(1))
	
def RequestOpenWin(role, msg):
	'''
	客户端请求打开七日礼包界面
	@param role:
	@param msg:
	'''
	role.SendObj(Legion_Least_Seven_State, role.GetObj(EnumObj.LEGION_REWARD).get(1))
	
def RequestOpemPanel(role, msg):
	'''
	客户端请求打开登录奖励界面
	@param role:
	@param msg:
	'''
	return
	
	if not role.GetI1(EnumInt1.LegionRewardState):
		return
	GetedRewards = role.GetObj(EnumObj.LEGION_REWARD)
	role.SendObj(Legion_Least_State, GetedRewards.get(2))
	
def RequestGetReward(role, msg):
	'''
	请求获取登录奖励
	@param role:
	@param msg:
	'''
	return
	
	global SEVEN_REWARD_TIMES
	GetedRewards = role.GetObj(EnumObj.LEGION_REWARD)
	#七日奖励没领取完
	if len(GetedRewards[1]) < SEVEN_REWARD_TIMES:
		return
	#获取玩家的登录天数
	LegionNum = role.GetI8(EnumInt8.LegionDays)
	if LegionNum <= SEVEN_REWARD_TIMES:
		return
	#已领取
	if role.GetDI1(EnumDayInt1.GetLegionRewardState):
		return
	cfg, rewardId = RandomReward(role)
	if not cfg or not rewardId:
		return
	if cfg.itemconfig and cfg.cnt:
		#判断背包
		if role.PackageEmptySize() < 1:
			#提示
			role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
			return
	role.SetDI1(EnumDayInt1.GetLegionRewardState, 1)
	#加入玩家已领取列表中
	GetedRewards[2].add(rewardId)
	role.SendObjAndBack(Legion_Legion_CallBack, [rewardId], 120, CallBackPayReward, [cfg, rewardId])

def CallBackPayReward(role, callargv, regparam):
	cfg, _ = regparam
	GetedRewards = role.GetObj(EnumObj.LEGION_REWARD)	
	with LegionReward:
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			role.SendObj(Legion_Least_State, GetedRewards.get(2))
			role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % cfg.bindRMB)
			return
		if cfg.itemconfig and cfg.cnt:
			role.AddItem(cfg.itemconfig, cfg.cnt)
			role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (cfg.itemconfig, cfg.cnt))
	role.SendObj(Legion_Least_State, GetedRewards.get(2))
#==============================
def RandomReward(role):
	'''
	#随机一个未获得过的奖励
	@param role:
	'''
	rewardId= LegionRewardConfig.GetRandomOne(role)
	cfg = LegionRewardConfig.LEGION_REWARD.get(rewardId)
	if not cfg:
		print "GE_EXC,can not find rewardId=(%s) in RandomReward149" % rewardId
		return None, 0
	return cfg,rewardId	

def RoleLogin(role, param):
	state = role.GetDI1(EnumDayInt1.LegionRewardState)
	#玩家当天第一次登录
	if not state:
		if role.GetI8(EnumInt8.LegionDays) <= MAX_LEGION_DAY:
			role.IncI8(EnumInt8.LegionDays, 1)
		role.SetDI1(EnumDayInt1.LegionRewardState, 1)
	GetedRewards = role.GetObj(EnumObj.LEGION_REWARD)
	role.SendObj(Legion_Least_Seven_State, GetedRewards.get(1))
	return
	
	rewardState = role.GetI1(EnumInt1.LegionRewardState)
	if not rewardState:
		
		if len(GetedRewards[1]) >= SEVEN_REWARD_TIMES:
			if role.GetI8(EnumInt8.LegionDays) >= MAX_LEGION_DAY:
				role.SetI1(EnumInt1.LegionRewardState, 1)
			role.SendObj(Legion_Least_Seven_State, GetedRewards.get(1))
		else:
			if role.GetLevel() >= GET_REWARD_LEVEL:
				role.SendObj(Legion_Least_Seven_State, GetedRewards.get(1))

def SyncRoleOtherData(role, param):
	GetedRewards = role.GetObj(EnumObj.LEGION_REWARD)
	role.SendObj(Legion_Least_Seven_State, GetedRewards.get(1))
		
def RoleDayClear(role, param):
	'''
	每日清理
	'''
	state = role.GetDI1(EnumDayInt1.LegionRewardState)
	if not state:
		if role.GetI8(EnumInt8.LegionDays) <= MAX_LEGION_DAY:
			role.IncI8(EnumInt8.LegionDays, 1)
		role.SetDI1(EnumDayInt1.LegionRewardState, 1)
	
	return
	
	rewardState = role.GetI1(EnumInt1.LegionRewardState)
	if not rewardState:
		GetedRewards = role.GetObj(EnumObj.LEGION_REWARD)
		if len(GetedRewards[1]) >= SEVEN_REWARD_TIMES:
			if role.GetI8(EnumInt8.LegionDays) >= MAX_LEGION_DAY:
				role.SetI1(EnumInt1.LegionRewardState, 1)
	#============每周5清理=============
	GetedRewards = role.GetObj(EnumObj.LEGION_REWARD)
	#获取当前时间
	cnow_time = cDateTime.Now()
	now_time = Time.DateTime2UnitTime(cnow_time)
	week_day = Time.GetWeekDay(cnow_time)
	if week_day == 5 or len(GetedRewards[2]) >= 7:
		GetedRewards[2] = set()
		GetedRewards[3] = now_time
	else:
		last_time = 0
		if not GetedRewards.get(3):
			#获取最后活跃时间
			last_time = role.GetDI32(EnumDisperseInt32.LastSaveUnixTime)
		else:
			last_time = GetedRewards.get(3)
		clast_time = Time.UnixTime2DateTime(last_time)
		last_week_day = Time.GetWeekDay(clast_time)			
		#两个时间相隔的天数
		keep_day, _ = divmod(now_time - last_time, 24 * 3600)
		tbool = False
		if last_week_day < 5:#上次登录周数小于周五
			if last_week_day + keep_day >= 5:
				tbool = True		
		else:#上传登录时为5,6,7
			if keep_day  >= 12 - last_week_day:
				tbool = True
		if tbool:
			GetedRewards[2] = set()
			GetedRewards[3] = now_time
			role.SendObj(Legion_Least_State, GetedRewards.get(2))
			
if '_HasLoad' not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, RoleLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#日志
		LegionSevenReward = AutoLog.AutoTransaction("LegionSevenReward", "七日登录奖励")
		LegionReward = AutoLog.AutoTransaction("LegionReward", "登录奖励")
	
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_Legion_Seven_Rewards", "客户端请求获取七日礼包奖励"), RequestGetSevenReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_Legion_Seven_Open", "客户端请求打开七日礼包界面"), RequestOpenWin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_Legion_Rewards_Open", "客户端请求打开登录奖励界面"), RequestOpemPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_Legion_Rewards", "客户端请求获取登录奖励"), RequestGetReward)
		
	