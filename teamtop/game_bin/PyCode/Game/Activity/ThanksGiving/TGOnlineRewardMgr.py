#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ThanksGiving.TGOnlineRewardMgr")
#===============================================================================
# 在线赢大礼Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.ThanksGiving import ThanksGivingConfig
from Game.Role.Data import EnumInt16, EnumDayInt8, EnumTempInt64

ONE_MINUTE_SECONDS = 60

if "_HasLoad" not in dir():
	IS_START = False	#在线赢大礼活动开关标志
	
	Tra_TGOnlineReward_Award = AutoLog.AutoTransaction("Tra_TGOnlineReward_Award", "在线赢大礼领在线奖励")

def OnStartTGOnline(*param):
	'''
	开启在线赢大礼
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_TGOnlineReward:
		return
	
	# 已开启 
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open TGOnline"
		return
		
	IS_START = True	
	
	#给所有在线满足条件的玩家注册TICK
	for tmpRole in cRoleMgr.GetAllRole():
		if tmpRole.GetLevel() < EnumGameConfig.TG_OnlineReward_NeedLevel:
			continue
		tmpRole.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnEndTGOnline(*param):
	'''
	关闭在线赢大礼
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_TGOnlineReward:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC,end TGOnline while not open "
		return
		
	IS_START = False	

def OnGetOnlineReward(role, msg):
	'''
	领取在线奖励 
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TG_OnlineReward_NeedLevel:
		return
	
	rewardIndex = msg
	rewardCfg = ThanksGivingConfig.TG_OLINEREWARD_DICT.get(rewardIndex)
	if not rewardCfg:
		print "GE_EXC,error rewardIndex(%s) can not get rewardCfg" % rewardIndex
		return
	
	todayOnlineMins = role.GetI16(EnumInt16.TGOnlineRewardOnlineMinute)
	if todayOnlineMins < rewardCfg.needMinutes:
		return
	
	rewardRecord = role.GetDI8(EnumDayInt8.TGOnlineRewardRecord)
	if rewardIndex & rewardRecord:
		return
	
	rewardPrompt = GlobalPrompt.TG_OnlineReward_Tips_Head
	with Tra_TGOnlineReward_Award:
		#更新领取记录
		role.IncDI8(EnumDayInt8.TGOnlineRewardRecord, rewardIndex)
		#物品
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			rewardPrompt += GlobalPrompt.TG_OnlineReward_Tips_Item % (coding, cnt)
		#金币
		rewardMoney = rewardCfg.rewardMoney
		if rewardMoney:
			role.IncMoney(rewardMoney)			
			rewardPrompt += GlobalPrompt.TG_OnlineReward_Tips_Money % rewardMoney
		#魔晶
		rewardBindRMB = rewardCfg.rewardBindRMB
		if rewardBindRMB:
			role.IncBindRMB(rewardBindRMB)
			rewardPrompt += GlobalPrompt.TG_OnlineReward_Tips_BindRMB % rewardBindRMB
			
		#3366和大厅平台额外获得抽奖次数
		rewardTimes = rewardCfg.rewardTimes
		if rewardTimes:
			if role.GetTI64(EnumTempInt64.Is3366) or role.GetTI64(EnumTempInt64.IsQQGame):
				role.IncDI8(EnumDayInt8.TGRechargeRewardOnlineTimes, rewardTimes)
				rewardPrompt += GlobalPrompt.TG_OnlineReward_Tips_ExtraTimes % rewardTimes
	
	role.Msg(2, 0, rewardPrompt)

def UpdateOnlineMinutes(role, calargv, regparam):
	'''
	每分钟更新在线分钟数
	'''
	if not IS_START:
		return
	
	if role.IsKick():
		return
	
	if role.GetLevel() < EnumGameConfig.TG_OnlineReward_NeedLevel:
		return
	
	#增加在线一分钟
	role.IncI16(EnumInt16.TGOnlineRewardOnlineMinute, 1)
	#接着注册到下一分钟
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnRoleLogin(role, param):
	'''
	登陆注册tick
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TG_OnlineReward_NeedLevel:
		return
	
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnRoleLevelUp(role, param):
	'''
	玩家升级 检测是否达到等级 并注册TICK
	'''
	if not IS_START:
		return
	
	#此次升级不是 解锁等级限制
	if role.GetLevel() != EnumGameConfig.TG_OnlineReward_NeedLevel:
		return 
	
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)


def OnRoleDayClear(role, param):
	'''
	重置今日在线分钟数
	'''
	role.SetI16(EnumInt16.TGOnlineRewardOnlineMinute, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndTGOnline)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartTGOnline)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TG_OnlineReward_OnGetOnlineReward", "请求获取在线奖励"), OnGetOnlineReward)