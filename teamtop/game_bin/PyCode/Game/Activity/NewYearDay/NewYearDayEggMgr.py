#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NewYearDay.NewYearDayEggMgr")
#===============================================================================
# 2016元旦金蛋活动
#===============================================================================
import Environment
import cNetMessage
import cRoleMgr
import cDateTime
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumObj
from Game.Role.Data import EnumDayInt8
from Game.Activity.NewYearDay import NewYearDayEggConfig
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.PassionAct.PassionDefine import PassionNewYearEgg
if "_HasLoad" not in dir():
	IsStart = False
	ONE_MINUTE_SECONDS = 60
	#金蛋活动消息同步
	NewYearDayEggStart = AutoMessage.AllotMessage("NewYearDayEggStart", "元旦金蛋活动开启")
	NewYearDayEggOnLineState = AutoMessage.AllotMessage("NewYearDayEggOnLineState", "在线状态")
	NewYearDayEggRMBState = AutoMessage.AllotMessage("NewYearDayEggRMBState", "充值状态")
	NewYearDayEggState = AutoMessage.AllotMessage("NewYearDayEggState", "金蛋状态")
	#元旦金蛋活动的日志
	NewYearDayEggOnLineState_Log = AutoLog.AutoTransaction("NewYearDayEggOnLineState_Log", "元旦活动在线锤子记录")
	NewYearDayEggRMBState_Log = AutoLog.AutoTransaction("NewYearDayEggRMBState_Log", "元旦活动充值锤子日志")
	NewYearDayEggState_Log = AutoLog.AutoTransaction("NewYearDayEggState_Log", "金蛋获得纪录")
	


def OpenActive(callArgv, param):
	if CircularDefine.CA_NewYearDayEgg != param :
		return
	global IsStart
	if IsStart :
		print "GE_EXC, NewYearDayEgg has Started"
	IsStart = True
	#通知客户端活动开启
	cNetMessage.PackPyMsg(NewYearDayEggStart, 1)
	#给所有在线玩家注册个tick
	for tmpRole in cRoleMgr.GetAllRole():
		tmpRole.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes, None)

def CloseActive(callArgv, param):
	if CircularDefine.CA_NewYearDayEgg != param :
		return
	global IsStart
	if not IsStart :
		print "GE_EXC, NewYearDayEgg has Closed"
	IsStart = False
	cNetMessage.PackPyMsg(NewYearDayEggStart, 0)

#打开元旦金蛋面板
def OpenNewYearDayEgg(role, param = 1):
	global IsStart
	if not IsStart :
		return
	#低于最低等级
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	
	EggState = role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg]
	# 金蛋状态[]
	OwnerEgg = EggState[1]
	#在线锤子状态 
	OnLineState = EggState[2]
	#充值锤子状态 
	RMBState = EggState[3]
	#同步客户端
	role.SendObj(NewYearDayEggState, OwnerEgg)
	role.SendObj(NewYearDayEggOnLineState, (role.GetOnLineTimeToday(), OnLineState))
	role.SendObj(NewYearDayEggRMBState, RMBState)

def NewYearDayEggOnLineAward(role, Choice):
	global IsStart
	if not IsStart :
		return
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	OnLineState = role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg][2]
	if Choice not in NewYearDayEggConfig.OnLineAward :
		return
	
	#在线时间不满足
	if role.GetOnLineTimeToday() / 60 < NewYearDayEggConfig.OnLineAward[Choice].NeedTime :
		return
	#已经领取
	if OnLineState[Choice - 1] != 1:
		return
	#领取锤子
	with NewYearDayEggOnLineState_Log:
		OnLineState[Choice - 1] = 2
		role.IncDI8(EnumDayInt8.NewYearHammer, NewYearDayEggConfig.OnLineAward[Choice].HammersNumbers)
		tips = ""
		tips += GlobalPrompt.NewYearDayEggHummer % NewYearDayEggConfig.OnLineAward[Choice].HammersNumbers
		
	role.Msg(2, 0, tips)
	role.SendObj(NewYearDayEggOnLineState, (role.GetOnLineTimeToday(), OnLineState))


def NewYearDayEggRMBAward(role, Choice):
	global IsStart
	if not IsStart :
		return
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	OnLineState = role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg][3]
	if Choice not in NewYearDayEggConfig.RMBAward :
		return
	#充值不足
	if role.GetDayBuyUnbindRMB_Q() < NewYearDayEggConfig.RMBAward[Choice].NeedRMB:
		return
	#已经领取
	if OnLineState[Choice - 1] != 1:
		return
	with NewYearDayEggRMBState_Log:
		OnLineState[Choice - 1] = 2
		role.IncDI8(EnumDayInt8.NewYearHammer, NewYearDayEggConfig.RMBAward[Choice].Hammers)
		tips = ""
		tips += GlobalPrompt.NewYearDayEggHummer % NewYearDayEggConfig.OnLineAward[Choice].HammersNumbers
	role.Msg(2, 0, tips)
	role.SendObj(NewYearDayEggRMBState, OnLineState)

def NewYearDayEggAward(role, index):
	global IsStart
	if not IsStart :
		return
	#不够等级
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	#锤子数量不足
	if role.GetDI8(EnumDayInt8.NewYearHammer) <= 0:
		return
	boxs = role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg][1]
	#超出范围
	if index < 0 or index >= len(boxs) :
		return
	#已经领取
	if boxs[index] :
		return
	for indexs, cf in NewYearDayEggConfig.NYD_Egg_Random_Dict.iteritems():
		minlevel, maxlevel = indexs
		if minlevel <= role.GetLevel() <= maxlevel :
			break
	with NewYearDayEggState_Log:
		EggAwardIndex = cf.RandomOne()
		EggAward = NewYearDayEggConfig.NYD_Egg_Award.get(EggAwardIndex)
		if not EggAward :
			print "GE_EXC,No EggAwardIndex %s in NYD_Egg_Award" % EggAwardIndex
			return
		role.DecDI8(EnumDayInt8.NewYearHammer, 1)
		boxs[index] = 1
		tips = ""
		item, cnt = EggAward.RewardItems
		role.AddItem(item, cnt)
		tips += GlobalPrompt.NewYearDayEggAward % (item, cnt)
	role.Msg(2, 0, tips)
	role.SendObj(NewYearDayEggState, boxs)

def AfterNewDay(role, param):
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	EggState = {}
	EggState[1] = [0]*12			#金蛋状态
	EggState[2] = [0]*3				#在线领取锤子状态
	EggState[3] = [0]*3				#充值领取锤子状态
	role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg] = EggState
	if not IsStart:
		return
	OpenNewYearDayEgg(role)

#充值改变后触发
def AfterChangeRMB(role, param):
	global IsStart
	if not IsStart :
		return
	RMBState = role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg][3]
	
	for index, cf in NewYearDayEggConfig.RMBAward.iteritems():
		if role.GetDayBuyUnbindRMB_Q() >= cf.NeedRMB and not RMBState[index - 1]:
			RMBState[index - 1] = 1
	role.SendObj(NewYearDayEggRMBState, RMBState)

def SyncRoleOtherData(role, param):
	global IsStart
	if not IsStart :
		return
	OpenNewYearDayEgg(role)
	
def AfterLogin(role, param):
	'''
	玩家登录
	'''
	PassionActData = role.GetObj(EnumObj.PassionActData)
	if PassionNewYearEgg not in PassionActData:
		PassionActData[PassionNewYearEgg] = {}
	
	EggState = role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg]
	if 1 not in EggState:
		EggState[1] = [0]*12			#金蛋状态
	if 2 not in EggState:
		EggState[2] = [0]*3				#在线领取锤子状态
	if 3 not in EggState:
		EggState[3] = [0]*3				#充值领取锤子状态
	#登陆注册tick
	global IsStart
	if not IsStart :
		return
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes, None)
	
#每分钟检测时候满足
def UpdateOnlineMinutes(role, callargv, regparam):
	global IsStart
	if not IsStart :
		return
	if role.IsKick():
		return
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	OnlineMin = role.GetOnLineTimeToday() / 60
	OnlineState = role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg][2]
	for index, cf in NewYearDayEggConfig.OnLineAward.iteritems() :
		if OnlineMin >= cf.NeedTime and not OnlineState[index - 1] :
			OnlineState[index - 1] = 1
	OnLineMgr = NewYearDayEggConfig.OnLineAward.get(3)
	role.SendObj(NewYearDayEggOnLineState, (role.GetOnLineTimeToday(), OnlineState))
	if OnlineMin >= OnLineMgr.NeedTime :
		NowTime = cDateTime.Hour()*60*60 + cDateTime.Minute()*60 + cDateTime.Second()
		leftTime = 24*60*60 - NowTime
		role.RegTick(leftTime, UpdateOnlineMinutes, None)
		return
	#重新注册新的一分钟
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes, None)

def AfterLevelUp(role, param):
	'''
	玩家升级 检测是否达到等级 并注册TICK
	'''
	global IsStart
	if not IsStart:
		return 
	if role.GetLevel() != EnumGameConfig.NewYearDayMinLevel :
		return
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes, None)

def StateicPig(role, param):
	'''
	检测对象是否存在
	'''
	global IsStart
	if not IsStart :
		return
	EggState = role.GetObj(EnumObj.PassionActData)[PassionNewYearEgg]
	if 1 not in EggState:
		EggState[1] = [0]*12			#金蛋状态
	if 2 not in EggState:
		EggState[2] = [0]*3				#在线领取锤子状态
	if 3 not in EggState:
		EggState[3] = [0]*3				#充值领取锤子状态



if "_HasLoad" not in dir() :
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OpenNewYearDayEgg", "金蛋打开面板"), OpenNewYearDayEgg)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearDayEggOnLineAward", "领取在线锤子奖励"), NewYearDayEggOnLineAward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearDayEggRMBAward", "领取充值锤子奖励"), NewYearDayEggRMBAward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearDayEggAward", "砸金旦"), NewYearDayEggAward)
		Event.RegEvent(Event.Eve_StartCircularActive, OpenActive)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseActive)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeRMB)
		Event.RegEvent(Event.Eve_RoleDayClear, AfterNewDay)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		#Event.RegEvent(Event.Eve_InitRolePyObj, StateicPig)
