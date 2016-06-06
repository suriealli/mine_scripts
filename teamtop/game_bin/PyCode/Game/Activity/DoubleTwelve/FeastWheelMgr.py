#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.FeastWheelMgr")
#===============================================================================
# 盛宴摩天轮Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event, Call
from Game.Activity import CircularDefine
from Game.Activity.DoubleTwelve import FeastWheelConfig
from Game.Role.Data import EnumDayInt8, EnumInt32, EnumInt16

FW_LOTTERYTYPE_RMB = 1		#RMB抽奖次数
FW_LOTTERYTYPE_NOMAL = 2	#普通抽奖次数

if "_HasLoad" not in dir():
	IS_START = False
	FeastWheel_OpenPanelRole_Set = set()	#当前打开操作面板的RoleId集合
	FeastWheel_PreciousRecord_List = []		#盛宴摩天轮珍贵奖励记录 [(roleName,coding,cnt),] 
	
	Tra_FeastWheel_Lottery = AutoLog.AutoTransaction("Tra_FeastWheel_Lottery", "盛宴摩天轮抽奖奖励")
	Tra_FeastWheel_RechargeReward = AutoLog.AutoTransaction("Tra_FeastWheel_RechargeReward", "盛宴摩天轮重置奖励领取")
	
	FeastWheel_PreciousRecord_S = AutoMessage.AllotMessage("FeastWheel_PreciousRecord_S", "盛宴摩天轮珍贵奖励记录")
	FeastWheel_LotteryResult_SB = AutoMessage.AllotMessage("FeastWheel_LotteryResult_SB", "盛宴摩天轮抽奖结果")
	
#### 活动控制  start ####
def OnStartFeastWheel(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_DTFeastWheel != circularType:
		return
	
	global IS_START
	global FeastWheel_OpenPanelRole_Set
	global FeastWheel_PreciousRecord_List
	if IS_START:
		print "GE_EXC,repeat open FeastWheel"
		return
		
	IS_START = True
	FeastWheel_OpenPanelRole_Set = set()
	FeastWheel_PreciousRecord_List = []

def OnEndFeastWheel(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_DTFeastWheel != circularType:
		return
	
	# 未开启 
	global IS_START
	global FeastWheel_OpenPanelRole_Set
	global FeastWheel_PreciousRecord_List
	if not IS_START:
		print "GE_EXC, end FeastWheel while not start"
		return
		
	IS_START = False
	FeastWheel_OpenPanelRole_Set = set()
	FeastWheel_PreciousRecord_List = []

#### 请求 start ####
def OnOpenPanel(role, msg = None):
	'''
	打开操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	global FeastWheel_OpenPanelRole_Set
	FeastWheel_OpenPanelRole_Set.add(role.GetRoleID())
	
	role.SendObj(FeastWheel_PreciousRecord_S, FeastWheel_PreciousRecord_List)

def OnClosePanel(role, msg = None):
	'''
	关闭操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	global FeastWheel_OpenPanelRole_Set
	FeastWheel_OpenPanelRole_Set.discard(role.GetRoleID())

def OnLottery(role, msg = None):
	'''
	客户端请求抽奖
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	#有效抽奖次数不足
	effectRMBTimes = role.GetI16(EnumInt16.FeastWheelRMBTimes)
	effectNomalTimes = role.GetDI8(EnumDayInt8.FeastWheelNomalTimes)
	if effectNomalTimes < 1 and effectRMBTimes < 1:
		return
	
	#确定抽奖类型(优先使用RMB次数)
	lotteryType = 0
	randomObj = None
	if effectRMBTimes > 0:
		lotteryType = FW_LOTTERYTYPE_RMB
		randomObj = FeastWheelConfig.FeastWheel_LotteryReward_RandomObj_RMB
	elif effectNomalTimes > 0:
		lotteryType = FW_LOTTERYTYPE_NOMAL
		randomObj = FeastWheelConfig.FeastWheel_LotteryReward_RandomObj_Nomal
	else:
		pass
	
	if not lotteryType or not randomObj:
		return
	
	#(rewardId, isPrecious, item)
	rewardInfo = randomObj.RandomOne()
	if not rewardInfo:
		print "GE_EXC,can not random rewardInfo by randomObj.randomList(%s)" % randomObj.randomList
		return
	
	#先扣除抽奖次数
	with Tra_FeastWheel_Lottery:
		if lotteryType == FW_LOTTERYTYPE_RMB:
			role.DecI16(EnumInt16.FeastWheelRMBTimes, 1)
		elif lotteryType == FW_LOTTERYTYPE_NOMAL:
			role.DecDI8(EnumDayInt8.FeastWheelNomalTimes, 1)
		else:
			pass
	
	role.SendObjAndBack(FeastWheel_LotteryResult_SB, rewardInfo, 8, LotteryCallBack, (rewardInfo, role.GetRoleID(), role.GetRoleName()))

def OnGetRechargeReward(role, msg):
	'''
	客户端请求领取充值奖励
	@param msg: rewardIndex
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	#参数检测
	rewardIndex = msg
	rewardCfg = FeastWheelConfig.FeastWheel_RechargeReward_Dict.get(rewardIndex)
	if not rewardCfg:
		return
	
	#已领取
	rewardRecord = role.GetI32(EnumInt32.FeastWheel_RechargeRewardRecord)
	if rewardIndex & rewardRecord:
		return
	
	#充值神石不达标
	dayBuyUnbindRMB = role.GetDayBuyUnbindRMB_Q()
	if dayBuyUnbindRMB < rewardCfg.needRechargeRMB:
		return
	
	with Tra_FeastWheel_RechargeReward:
		#更新领取记录
		role.IncI32(EnumInt32.FeastWheel_RechargeRewardRecord, rewardIndex)
		#获得抽奖次数
		role.IncI16(EnumInt16.FeastWheelRMBTimes, rewardCfg.rewardTimes)

#### 回调 start ####
def LotteryCallBack(role, callargv, regparam):
	'''
	抽奖回调
	'''
	rewardInfo, roleId, roleName = regparam
	_, isPrecious, item = rewardInfo
	coding, cnt = item
	
	#珍贵奖励记录处理
	if isPrecious:
		global FeastWheel_PreciousRecord_List
		preciousInfo = (roleName, coding, cnt)
		if len(FeastWheel_PreciousRecord_List) >= EnumGameConfig.FeastWheel_PreciousRecordMaxSize:
			FeastWheel_PreciousRecord_List.pop(0)
		FeastWheel_PreciousRecord_List.append(preciousInfo)
		
		#同步最新珍贵奖励记录给缓存的role
		invalidRoleSet = set()
		global FeastWheel_OpenPanelRole_Set
		for tmpRoleId in FeastWheel_OpenPanelRole_Set:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
			if not tmpRole:
				invalidRoleSet.add(tmpRoleId)
				continue
			tmpRole.SendObj(FeastWheel_PreciousRecord_S, FeastWheel_PreciousRecord_List)
		
		#删除缓存的无效roleId
		if len(invalidRoleSet) > 0:
			FeastWheel_OpenPanelRole_Set.difference_update(invalidRoleSet)
		
	Call.LocalDBCall(roleId, RealAward, (coding, cnt))
	
def RealAward(role, param):
	'''
	抽奖实际获得处理
	'''
	coding, cnt = param
	with Tra_FeastWheel_Lottery:
		#物品获得
		role.AddItem(coding, cnt)
		#获得提示
		role.Msg(2, 0, GlobalPrompt.FeastWheel_Tips_Head + GlobalPrompt.FeastWheel_Tips_Item % (coding, cnt))

#### 事件 start ####
def OnRoleDayClear(role,param):
	'''
	每日清除
	'''
	#重置今日充值兑换次数记录
	role.SetI32(EnumInt32.FeastWheel_RechargeRewardRecord, 0)
	#重置今日重置兑换的RMB抽奖次数
	role.SetI16(EnumInt16.FeastWheelRMBTimes, 0)



if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartFeastWheel)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndFeastWheel)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FeastWheel_OnOpenPanel", "打开盛宴摩天轮面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FeastWheel_OnClosePanel", "关闭盛宴摩天轮面板"), OnClosePanel)		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FeastWheel_OnLottery", "盛宴摩天轮抽奖请求"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FeastWheel_OnGetRechargeReward", "盛宴摩天轮充值奖励请求"), OnGetRechargeReward)
		