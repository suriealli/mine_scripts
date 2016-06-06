#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.VIP.VIPMgr")
#===============================================================================
# 会员系统
#===============================================================================
import Environment
import cRoleDataMgr
import cRoleMgr
from Common.Other import EnumAppearance, EnumSocial, GlobalPrompt,\
	EnumGameConfig
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
from Game.Role import Event
from Game.Role.Data import EnumDisperseInt32, EnumTempObj, EnumInt32
from Game.Union import UnionDefine
from Game.VIP import VIPConfig
import cDateTime


if "_HasLoad" not in dir():
	pass

def VIPLevelUp(role):
	'''
	VIP等级提升
	@param role:
	'''
	vipLevel = role.GetVIP()
	ConsumeQPoint = role.GetConsumeQPoint()
	IncNum = 1
	vipLevel += 1
	nextLevelCfg = VIPConfig._VIP_BASE.get(vipLevel)
	if not nextLevelCfg:
		return 
	if nextLevelCfg.growValue == -1:
		#已经是超级VIP了
		return
	if ConsumeQPoint < nextLevelCfg.growValue:
		#少于下一级的成长值，暂时不能升级
		return
	
	while 1:
		nextLevelCfg = VIPConfig._VIP_BASE.get(vipLevel + 1)
		if not nextLevelCfg:
			break 
		if nextLevelCfg.growValue == -1:
			#已经是超级VIP了
			break
		if ConsumeQPoint < nextLevelCfg.growValue:
			#少于下一级的成长值，暂时不能升级
			break
		vipLevel += 1
		IncNum += 1
	#设置VIP
	role.SetVIP(vipLevel)
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_VIP, (role, IncNum))
	
	#各版本判断
	if Environment.EnvIsNA():
		if vipLevel <= 4:
			return
		cRoleMgr.Msg(1, 0, GlobalPrompt.VIP_TIPS % (role.GetRoleName(), vipLevel))
	else:
		cRoleMgr.Msg(1, 0, GlobalPrompt.VIP_TIPS % (role.GetRoleName(), vipLevel))
		
		
#===============================================================================
# 数组调用函数
#===============================================================================
def AfterChangeVIP(role, oldValue, newValue):
	#设置外形
	role.SetApperance(EnumAppearance.App_VIP, newValue)
	
	#设置聊天
	role.SetChatInfo(EnumSocial.RoleVIPKey, newValue)
	
	packmgr = role.GetTempObj(EnumTempObj.enPackMgr)
	if packmgr:
		#重新计算背包大小
		packmgr.CountPackageMaxSize()
	#北美环境
	if Environment.EnvIsNA():
		from Game.Activity.KaiFuAct import KaiFuActMgr
		KaiFuActMgr.AfterChangeVIP(role)
		
	from Game.Activity.TheMammon import TheMammon
	TheMammon.AfterChangeVIP(role)
	
	#设置公会内VIP
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	roleId = role.GetRoleID()
	#是不是公会成员
	if unionObj.IsMember(roleId) is False:
		return
	#设置VIP
	unionObj.members[roleId][UnionDefine.M_VIP_IDX] = newValue
	#保存
	unionObj.HasChange()
	
	

#===============================================================================
# 事件
#===============================================================================
def AfterEve_QPoint(role, param):
	#消费Q点改变尝试触发vip等级提升
	VIPLevelUp(role)
	#记录最后一次充值时间
	role.SetI32(EnumInt32.LastChargeSeconds, cDateTime.Seconds())

def OnChangeUnbindRMB_Q(role, param):
	oldValue, newValue = param
	if newValue < oldValue:
		#增加今日消耗神石数量
		role.IncI32(EnumInt32.DayConsumeUnbindRMB, oldValue - newValue)
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_Consume, role.GetI32(EnumInt32.DayConsumeUnbindRMB)))
	else:
		#增加今日充值神石数量
		role.IncI32(EnumInt32.DayBuyUnbindRMB_Q, newValue - oldValue)
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_Charge, role.GetI32(EnumInt32.DayBuyUnbindRMB_Q)))
		
def OnChangeUnbindRMB_S(role, param):
	oldValue, newValue = param
	if newValue < oldValue:
		#增加今日消耗神石数量
		role.IncI32(EnumInt32.DayConsumeUnbindRMB, oldValue - newValue)
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_Consume, role.GetI32(EnumInt32.DayConsumeUnbindRMB)))


def AfterChangeDayBuyUnbindRMB_Q(role, oldValue, newValue):
	Event.TriggerEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, role, (oldValue, newValue))


def AfterDayConsumeUnbindRMB(role, oldValue, newValue):
	Event.TriggerEvent(Event.Eve_AfterChangeDayConsumeUnbindRMB, role, (oldValue, newValue))


def OnRoleLogin(role, param):
	'''
	角色登录
	@param role:
	@param param:
	'''
	
def OnRoleDayClear(role, param):
	'''
	角色每日清理
	@param role:
	@param param:
	'''
	role.SetI32(EnumInt32.DayBuyUnbindRMB_Q, 0)
	role.SetI32(EnumInt32.DayConsumeUnbindRMB, 0)
	
if "_HasLoad" not in dir():
	#事件
	Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
	
	Event.RegEvent(Event.AfterChangeUnbindRMB_Q, OnChangeUnbindRMB_Q, index = 0)
	Event.RegEvent(Event.AfterChangeUnbindRMB_S, OnChangeUnbindRMB_S, index = 0)
	Event.RegEvent(Event.Eve_GamePoint, AfterEve_QPoint, index = 0)
	Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear, index = 0)
	
	#设置数组改变调用的函数
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.enVIP, AfterChangeVIP)
	cRoleDataMgr.SetInt32Fun(EnumInt32.DayBuyUnbindRMB_Q, AfterChangeDayBuyUnbindRMB_Q)
	cRoleDataMgr.SetInt32Fun(EnumInt32.DayConsumeUnbindRMB, AfterDayConsumeUnbindRMB)
	
