#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TheMammon.TheMammon")
#===============================================================================
#天降财神
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Game.Role import Event
from Game.Role.Mail import Mail
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from Game.Role.Data import EnumDayInt1
from Game.Activity.TheMammon import TheMammonConfig


if "_HasLoad" not in dir():
	NeedLevel = 20
	NeedVIP = 1
	
	#活动结束时间戳
	StartTime = None
	#日志
	TraTheMammonRebate = AutoLog.AutoTransaction("TraTheMammonRebate", "天降财神返利")
	TraTheMammonTimeSetting = AutoLog.AutoTransaction("TraTheMammonTimeSetting", "天降财神返利活动时间设置")
	#这条消息原来是同步角色活动的开启索引,更新后修改为图标开启状态
	SyncCurrentMammonIndex = AutoMessage.AllotMessage("SyncCurrentMammonIndex", "同步客户端天降财神活动索引")


def IsStart():
	'''
	活动是否开启
	'''
	year = cDateTime.Year()
	month = cDateTime.Month()
	day = cDateTime.Day()
	if (year, month, day) == StartTime:
		return True
	return False


def TimeSetting(year, month, day):
	'''
	活动开始和结束的时间设置
	'''
	global StartTime
	with TraTheMammonTimeSetting:
		StartTime = (year, month, day)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveTheMammonTimeSetting, StartTime)
		
	if IsStart():
		for role in cRoleMgr.GetAllRole():
			if role:
				SyncTheMammonActStatu(role)
				
	print "GREEN, GM set TheMammon act date (year-%s, month-%s, day-%s)" % (year, month, day)


def ClearTimeSetting():
	global StartTime
	with TraTheMammonTimeSetting:
		StartTime = None
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveTheMammonTimeSetting, StartTime)
	
	for role in cRoleMgr.GetAllRole():
		if role:
			SyncTheMammonActStatu(role)


def GetTimeSetting():
	return StartTime


def AfterChangeUnbindRMB_Q(role, param):
	'''
	监听Q点神石数值变化
	'''
	#仅监听神石增加的情况
	oldValue, newValue = param
	if IsStart() is False:
		return
	
	if newValue <= oldValue:
		return
	
	if role.GetLevel() < NeedLevel:
		return
	
	#这里VIP的改变是在触发神石数值改变之后才发生的
	if role.GetVIP() < NeedVIP:
		return
	
	if role.GetDI1(EnumDayInt1.TheMammon) is True:
		return
	
	#单笔充值神石的数量
	singleBill = newValue - oldValue
	config = GetConfig(singleBill)
	if config is None:
		return
	
	with TraTheMammonRebate:
		role.SetDI1(EnumDayInt1.TheMammon, True)
		roleId = role.GetRoleID()
		Mail.SendMail(roleId,
				GlobalPrompt.TheMammonMailTitle,
				GlobalPrompt.TheMammonMailSender,
				GlobalPrompt.TheMammonMailContent,
				items=config.rebate)

	SyncTheMammonActStatu(role)


def GetConfig(singleBill):
	'''
	 获取当前的配置
	'''
	for _, config in TheMammonConfig.TheMammonConfigDict.iteritems():
		if not config.chargeValue[0] <= singleBill <= config.chargeValue[1]:
			continue
		return config
		
	else:
		#如果没要满足要求的配置的话
		return None


def GetActStatu(role):
	'''
	获取角色活动图标开启情况
	'''
	if role.GetLevel() < NeedLevel:
		return 0
	
	if role.GetVIP() < NeedVIP:
		return 0
	
	if IsStart() is False:
		return 0
	
	if role.GetDI1(EnumDayInt1.TheMammon) is True:
		return 0
	
	return 1


def SyncTheMammonActStatu(role):
	'''
	同步天降财神活动索引
	'''
	statu = GetActStatu(role)
	role.SendObj(SyncCurrentMammonIndex, statu)


def OnSyncRoleOtherData(role, param):
	'''
	同步角色其他数据
	'''
	SyncTheMammonActStatu(role)
	

def OnAfterLevelUp(role, param):
	'''
	角色升级后处理
	'''
	SyncTheMammonActStatu(role)


def RoleDayClear(role, param):
	SyncTheMammonActStatu(role)


def AfterChangeVIP(role):
	SyncTheMammonActStatu(role)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and not Environment.EnvIsNA():
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnAfterLevelUp)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
