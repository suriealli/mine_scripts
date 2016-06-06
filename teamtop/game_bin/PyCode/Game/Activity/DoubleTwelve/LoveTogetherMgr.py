#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.LoveTogetherMgr")
#===============================================================================
# 爱在一起Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.DoubleTwelve import LoveTogetherConfig
from Game.Role.Data import EnumInt16, EnumInt32, EnumDayInt8

ONE_MINUTE_SECONDS = 60

if "_HasLoad" not in dir():
	IS_START = False	#活动开关标志
	
	Tra_LoveTogether_OnlineReward = AutoLog.AutoTransaction("Tra_LoveTogether_OnlineReward", "爱在一起在线奖励领取")

#### 活动控制 start ####
def OnStartLoveTogether(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_DTLoveTogether != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open LoveTogether"
		return
		
	IS_START = True
	#给所有在线满足条件的玩家注册TICK
	for tmpRole in cRoleMgr.GetAllRole():
		if tmpRole.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
			continue
		tmpRole.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnEndLoveTogether(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_DTLoveTogether != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end LoveTogether while not start"
		return
		
	IS_START = False

#### 请求 start ####
def OnGetOnlineReward(role, msg):
	'''
	请求领取在线奖励
	@param msg: rewardIndex
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	#对应奖励项不存在
	rewardIndex = msg
	rewardCfg = LoveTogetherConfig.LoveTogether_OnlineReward_Dict.get(rewardIndex)
	if not rewardCfg:
		return
	
	#已领取该项奖励
	rewardRecord = role.GetI32(EnumInt32.LoveTogether_OnlineRewardRecord)
	if rewardIndex & rewardRecord:
		return
	
	#在线时间不够
	onlineMinutes = role.GetI16(EnumInt16.LoveTogetherOnLineMinutes)
	if onlineMinutes < rewardCfg.needOnlineMins:
		return

	rewardPrompt = GlobalPrompt.LoveTogether_Tips_Head	
	with Tra_LoveTogether_OnlineReward:
		#更新领取记录
		role.IncI32(EnumInt32.LoveTogether_OnlineRewardRecord, rewardIndex)
		#盛宴摩天轮普通抽奖次数
		if rewardCfg.rewardLotteryTimes:
			role.IncDI8(EnumDayInt8.FeastWheelNomalTimes, rewardCfg.rewardLotteryTimes)
			rewardPrompt += GlobalPrompt.LoveTogether_Tips_FWTimes % rewardCfg.rewardLotteryTimes
		#获得物品
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			rewardPrompt += GlobalPrompt.LoveTogether_Tips_Item % (coding, cnt)
		#金币
		if rewardCfg.rewardMoney:
			role.IncMoney(rewardCfg.rewardMoney)
			rewardPrompt += GlobalPrompt.LoveTogether_Tips_Money % rewardCfg.rewardMoney
		#魔晶
		if rewardCfg.rewardBindRMB:
			role.IncBindRMB(rewardCfg.rewardBindRMB)
			rewardPrompt += GlobalPrompt.LoveTogether_Tips_BindRMB % rewardCfg.rewardMoney
		
	role.Msg(2, 0, rewardPrompt)

#### 事件 start ####
def UpdateOnlineMinutes(role, calargv, regparam):
	'''
	每分钟更新在线分钟数
	'''
	if not IS_START:
		return
	
	if role.IsKick():
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel: 
		return
	
	#增加在线一分钟
	role.IncI16(EnumInt16.LoveTogetherOnLineMinutes, 1)
	#接着注册到下一分钟
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnRoleLogin(role, param):
	'''
	登陆注册tick
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnRoleLevelUp(role, param):
	'''
	玩家升级 检测是否达到等级 并注册TICK
	'''
	if not IS_START:
		return
	
	#此次升级不是 解锁等级限制
	if role.GetLevel() != EnumGameConfig.DoubleTwelve_NeedLevel:
		return 
	
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnRoleDayClear(role, param):
	'''
	每日重置
	'''
	#重置在线分钟数
	role.SetI16(EnumInt16.LoveTogetherOnLineMinutes, 0)
	#重置领取记录
	role.SetI32(EnumInt32.LoveTogether_OnlineRewardRecord, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartLoveTogether)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndLoveTogether)
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LoveTogether_OnGetOnlineReward", "爱在一起在线奖励领取请求"), OnGetOnlineReward)
		