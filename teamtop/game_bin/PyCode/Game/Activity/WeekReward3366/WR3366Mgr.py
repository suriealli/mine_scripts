#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WeekReward3366.WR3366Mgr")
#===============================================================================
# 3366 一周豪礼
#===============================================================================
import time
import datetime
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity.WeekReward3366 import WR3366Config
from Game.Role.Data import EnumTempInt64, EnumDayInt1, EnumInt8

WR3366_STATE_CLOSE = 0
WR3366_STATE_OPEN = 1

WR3366_DEFAULT_ACTIVEID = 1		#3366一周豪礼活动ID

if "_HasLoad" not in dir():
	WR3366_ONLINE_ACTIVE_DICT = {}	#当前开启的活动信息{activeID:endTime}
	
	WeekReward3366_S_Active_State = AutoMessage.AllotMessage("WeekReward3366_S_Active_State", "3366一周豪礼活动状态")
	
	Tra_WR3366_TodayReward = AutoLog.AutoTransaction("Tra_WR3366_TodayReward", "3366一周豪礼领取今日礼包")

def Initialize():	
	'''
	初始化活动tick
	'''
	nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
	
	for activeID,config in WR3366Config.WEEK_REWARD_3366_CCONFIG_DICT.iteritems():
		beginTime = int(time.mktime(datetime.datetime(*config.beginDate).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*config.endDate).timetuple()))
		
		if config.beginDate <= nowDate < config.endDate:
			#开启 并注册结束tick
			WR3366_Start(None, (activeID, endTime))
			cComplexServer.RegTick(endTime - nowTime, WR3366_End, (activeID, endTime))
		elif nowDate < config.beginDate:
			#注册开启和结束的tick
			cComplexServer.RegTick(beginTime - nowTime, WR3366_Start, (activeID, endTime))
			cComplexServer.RegTick(endTime - nowTime, WR3366_End, (activeID, endTime))
			
def WR3366_Start(callargv, regparam):
	'''
	开启3366一周豪礼活动
	@param callargv:
	@param  regparam:(activeID, endTime)
	'''	
	activeID, endTime = regparam
	global WR3366_ONLINE_ACTIVE_DICT	
	if activeID in WR3366_ONLINE_ACTIVE_DICT:
		print "GE_EXC,repeat open WeekReward3366(%s)" % activeID
		return
		
	#设置开启 并广播通知
	WR3366_ONLINE_ACTIVE_DICT[activeID] = endTime 
	cNetMessage.PackPyMsg(WeekReward3366_S_Active_State, (WR3366_STATE_OPEN, endTime))
	cRoleMgr.BroadMsg()

def WR3366_End(callargv, regparam):
	'''
	结束3366一周豪礼活动
	'''
	activeID, _ = regparam
	global WR3366_ONLINE_ACTIVE_DICT	
	if activeID not in WR3366_ONLINE_ACTIVE_DICT:
		print "GE_EXC,no need to close WeekReward3366 for it is not open!"
		return
	
	#设置关闭 并广播通知
	del WR3366_ONLINE_ACTIVE_DICT[activeID]
	cNetMessage.PackPyMsg(WeekReward3366_S_Active_State, (WR3366_STATE_CLOSE,None))
	cRoleMgr.BroadMsg()
#============================================================================

def OnGetTodayReward(role, msg):
	'''
	领取3366一周豪礼的今日奖励
	@param role:
	@param msg:  
	'''
	# 活动未开启
	if not WR3366_ONLINE_ACTIVE_DICT.get(WR3366_DEFAULT_ACTIVEID, None):
		print "GE_EXC,OnGetTodayReward::active not open"
		return
	
	# 非3366平台玩家
	if role.GetTI64(EnumTempInt64.Is3366) == 0:
		print "GE_EXC,OnGetTodayReward::can not get reward except 3366 platform"
		return
	
	# 今日已领取奖励
	if role.GetDI1(EnumDayInt1.WR3366_RewardFlag):
		print "GE_EXC,OnGetTodayReward::have gotten reward today"
		return
	
	# 获取当前可领取奖励的cfg
	rewardCfg = WR3366Config.GetNextReward(role)
	if not rewardCfg:
		print "GE_EXC,OnGetTodayReward::all reward has been gotten"
		return
	
	# process
	promptMsg = ""
	with Tra_WR3366_TodayReward:
		# 今日领取标志
		role.SetDI1(EnumDayInt1.WR3366_RewardFlag, 1)
		# 领取记录
		role.SetI8(EnumInt8.WR3366_RewardRecord, role.GetI8(EnumInt8.WR3366_RewardRecord) + rewardCfg.rewardID)
		#普通物品奖励
		for itemCoding, cnt in rewardCfg.items:
			role.AddItem(itemCoding, cnt)
			promptMsg += GlobalPrompt.WR3366_Tips_Reward_Item % (itemCoding, cnt)
		#金币奖励
		if rewardCfg.money > 0:
			role.IncMoney(rewardCfg.money)
			promptMsg += GlobalPrompt.WR3366_Tips_Reward_Money % rewardCfg.money
		#魔晶奖励
		if rewardCfg.bindRMB > 0:
			role.IncBindRMB(rewardCfg.bindRMB)
			promptMsg += GlobalPrompt.WR3366_Tips_Reward_BindRMB % rewardCfg.bindRMB
		
		if promptMsg:
			role.Msg(2, 0, GlobalPrompt.WR3366_Tips_Reward_Head + promptMsg)	

#============================================================================
def OnSyncRoleOtherData(role, param):
	'''
	同步活动开启状态
	@param role:
	@param param: 
	'''
	if len(WR3366_ONLINE_ACTIVE_DICT) > 0:
		role.SendObj(WeekReward3366_S_Active_State, (WR3366_STATE_OPEN, WR3366_ONLINE_ACTIVE_DICT.get(WR3366_DEFAULT_ACTIVEID)))
	else:
		pass
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Initialize()
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WR3366_OnGetTodayReward", "3366一周豪礼之领取今日奖励"), OnGetTodayReward)
