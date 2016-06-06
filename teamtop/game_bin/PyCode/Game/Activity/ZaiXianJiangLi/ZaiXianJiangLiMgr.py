#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZaiXianJiangLi.ZaiXianJiangLiMgr")
#===============================================================================
# 新在线奖励  Mgr
#===============================================================================
import cRoleMgr
import cNetMessage
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event, Call
from Game.Activity.ZaiXianJiangLi import ZaiXianJiangLiConfig
from Game.Role.Data import EnumInt32, EnumInt8, EnumTempInt64, EnumDayInt8

OneMinute_Sec = 60 

if "_HasLoad" not in dir():
	IS_START = False
	ENDTIME = 0
	VERSION = 0
	
	ZXJL_Precious_List = []		#珍稀奖励记录 格式 [(rolename, coding, cnt),]
	
	ZaiXianJiangLi_ActiveStatus_S = AutoMessage.AllotMessage("ZaiXianJiangLi_ActiveStatus_S", "新在线奖励_同步活动状态")
	ZaiXianJiangLi_LotteryResult_S = AutoMessage.AllotMessage("ZaiXianJiangLi_LotteryResult_S", "新在线奖励_同步抽奖结果")
	ZaiXianJiangLi_PreciousRecord_S = AutoMessage.AllotMessage("ZaiXianJiangLi_PreciousRecord_S", "新在线奖励_同步珍稀中奖记录")
	
	Tra_ZaiXianJiangLi_UpdateVersion = AutoLog.AutoTransaction("Tra_ZaiXianJiangLi_UpdateVersion","新在线奖励_升级活动版本号")
	Tra_ZaiXianJiangLi_Lottery = AutoLog.AutoTransaction("Tra_ZaiXianJiangLi_Lottery", "新在线奖励_抽奖")
	
#### 活动控制 start
def OnStartZaiXianJiangLi(*param):
	'''
	连充返利_开启
	'''
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open ZaiXianJiangLi"
		return 
	
	global ENDTIME, VERSION
	_,activeParam = param
	VERSION, ENDTIME = activeParam
	IS_START = True
	
	#更新所有在线玩家 活动相关数据
	for tmpRole in cRoleMgr.GetAllRole():
		InitAndUpdateVersion(tmpRole)
		TryStartTick(tmpRole)
	
	cNetMessage.PackPyMsg(ZaiXianJiangLi_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

def OnEndZaiXianJiangLi(*param):
	'''
	连充返利_结束
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,end ZaiXianJiangLi while not start"
	IS_START = False
	
	cNetMessage.PackPyMsg(ZaiXianJiangLi_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

def OnOpenPanel(role, msg = None):
	'''
	新在线奖励_请求打开面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ZaiXianJiangLi_NeedLevel:
		return
	
	role.SendObj(ZaiXianJiangLi_PreciousRecord_S, ZXJL_Precious_List)

def OnLottery(role, msg = None):
	'''
	新在线奖励_请求抽奖
	'''
#	if not IS_START:
#		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ZaiXianJiangLi_NeedLevel:
		return
	
	lotteryTimes = role.GetDI8(EnumDayInt8.ZaiXianJiangLiLotteryTimes)
	if lotteryTimes >= EnumGameConfig.ZaiXianJiangLi_MaxLotteryTimes:
		return
	
	onlineMins = role.GetI8(EnumInt8.ZaiXianJiangLiOnLineMins) 
	if onlineMins < EnumGameConfig.ZaiXianJiangLi_MaxMins:
		return
	
	randomObj = ZaiXianJiangLiConfig.GetRandomObjByLevel(roleLevel)
	if not randomObj:
		print "GE_EXC, ZaiXianJiangLi config error can not get randomObj by rolelevel(%s) role(%s)" % (roleLevel, role.GetRoleID())
		return
	
	rewardInfo = randomObj.RandomOne()
	if not rewardInfo:
		print "GE_EXC, ZaiXianJiangLi config error can not get RandomOne by rolelevel(%s) role(%s)" % (roleLevel, role.GetRoleID())
		return
	
	roleName = role.GetRoleName()
	rewardId, rewardIndex, coding, cnt, isPrecious = rewardInfo
	with Tra_ZaiXianJiangLi_Lottery:
		#增加抽奖次数
		lotteryTimes += 1
		role.SetDI8(EnumDayInt8.ZaiXianJiangLiLotteryTimes, lotteryTimes)
		#重置在线分钟数
		role.SetI8(EnumInt8.ZaiXianJiangLiOnLineMins, 0)
		#珍稀奖励记录
		if isPrecious:
			global ZXJL_Precious_List
			ZXJL_Precious_List.insert(0, (roleName, coding, cnt))
			if len(ZXJL_Precious_List) > EnumGameConfig.ZaiXianJiangLi_MaxRecordNums:
				ZXJL_Precious_List.pop()
	
	#同步抽奖结果 等待回调
	role.SendObjAndBack(ZaiXianJiangLi_LotteryResult_S, (rewardId, rewardIndex), 8, OnLottryCallBack, (role.GetRoleID(), roleName, coding, cnt, isPrecious))
	#重新尝试启动计时器
	TryStartTick(role)
	
def OnLottryCallBack(role, callargv, regparam):
	'''
	抽奖回调
	@param param: roleId, roleName, coding, cnt
	'''
	roleId, roleName, coding, cnt, isPrecious = regparam
	Call.LocalDBCall(roleId, LotteryAward, (coding, cnt))
	
	if isPrecious:
		#广播
		cRoleMgr.Msg(1, 0, GlobalPrompt.ZaiXianJiangLi_Msg_Precious % (roleName, coding, cnt))
		#角色同步珍稀记录给自己
		if not (role.IsKick() or role.IsLost()):
			role.SendObj(ZaiXianJiangLi_PreciousRecord_S, ZXJL_Precious_List)

#离线命令执行 修改请三思
def LotteryAward(role, param):
	'''
	抽奖获得
	@param param: roleId, roleName, rewardId
	'''
	coding, cnt  = param
	with Tra_ZaiXianJiangLi_Lottery:
		role.AddItem(coding, cnt)
		role.Msg(2, 0, GlobalPrompt.ZaiXianJiangLi_Tips_LotterySuccess % (coding, cnt))

#### 辅助 start
def TryStartTick(role):
	'''
	尝试启动在线计时器
	'''
	#活动非开启
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ZaiXianJiangLi_NeedLevel:
		return
	
	#今日剩余可领奖机会不足
	if role.GetDI8(EnumDayInt8.ZaiXianJiangLiLotteryTimes) >= EnumGameConfig.ZaiXianJiangLi_MaxLotteryTimes:
		return
	
	#如果有tick 先注销掉 (1.避免注册多个计时器  2.避免失效tickId)
	tickId = role.GetTI64(EnumTempInt64.ZaiXianJiangLiTickId)
	if tickId:
		cComplexServer.UnregTick(tickId)
	
	#注册tick 保存
	tickId = cComplexServer.RegTick(OneMinute_Sec, OnTickTack, role.GetRoleID())
	role.SetTI64(EnumTempInt64.ZaiXianJiangLiTickId, tickId)
	
def OnTickTack(callargv, regparam):
	'''
	计时器
	'''	
	role = cRoleMgr.FindRoleByRoleID(regparam)
	if role is None or role.IsKick() or role.IsLost():
		return
	
	#活动结束了 注销Tick
	if not IS_START:
		role.SetTI64(EnumTempInt64.ZaiXianJiangLiTickId, 0)
	
	
	#在线时间增加一分钟
	onlineMins = role.GetI8(EnumInt8.ZaiXianJiangLiOnLineMins)
	onlineMins += 1
	role.SetI8(EnumInt8.ZaiXianJiangLiOnLineMins, onlineMins)
	
	#未达到可抽奖在线时间 继续 tick
	newTickId = 0
	if onlineMins < EnumGameConfig.ZaiXianJiangLi_MaxMins:
		newTickId = cComplexServer.RegTick(OneMinute_Sec, OnTickTack, role.GetRoleID())
	else:
		pass
	
	#保存 新的tickId
	role.SetTI64(EnumTempInt64.ZaiXianJiangLiTickId, newTickId)
	
#### 事件 start
def InitAndUpdateVersion(role, param = None):
	'''
	根据活动版本号 和 记录的版本好 处理角色Obj数据
	'''
	if Environment.IsCross:
		return
	
	#活动没开返回   活动开启触发 和 开启后触发 保证升级版本号数据逻辑
	if not IS_START:
		return
	
	#2.根据版本号处理活动数据
	roleVersion = role.GetI32(EnumInt32.ZaiXianJiangLiVersion)
	if VERSION == roleVersion:
		return
	
	if VERSION < roleVersion:
		print "GE_EXC, ZaiXianJiangLiMgr::UpdateVersion VERSION(%s) < roleVersion (%s)" % (VERSION, roleVersion)
		return 
	
	#重置相关数据	
	with Tra_ZaiXianJiangLi_UpdateVersion:
		#升级版本号
		role.SetI32(EnumInt32.ZaiXianJiangLiVersion, VERSION)
		#已领奖次数
		role.SetDI8(EnumDayInt8.ZaiXianJiangLiLotteryTimes, 0)
		#当前有效在线时间
		role.SetI8(EnumInt8.ZaiXianJiangLiOnLineMins, 0)
		#清除tickId
		role.SetTI64(EnumTempInt64.ZaiXianJiangLiTickId, 0)
		
def OnSyncRoleOtherData(role,param):
	'''
	兼容活动放出去当日 维护之前玩家充值触发完成返利项
	'''
	#尝试启动在线计时器
	TryStartTick(role)
	
	#同步活动状态
	role.SendObj(ZaiXianJiangLi_ActiveStatus_S, (IS_START, ENDTIME))

def OnDailyClear(role, param):
	'''
	每日清理  当日充值返利项领奖标志
	'''
	#尝试启动在线计时器
	TryStartTick(role)

def OnClientLost(role, param = None):
	'''
	客户端掉线 取消在线计时器
	'''
	tickId = role.GetTI64(EnumTempInt64.ZaiXianJiangLiTickId)
	if tickId:
		cComplexServer.UnregTick(tickId)
	
	#清理tickId
	role.SetTI64(EnumTempInt64.ZaiXianJiangLiTickId, 0)

def AfterLevelUp(role, param = None):
	'''
	角色升级尝试启动在线计时器
	'''
	#刚刚解锁玩法
	if role.GetLevel() == EnumGameConfig.ZaiXianJiangLi_NeedLevel:
		TryStartTick(role) 
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnDailyClear)
		Event.RegEvent(Event.Eve_InitRolePyObj, InitAndUpdateVersion)
		
		Event.RegEvent(Event.Eve_ClientLost, OnClientLost)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZaiXianJiangLi_OnOpenPanel", "新在线奖励_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZaiXianJiangLi_OnLottery", "新在线奖励_请求抽奖"), OnLottery)