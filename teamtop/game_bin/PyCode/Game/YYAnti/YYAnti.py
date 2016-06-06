#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.YYAnti.YYAnti")
#===============================================================================
# YY防沉迷及称号环境处理
#===============================================================================
import Environment
import cDateTime
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt1, EnumInt16, EnumDisperseInt32, EnumTempInt64
from Game.Activity.Title import Title

HALFREWARD = 1 #收益减半
ALLREWARD = 0  #原有收益
NOREWARD = -1  #无收益


def YYAntiTickTock(role, calArgvs, regParam):
	'''
	防沉迷计时
	@param role:
	@param calArgvs:
	@param regParam:
	'''
	if not role.GetI1(EnumInt1.YYAntiState):#已不在防沉迷
		return
	if role.GetI16(EnumInt16.YYAntiOnlineMinCnt) > EnumGameConfig.YY_Anti_FiveHours + 5:#超过5小时+5分就不计时了
		return
	role.IncI16(EnumInt16.YYAntiOnlineMinCnt, 1)
	OnlineMin = role.GetI16(EnumInt16.YYAntiOnlineMinCnt)
	if OnlineMin in (60, 120, 180, 240):
		role.Msg(2, 0, GlobalPrompt.YYAnti_Msg % (OnlineMin/60))
	elif OnlineMin == 210:
		role.Msg(2, 0, GlobalPrompt.YYAnti_Msg % 3.5)
	elif OnlineMin == 270:
		role.Msg(2, 0, GlobalPrompt.YYAnti_Msg % 4.5)
	
	role.RegTick(60, YYAntiTickTock)
	
def AfterLogin(role, param):
	'''
	玩家登录
	@param role:
	@param param:
	'''
	LoginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	from1 = LoginInfo.get('pf', 0)
	if from1 != "duowan":
		return
	#在玩家身上记录平台
	role.SetTI64(EnumTempInt64.IsDomesticType, 1)
	
	LoginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	fm = int(LoginInfo.get('fm', 0))
	
	if fm == 0 or fm == 2:#未注册防沉迷或注册了但未成年
		role.SetI1(EnumInt1.YYAntiState, 1)
	elif fm == 1:
		role.SetI1(EnumInt1.YYAntiState, 0)
	else:
		print "GE_EXC,fm(%s) is wrong" % fm
		return
	YYAntiState = role.GetI1(EnumInt1.YYAntiState)
	if YYAntiState:
		#离线5小时上线后积累时间清0
		last_time = role.GetDI32(EnumDisperseInt32.LastSaveUnixTime)
		hours = (cDateTime.TimeZoneSeconds() - last_time) / 3600
		if hours >= 5:
			role.SetI16(EnumInt16.YYAntiOnlineMinCnt, 0)
		#一分钟tick
		role.RegTick(60, YYAntiTickTock)
	
def RoleDayClear(role, param):
	'''
	跨天清理
	@param role:
	@param param:
	'''
	if role.GetI16(EnumInt16.YYAntiOnlineMinCnt):
		role.SetI16(EnumInt16.YYAntiOnlineMinCnt, 0)
		
def SyncRoleOtherData(role, param):
	LoginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	fm = int(LoginInfo.get('fm', 0))
	if fm == 1:
		if role.GetI1(EnumInt1.YYAntiState):
			role.SetI1(EnumInt1.YYAntiState, 0)
		if role.GetI16(EnumInt16.YYAntiOnlineMinCnt):
			role.SetI16(EnumInt16.YYAntiOnlineMinCnt, 0)


def GetAnti(role):
	global HALFREWARD  #收益减半
	global ALLREWARD   #原有收益
	global NOREWARD    #无收益
	if Environment.EnvIsYY() and role.GetTI64(EnumTempInt64.IsDomesticType) and role.GetI1(EnumInt1.YYAntiState):
		#进入YY防沉迷
		YYAntiOnlineMinCnt = role.GetI16(EnumInt16.YYAntiOnlineMinCnt)
		if YYAntiOnlineMinCnt < EnumGameConfig.YY_Anti_ThreeHours:
			#全收益
			return ALLREWARD
		elif EnumGameConfig.YY_Anti_ThreeHours <= YYAntiOnlineMinCnt < EnumGameConfig.YY_Anti_FiveHours:
			#半收益
			return HALFREWARD
		else:
			return NOREWARD
	else:
		#非YY防沉迷
		return 0
	
def FirstInitRole(role, param):
	#第一次初始化完成,是YY用户的话增加称号
	if Environment.EnvIsYY():
		LoginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
		from1 = LoginInfo.get('pf', 0)
		if from1 != "duowan":
			return
		Title.AddTitle(role.GetRoleID(), 99)
			
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsYY() or Environment.IsDevelop):
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_FirstInitRole, FirstInitRole)
		