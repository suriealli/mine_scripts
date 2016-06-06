#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActD12GroupBuyMgr")
#===============================================================================
# 全民团购  @author liujia 2015
#===============================================================================
import copy
import time
import datetime
import cDateTime
import Environment
import cProcess
import cComplexServer
import cRoleMgr
from Common.Other import GlobalPrompt
from Game.Role import Event
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Message import PyMessage
from Game.Persistence import Contain
from Game.Role.Data import EnumObj
from ComplexServer.Plug.Control import ControlProxy
from Game.Activity.PassionAct.PassionDefine import PassionD12GroupBuy
from Game.Activity.PassionAct.PassionActD12GroupBuyConfig import PassionActD12GB_Dict,PassionActD12GBControl_Dict

if "_HasLoad" not in dir():

	IsStart = False

	#IsLoadFromControl 	= False		#控制进程载入数据标记
	itemCodingList 		= []		#今日出售列表

	allItemRecord 		= {}		#全服购买记录缓存{index:cnt,...}

	openPanelRoleID_Set = set()
	TodayFlag = 0					#参见控制进程描述
	backData = {}					#双缓存{day1:{},day2:{}}

	dayKey 	= -1					#天数字段key，常量
	dataKey = 1						#数据字段key, 常量
	
	#日志
	D12GroupBuy 	= AutoLog.AutoTransaction("D12GroupBuy", "超值团购购买 ")
	#消息
	D12GroupBuyData 	= AutoMessage.AllotMessage("D12GroupBuyRoleData", "超值团购数据")			#{1:[item_index],2:{index:cnt}}
	
def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionD12GroupBuy:
		return
	if IsStart:
		print 'GE_EXC, PassionActD12GroupBuy is already start'
	IsStart = True

	global itemCodingList
	dataKey = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day())
	itemCodingList = PassionActD12GBControl_Dict.get(dataKey, [])

	global TodayFlag
	TodayFlag = cDateTime.Days()
	
	#本地服务器重启，重新获取数据
	RequestControlData()

def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionD12GroupBuy:
		return
	if not IsStart:
		print 'GE_EXC, PassionActTGPointExchange is already end'
	IsStart = False
	
	global openPanelRoleID_Set
	openPanelRoleID_Set.clear()

def NowTime():
	'''
	获取当前时间戳(精确到秒)
	'''
	return int(time.mktime(datetime.datetime(	\
		cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second() \
		).timetuple()))
	
def RequestGroupBuy(role,msg):
	'''
	玩家请求团购购买
	'''
	global IsStart
	if not IsStart: return

	index = msg
	if index not in itemCodingList:
		print "GE_EXC, can't find the itemObj in today's PassionActD12GBControl_Dict index = %s, roleId = %s" % (index, role.GetRoleID())
		return
	itemObj = PassionActD12GB_Dict.get(index)
	if not itemObj:
		print "GE_EXC, can't find the itemObj in PassionActD12GB_Dict index = %s" % index
		return

	#等级
	if role.GetLevel() < itemObj.needLevel:
		return

	needRMB_Q = 0 	#需要充值神石
	needRMB = 0		#需要奖励神石
	#充值神石
	if itemObj.isRMB_Q:
		if role.GetUnbindRMB_Q() < itemObj.needRMB:
			return
		else:
			needRMB_Q = itemObj.needRMB
	#奖励神石
	else:
		#奖励神石不够，扣除充值神石
		if role.GetUnbindRMB_S() < itemObj.needRMB:
			if role.GetUnbindRMB() < itemObj.needRMB:
				return
			else:
				needRMB = role.GetUnbindRMB_S()
				needRMB_Q = itemObj.needRMB - needRMB
		else:
			needRMB = itemObj.needRMB


	#物品今日已经购买
	dayBuys = role.GetObj(EnumObj.PassionActData)[PassionD12GroupBuy]
	if index in dayBuys:
		return

	#记录购买道具
	dayBuys.add(index)
	coding,cnt = itemObj.items
	with D12GroupBuy:
		#奖励神石
		if needRMB:
			role.DecUnbindRMB(needRMB)
		#充值神石
		if needRMB_Q:
			role.DecUnbindRMB_Q(needRMB_Q)

		role.AddItem(coding, cnt)

	#更新本服购买记录
	tempDict = ForwardBuffer()
	roles = tempDict[index] = tempDict.get(index,[])
	roles.append((role.GetRoleID(),NowTime()))
	
	D12GroupBuy_Record_Dict.HasChange()
	#前20名排序(本服先来后到不用比较时间戳)
	
	SyncUserData(role)
	
def OnGBDataFromControl(sessionid, msg):
	'''
	@控制进程更新了新的跨服团购数据
	@载入数据格式 {index:cnt}
	'''
	global allItemRecord
	allItemRecord = msg

	SyncAllUserData()

def RespondToControlData(dayflag):
	'''
	@返回控制进程请求的数据
	@{index:[(roleid,time)]}
	'''
	global backData
	return (cProcess.ProcessID,backData.get(dayflag,{}))

def OnRequestGBDataFromControl(sessionid, msg):
	'''
	@控制进程请求本服购买数据
	@返回数据格式 {1:消费记录dict,2:前20排行dict}
	'''
	backid, dayflag = msg
	ControlProxy.CallBackFunction(sessionid, backid, RespondToControlData(dayflag))

def OnCleanBackBuffer(sessionid, msg):
	'''
	控制进程统计完成，清空脏数据
	'''
	CleanBackBuffer()
	
def RequestControlData():
	global IsStart
	if not IsStart: return
	
	ControlProxy.SendControlMsg(PyMessage.Control_RequestControlD12GroupBuyData, None)

def SyncAllUserData():
	
	global IsStart
	if not IsStart:
		return
	#向打开面板的用户推送获奖消息
	global openPanelRoleID_Set
	oldRoleSet = set()
	for roleId in openPanelRoleID_Set:
		roleTmp = cRoleMgr.FindRoleByRoleID(roleId)
		if not roleTmp :
			oldRoleSet.add(roleId)
			continue
		
		SyncUserData(roleTmp)
		
	openPanelRoleID_Set -= oldRoleSet
	
	
def SyncUserData(role):
	'''
	同步角色数据
	'''
	global IsStart
	if not IsStart:
		return
	
	#同步个人购买记录
	D12GroupBuy_set = role.GetObj(EnumObj.PassionActData)[PassionD12GroupBuy]
	role.SendObj(D12GroupBuyData,{1:D12GroupBuy_set,2:allItemRecord})
	
def RequestOpenPanel(role, msg):
	'''
	超值团购打开面板
	@param role:
	@param param: None
	'''
	global IsStart
	
	if not IsStart:
		return

	SyncUserData(role)
	
	global openPanelRoleID_Set
	openPanelRoleID_Set.add(role.GetRoleID())

def RequestClosePanel(role,msg):
	
	global openPanelRoleID_Set
	openPanelRoleID_Set.discard(role.GetRoleID())

def RoleDayClear(role, param):
	#玩家数据每日清理
	global IsStart
	if not IsStart: return

	#清空个人购买记录
	role.GetObj(EnumObj.PassionActData)[PassionD12GroupBuy] = set()
	#同步角色团购数据
	SyncUserData(role)

def ForwardBuffer():
	global TodayFlag
	return backData[TodayFlag]

def SwapBackBuffer(newDay):
	'''
	更新缓存
	'''
	global TodayFlag
	#跨天太多
	if newDay - TodayFlag != 1:
		backData[TodayFlag] = {}
	else:
		#昨天
		backData[TodayFlag] = copy.deepcopy(D12GroupBuy_Record_Dict.data[dataKey])
		
	#清空本服数据
	D12GroupBuy_Record_Dict.clear()
	#服务器此时掉线将无法领取自前一整点消费奖励
	#hold ref
	backData[newDay] = D12GroupBuy_Record_Dict.data[dataKey] = {}
	
	D12GroupBuy_Record_Dict[dayKey] = newDay
	D12GroupBuy_Record_Dict.HasChange()
	#更新标志位
	TodayFlag = newDay

def CleanBackBuffer():
	'''
	后备缓存失效，清除之
	'''
	
	for day in backData.keys():
		if day != TodayFlag:
			del backData[day]

def everyNewDay():
	#缓存本日可购买物品
	
	global IsStart
	if not IsStart:	return
	
	global itemCodingList
	
	dataKey = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day())
	itemCodingList = PassionActD12GBControl_Dict.get(dataKey, [])

	#更新缓存
	SwapBackBuffer(cDateTime.Days())
	#清空全服记录缓存
	allItemRecord = {}
	
	#更新角色数据
	SyncAllUserData()
	
def AfterNewHour():
	global IsStart
	if not IsStart: return
	
	cRoleMgr.Msg(1, 1, GlobalPrompt.D12GroupBuy_Tip)	

def AfterD12GBRecord():
	
	global TodayFlag
	TodayFlag = cDateTime.Days()

	global dayKey
	global dataKey
	global backData

	backData = {}
	#数据太旧，清空
	if D12GroupBuy_Record_Dict.get(dayKey,0) != TodayFlag:
		D12GroupBuy_Record_Dict.clear()
		D12GroupBuy_Record_Dict[dayKey] 	= TodayFlag
		D12GroupBuy_Record_Dict[dataKey] 	= {}

	D12GroupBuy_Record_Dict[dataKey] 	= D12GroupBuy_Record_Dict.get(dataKey,{})
	backData[TodayFlag] 		= D12GroupBuy_Record_Dict.data[dataKey]
	
	D12GroupBuy_Record_Dict.HasChange()
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		cComplexServer.RegAfterNewDayCallFunction(everyNewDay)

		cComplexServer.RegDistribute(PyMessage.Control_LogicSendD12GroupBuyData, OnGBDataFromControl)
		cComplexServer.RegDistribute(PyMessage.Control_RequestD12GroupBuyData, OnRequestGBDataFromControl)
		cComplexServer.RegDistribute(PyMessage.Control_CleanLogicGroupBuyData, OnCleanBackBuffer)

		#本服持久化数据{-1:day,1:{}}
		D12GroupBuy_Record_Dict = Contain.Dict("D12GroupBuy_Record_Dict", (2038, 1, 1), AfterD12GBRecord)		#{-1:day,2:{index:[roleid],...}} ordered 列表

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Passion_D12GroupBuy_OpenPane", "请求打开超值团购面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Passion_D12GroupBuy_ClosePane", "请求关闭超值团购面板") ,RequestClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Passion_D12GroupBuy", "请求团购物品"), RequestGroupBuy)
