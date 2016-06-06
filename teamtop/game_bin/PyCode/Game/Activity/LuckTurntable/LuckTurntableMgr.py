#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LuckTurntable.LuckTurntableMgr")
#===============================================================================
# 幸运转盘管理
#===============================================================================

import cRoleMgr
import Environment
from Game.Persistence import Contain
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Call, Event
from Game.Role.Data import EnumDayInt8, EnumInt32
from Game.Activity.LuckTurntable import LuckTurntableConfig
from Game.Activity.HappyNewYear import NewYearDiscount



if "_HasLoad" not in dir():
	CallBackSec = 20			#回调时间
	LuckPool_RMB = 1			#持久化字典奖池神石数索引
	LuckPool_Luckrole = 2		#持久化字典玩家中奖信息索引
	Luckrolelist_lenth = 8		#玩家中奖信息长度
	LuckPoolInit = 10000		#奖池初始化数量
	#消息
	LuckyTurntable_callback = AutoMessage.AllotMessage("LuckyTurntable_callback", "幸运转盘抽奖回调")
	LuckTurntable_role_list = AutoMessage.AllotMessage("LuckTurntable_role_list", "幸运转盘玩家中奖信息")

	#日志
	LuckyTurntableCost = AutoLog.AutoTransaction("LuckyTurntableCost", "参加幸运转盘扣除神石及增加当日次数")
	LuckyTurntableReward = AutoLog.AutoTransaction("uckyTurntableReward", "参加幸运转盘获取奖励")

def RequestLuckyTurntable(role,msg):
	'''
	客户端请求幸运大转盘
	@param role:
	@param msg:
	'''
	#判断玩家等级是否达到参加幸运转盘的最低要求
	if role.GetLevel() < EnumGameConfig.LuckTurntable_Need_level:
		return
	roleVIP = role.GetVIP()
	if role.GetVIP() < EnumGameConfig.LuckTurntable_Need_VIPlevel:
		return
	#判断次数是否超过该vip等级每日允许次数
	maxcnt_cfg = LuckTurntableConfig.LuckTurntable_Luckcnt_dict.get(roleVIP)
	if not maxcnt_cfg:
		print "GE_EXC, error in maxcnt_cfg = LuckTurntableConfig.LuckTurntable_Luckcnt_dict.get(roleVIP)"
		return

	if not role.GetDI8(EnumDayInt8.LuckTurntablecnt) < maxcnt_cfg.cnt:
		return

	needRMB = EnumGameConfig.LuckTurntablePrice
	#版本判断
	if Environment.EnvIsNA():
		needRMB = EnumGameConfig.LuckTurntablePrice_NA
	elif Environment.EnvIsRU():
		needRMB = EnumGameConfig.LuckTurntablePrice_RU
		
	#判断玩家神石是否足够，如果不足够
	if role.GetUnbindRMB() < needRMB:
		return
	luck_type = LuckTurntableConfig.LuckTurntable_Lucktype_dict.get(role.GetLevel())
	if not luck_type:
		print "GE_EXC, can not find luck_type(%s) in LuckTurntable_Award_dict for roleID(%s) " % (role.GetLevel(), role.GetRoleID())
		return
	rewardcfg = LuckTurntableConfig.LuckTurntable_Award_dict.get(luck_type.type)
	if not rewardcfg:
		print "GE_EXC, can not find luck_type(%s) in LuckTurntable_Award_dict for roleID(%s)" % (luck_type, role.GetRoleID())
		return
	#扣除玩家用于幸运转盘的神石
	with LuckyTurntableCost:
		role.DecUnbindRMB(needRMB)
		#增加当日玩家已参加幸运转盘的次数
		role.IncDI8(EnumDayInt8.LuckTurntablecnt,1)
		
		#新年乐翻天积分
		if NewYearDiscount.IsOpen:
			role.IncI32(EnumInt32.NewYearScore, needRMB)
		
	#获取玩家随机抽取的奖励
	rewardItems = rewardcfg(LuckPool[LuckPool_RMB]).RandomOne()
	#使用回调函数。传递玩家获取的奖励，并在回调后对玩家进行奖励，
	role.SendObjAndBack(LuckyTurntable_callback, rewardItems, CallBackSec, LuckyTurntable_Reward_callback, rewardItems)
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_LuckTurntable, 1))
	
def LuckyTurntable_Reward_callback(role, callargv, regparam):
	'''
	幸运转盘回调
	@param role:
	@param callargv:
	@param regparam:
	'''
	global LuckPool
	roleId = role.GetRoleID()
	rewardItems = regparam
	#判断奖励的是否无物品和数量组成的元组，如果不是则判断为神石数
	if type(rewardItems) != tuple:
		rewardrmb =int(rewardItems * LuckPool[LuckPool_RMB] / 100.0)
	else:
		Call.LocalDBCall(roleId, RewardRole, rewardItems)
		role.Msg(2, 0, GlobalPrompt.LuckTurntable_Item_award % rewardItems)
		rewardrmb = 0
			
	if rewardrmb > 0:
		Call.LocalDBCall(roleId, RewardRole, rewardrmb)
		LuckPool[LuckPool_RMB] -= rewardrmb
		LuckPool[LuckPool_Luckrole].append((role.GetRoleName(),rewardrmb))
		if len(LuckPool[LuckPool_Luckrole]) > Luckrolelist_lenth:
			LuckPool[LuckPool_Luckrole] = LuckPool[LuckPool_Luckrole][-Luckrolelist_lenth:]
		role.Msg(2, 0, GlobalPrompt.LuckTurntable_RMB_award % rewardrmb) 
		cRoleMgr.Msg(1, 0, GlobalPrompt.LuckTurntable_award % (role.GetRoleName(), rewardrmb))

	#增加奖池的神石数目
	LuckPool[LuckPool_RMB] += EnumGameConfig.LuckTurntableInc
	#打包消息，发送玩家信息以及奖池神石数目
	role.SendObj(LuckTurntable_role_list,(LuckPool[LuckPool_RMB], LuckPool[LuckPool_Luckrole]))



def RewardRole(role, regparam):
	'''
	奖励
	@param role:
	@param regparam:
	'''	
	rewardthing = regparam
	with LuckyTurntableReward:
		#如果奖励的为神石
		if type(rewardthing) == int:
			role.IncUnbindRMB_S(rewardthing)
		#如果奖励的为物品
		if type(rewardthing) == tuple:
			role.AddItem(*rewardthing)


def LuckTurntableAfterLoad():
	#数据载入后初始化
	global LuckPool
	if LuckPool_RMB not in LuckPool:
		LuckPool[LuckPool_RMB] = LuckPoolInit
	if LuckPool_Luckrole not in LuckPool:
		LuckPool[LuckPool_Luckrole] = []
		
def LuckTurntableBeforeSave():
	global LuckPool
	if len(LuckPool[LuckPool_Luckrole]) > Luckrolelist_lenth:
		LuckPool[LuckPool_Luckrole] = LuckPool[LuckPool_Luckrole][-Luckrolelist_lenth:]


def RequestLuckTurntableOpen(role, msg):
	'''
	请求打开幸运转盘面板
	@param role:
	@param msg:
	'''
	if len(LuckPool[LuckPool_Luckrole]) > Luckrolelist_lenth:
		LuckPool[LuckPool_Luckrole] = LuckPool[LuckPool_Luckrole][-Luckrolelist_lenth:]
	role.SendObj(LuckTurntable_role_list,(LuckPool[LuckPool_RMB], LuckPool[LuckPool_Luckrole]))


if "_HasLoad" not in dir():
	if (Environment.HasLogic or Environment.HasWeb) and not Environment.IsCross:
		LuckPool = Contain.Dict("LuckPool", (2038, 1, 1), LuckTurntableAfterLoad, LuckTurntableBeforeSave, isSaveBig = False)
	
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLuckyTurntable", "客户端请求幸运转盘"), RequestLuckyTurntable)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLuckTurntableOpen", "客户端请求打开幸运转盘面板"), RequestLuckTurntableOpen)



