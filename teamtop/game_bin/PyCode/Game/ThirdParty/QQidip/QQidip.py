#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQidip.QQidip")
#===============================================================================
# 逻辑进程
#===============================================================================
import Environment
from Game.Role import Event
from ComplexServer.Plug.DB import DBProxy
from Game.Role.Data import EnumTempObj, EnumDayInt8, EnumInt16, EnumInt8,\
	EnumObj
from ComplexServer import Init
import cDateTime

QQ_DragonBaozang = 1
QQ_Purgatory = 2
QQ_TT = 3
QQ_CouplesFB = 4
QQ_WishPool = 5
QQ_DayTask = 6
QQ_TiLiTask = 7
QQ_Gold = 8
QQ_JJC = 9
QQ_QANDA = 10
QQ_MoShouRuQin = 11
QQ_Duty = 12
QQ_GloyWar = 13

if "_HasLoad" not in dir():
	EvnDict = {}

def E1(role):
	return role.GetDI8(EnumDayInt8.SerachDrgonTimes)

def E2(role):
	return role.GetDI8(EnumDayInt8.PurgatoryCnt)


def E3(role):
	return role.GetDI8(EnumDayInt8.TT_RewradTimes)


def E4(role):
	return role.GetDI8(EnumDayInt8.CouplesFBTimes)

def E5(role):
	return role.GetI16(EnumInt16.WishPoolDayCnt)


def E6(role):
	return role.GetDI8(EnumDayInt8.DayTaskCnt)

def E7(role):
	return role.GetDI8(EnumDayInt8.TiLiTaskCnt)


def E8(role):
	return role.GetI16(EnumInt16.GoldTimesDay)

def E9(role):
	return 15 + role.GetDI8(EnumDayInt8.JJC_Buy_Cnt) - role.GetI8(EnumInt8.JJC_Challenge_Cnt)

def E10(role):
	return 1

def E11(role):
	return 1

def E12(role):
	return 1

def E13(role):
	return 1



def OnServerUp():
	global EvnDict
	EvnDict = {1 : E1,  2: E2, 3: E3, 4: E4, 5: E5, 6: E6, 7: E7, 8: E8,
			 9: E9, 10: E10, 11: E11, 12: E12, 13: E13,}


def GetEAID(role, eventID):
	#event_allot_id
	#角色ID最大2**48， 事件ID最大30000，组合ID
	return role.GetRoleID() + eventID * (2**48)


def UpdateEvent(role, param):
	eventID = param
	fun = EvnDict.get(eventID)
	if not fun:
		return
	roleid = role.GetRoleID()
	eventNum = fun(role)
	if not eventNum:
		return
	event_allot_id = GetEAID(role, eventID)
	DBProxy.DBRoleVisit(roleid, "IDIP_Event", (event_allot_id, roleid, role.GetTempObj(EnumTempObj.LoginInfo)['account'], eventID, eventNum))


def AfterChangeUnbindRMB(role, param):
	oldValue, newValue = param
	if oldValue <= newValue:
		#不是消费
		return
	
	consume = oldValue - newValue
	days = cDateTime.Days()
	consumeDict = role.GetObj(EnumObj.QQidipRoleConsume)
	consumeDict[days] = consumeDict.get(days, 0) + consume


def RoleDayClear(role, param):
	#每日清理，清理8天前的日志
	days = cDateTime.Days()
	consumeDict = role.GetObj(EnumObj.QQidipRoleConsume)
	for d in consumeDict.keys():
		if days - d < 10:
			continue
		del consumeDict[d]


if "_HasLoad" not in dir():
	if (Environment.IsQQ or Environment.IsDevelop)and Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.QQidip_Eve, UpdateEvent)
		Init.InitCallBack.RegCallbackFunction(OnServerUp)
	
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB)
		Event.RegEvent(Event.AfterChangeUnbindRMB_S, AfterChangeUnbindRMB)
		
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		
		