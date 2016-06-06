#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZhongQiu.HuoYueDaLiMgr")
#===============================================================================
# 活跃大礼 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.ZhongQiu import HuoYueDaLiConifg
from Game.Role.Data import EnumInt16, EnumInt8, EnumTempInt64

ONE_MINUTE_SECONDS = 60

if "_HasLoad" not in dir():
	
	IS_START = False
	
	Tra_HuoYueDaLi_OnLineInc = AutoLog.AutoTransaction("Tra_HuoYueDaLi_OnLineInc", "活跃大礼_在线增加步数")
	Tra_HuoYueDaLi_DailyDoInc = AutoLog.AutoTransaction("Tra_HuoYueDaLi_DailyDoInc", "活跃大礼_每日必做增加步数")
	
	Tra_HuoYueDaLi_Move = AutoLog.AutoTransaction("Tra_HuoYueDaLi_Move", "活跃大礼_前进")
	Tra_HuoYueDaLi_OneKeyMove = AutoLog.AutoTransaction("Tra_HuoYueDaLi_OneKeyMove", "活跃大礼_一键前进")
	

#===============================================================================
# 活动控制
#===============================================================================
def OnStartHuoYueDaLi(*param):
	'''
	活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_HuoYueDaLi != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open HuoYueDaLi"
		return
		
	IS_START = True
	

def OnEndHuoYueDaLi(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_HuoYueDaLi != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end HuoYueDaLi while not start"
		return
		
	IS_START = False


#===============================================================================
# 客户端请求
#===============================================================================
def OnMove(role, msg = None):
	'''
	活跃大礼_请求前进
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.HuoYueDaLi_NeedLevel:
		return
	
	nowIndex = role.GetI8(EnumInt8.HuoYueDaLi_NowIndex)
	effectStep = role.GetI8(EnumInt8.HuoYueDaLi_EffectStep)
	if nowIndex >= effectStep:
		return
	
	if nowIndex >= EnumGameConfig.HuoYueDaLi_MaxStep:
		return
	
	isPrompt = False
	prompt = GlobalPrompt.Reward_Tips
	rewardDict = HuoYueDaLiConifg.GetRewardByIndexInteval(nowIndex + 1, nowIndex+1)
	with Tra_HuoYueDaLi_Move:
		#前进一步
		role.IncI8(EnumInt8.HuoYueDaLi_NowIndex, 1)
		#获得道具
		for coding, cnt in rewardDict.iteritems():
			isPrompt = True
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#前进提示
	role.Msg(2, 0, GlobalPrompt.HuoYueDaLi_Tips_Move % 1)
	
	#获得提示
	if isPrompt:
		role.Msg(2, 0, prompt) 
	

def OnOnKeyMove(role, msg = None):
	'''
	活跃大礼_请求一键前进
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.HuoYueDaLi_NeedLevel:
		return
	
	nowIndex = role.GetI8(EnumInt8.HuoYueDaLi_NowIndex)
	effectStep = role.GetI8(EnumInt8.HuoYueDaLi_EffectStep)
	if nowIndex >= effectStep:
		return
	
	if nowIndex >= EnumGameConfig.HuoYueDaLi_MaxStep:
		return
	
	targetStep = min((effectStep - nowIndex), (EnumGameConfig.HuoYueDaLi_MaxStep - nowIndex))
	if targetStep < 1:
		return
	
	isPrompt = False
	prompt = GlobalPrompt.Reward_Tips
	rewardDict = HuoYueDaLiConifg.GetRewardByIndexInteval(nowIndex + 1, nowIndex + targetStep)
	with Tra_HuoYueDaLi_OneKeyMove:
		#前进一步
		role.IncI8(EnumInt8.HuoYueDaLi_NowIndex, targetStep)
		#获得道具
		for coding, cnt in rewardDict.iteritems():
			isPrompt = True
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#前进提示
	role.Msg(2, 0, GlobalPrompt.HuoYueDaLi_Tips_Move % targetStep)
	#获得提示
	if isPrompt:
		role.Msg(2, 0, prompt)


#===============================================================================
# 辅助
#===============================================================================
def UpdateOnlineMinutes(role, calargv, regparam):
	'''
	每分钟更新在线分钟数
	'''
	if not IS_START:
		return
	
	if role.IsKick() or role.IsLost():
		return
	
	if role.GetLevel() < EnumGameConfig.HuoYueDaLi_NeedLevel: 
		return
	
	#增加在线一分钟
	role.IncI16(EnumInt16.HuoYueDaLiOnLineMins, 1)
	if role.GetI16(EnumInt16.HuoYueDaLiOnLineMins) in EnumGameConfig.HuoYueDaLi_RewardMins_List:
		with Tra_HuoYueDaLi_OnLineInc:
			role.IncI8(EnumInt8.HuoYueDaLi_EffectStep, 1)
	#接着注册到下一分钟
	role.SetTI64(EnumTempInt64.HuoYueDaLiTickId, role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes))


#===============================================================================
# 事件
#===============================================================================
def OnSyncOtherData(role, param):
	'''
	登陆注册tick
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.HuoYueDaLi_NeedLevel:
		return
	
	oldTickId = role.GetTI64(EnumTempInt64.HuoYueDaLiTickId)
	if oldTickId:
		role.UnregTick(oldTickId)
	
	role.SetTI64(EnumTempInt64.HuoYueDaLiTickId, role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes))
	

def OnRoleLevelUp(role, param):
	'''
	玩家升级 检测是否达到等级 并注册TICK
	'''
	if not IS_START:
		return
	
	#此次升级不是 解锁等级限制
	if role.GetLevel() != EnumGameConfig.HuoYueDaLi_NeedLevel:
		return 
	
	role.SetTI64(EnumTempInt64.HuoYueDaLiTickId, role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes))


def OnRoleDayClear(role, param):
	'''
	每日重置
	'''
	#重置在线分钟数
	role.SetI16(EnumInt16.HuoYueDaLiOnLineMins, 0)
	#重启tick
	oldTickId = role.GetTI64(EnumTempInt64.HuoYueDaLiTickId)
	if oldTickId:
		role.UnregTick(oldTickId)
		role.SetTI64(EnumTempInt64.HuoYueDaLiTickId, 0)
	
	if not IS_START or role.GetLevel() < EnumGameConfig.HuoYueDaLi_NeedLevel:
		return
	
	role.SetTI64(EnumTempInt64.HuoYueDaLiTickId, role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes))


def OnRoleOffLine(role, param = None):
	'''
	角色离线：客户端掉线+服务端掉线 注销tick
	'''
	oldTickId = role.GetTI64(EnumTempInt64.HuoYueDaLiTickId)
	if oldTickId:
		role.UnregTick(oldTickId)
		role.SetTI64(EnumTempInt64.HuoYueDaLiTickId, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartHuoYueDaLi)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndHuoYueDaLi)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		Event.RegEvent(Event.Eve_ClientLost, OnRoleOffLine)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleOffLine)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HuoYueDaLi_OnMove", "活跃大礼_请求前进"), OnMove)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HuoYueDaLi_OnOnKeyMove", "活跃大礼_请求一键前进"), OnOnKeyMove)