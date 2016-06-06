#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TimeLimitSupply.TimeLimitSupply")
#===============================================================================
# 限时特供
#===============================================================================
import Environment
import cDateTime
import datetime
import time
import cRoleMgr
import cNetMessage
import cComplexServer
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt32, EnumDayInt1
from Game.Activity.TimeLimitSupply import TLSConfig

TLS_MailBuy = 1
TLS_Consume = 2
TLS_Buy = 3

if "_HasLoad" not in dir():
	StartFlag = False		#活动开启标志
	EndTime = 0				#活动结束时间
	ActDict = {}			#{活动标签索引:(活动编号, 活动类型, 活动参数)}
	TLSFun = {}				#类型检测函数
	
	#标签对应的枚举
	IndexToEnum = {1:EnumDayInt1.TimeLimitSupply_1, 2:EnumDayInt1.TimeLimitSupply_2, 3:EnumDayInt1.TimeLimitSupply_3}
	
	TLS_EndTime = AutoMessage.AllotMessage("TLS_EndTime", "限时特供结束时间")
	#{标签:(活动类型, 活动参数), ...}
	TLS_Data = AutoMessage.AllotMessage("TLS_Data", "限时特供开启活动数据")
	
	TLSReward_Log = AutoLog.AutoTransaction("TLSReward_Log", "限时特供领取奖励日志")
	
def LinkTLSFun():
	global TLSFun
	TLSFun[TLS_Buy] = CheckBuy		#充值
	TLSFun[TLS_Consume] = CheckConsume		#消费
	TLSFun[TLS_MailBuy] = CheckMallBuy		#购物
	
def CheckBuy(role, param):
	#检查充值是否满足
	return role.GetDayBuyUnbindRMB_Q() >= param

def CheckConsume(role, param):
	#检查消费值是否满足
	return role.GetDayConsumeUnbindRMB() >= param

def CheckMallBuy(role, param):
	#检查是否商城购买物品
	return role.GetDI1(EnumDayInt1.IsMallBuy)

def TLSControl(actTime, actId):
	'''
	限时特供控制模块
	@param actTime:开始时间, 结束时间
	@param actParam:{活动枚举:(活动类型, 活动参数)}
	'''
	global StartFlag
	if StartFlag:
		print 'GE_EXC, TLSControl StartFlag is already True'
		return
	
	cfg = TLSConfig.TimeLimitConfig_Dict.get(actId)
	if not cfg:
		print 'GE_EXC, TLSControl actId %s error' % actId
		return
	
	#读取要开的活动配置, 生成需要的数据
	actParam = {}
	for index, number in enumerate(cfg.actList):
		actCfg = TLSConfig.TimeLimitSupply_Dict.get(number)
		if not actCfg:
			continue
		actParam[index+1] = (actCfg.number, actCfg.actType, actCfg.param)
	
	beginDate, endDate = actTime
	
	#当前日期-时间
	nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	
	if beginDate < nowDate:
		#开始时间小于当前时间
		print 'GE_EXC, TLSControl beginDate less nowDate'
		return
	if beginDate > endDate:
		#开始时间小于结束时间
		print 'GE_EXC, TLSControl endDate less beginDate'
		return
	
	#当前的时间戳
	nowTime = cDateTime.Seconds()
	#开始时间戳
	beginTime = int(time.mktime(datetime.datetime(*beginDate).timetuple()))
	#结束时间戳
	endTime = int(time.mktime(datetime.datetime(*endDate).timetuple()))
	
	if beginTime <= nowTime < endTime:
		#开启 并注册结束tick
		StartTLS(None, (actParam, endTime))
		cComplexServer.RegTick(endTime - nowTime, EndTLS)
	elif nowTime < beginTime:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, StartTLS, (actParam, endTime))
		cComplexServer.RegTick(endTime - nowTime, EndTLS)
	
def StartTLS(param1, param2):
	global StartFlag, ActDict, EndTime
	if StartFlag:
		print 'GE_EXC, StartTLS StartFlag is already True'
	StartFlag = True
	
	actDict, endTime = param2
	
	if ActDict:
		print 'GE_EXC, StartTLS ActDict is not empty'
	ActDict = actDict
	
	if EndTime:
		print 'GE_EXC, StartTLS EndTime is not zero'
	EndTime = endTime
	
	#同步客户端活动开始
	cNetMessage.PackPyMsg(TLS_EndTime, endTime)
	cRoleMgr.BroadMsg()
	
	cNetMessage.PackPyMsg(TLS_Data, ActDict)
	cRoleMgr.BroadMsg()
	
def EndTLS(param1, param2):
	global StartFlag, ActDict, EndTime
	if not StartFlag:
		print 'GE_EXC, EndTLS StartFlag is already False'
	StartFlag = False
	
	if not ActDict:
		print 'GE_EXC, EndTLS ActDict is already empty'
	ActDict = {}
	
	EndTime = 0
	
	#同步客户端活动结束
	cNetMessage.PackPyMsg(TLS_EndTime, 0)
	cRoleMgr.BroadMsg()
	
def RequestTLSReward(role, msg):
	'''
	请求限时特供奖励
	@param role:
	@param msg:
	'''
	global StartFlag
	if not StartFlag: return
	
	index = msg
	
	global ActDict
	if index not in ActDict:
		#索引错误
		return
	actParam = ActDict[index]
	
	global TLSFun
	checkFun = TLSFun.get(actParam[1])
	if not checkFun:
		#检测函数错了
		return
	if not checkFun(role, actParam[2]):
		#没达到要求
		return
	
	cfg = TLSConfig.TimeLimitSupply_Dict.get(actParam[0])
	if not cfg:
		#没有配置
		return
	
	global IndexToEnum
	#设置领取奖励标志
	role.SetDI1(IndexToEnum[index], True)
	
	#奖励
	with TLSReward_Log:
		tips = GlobalPrompt.Reward_Tips
		for item in cfg.rewardItem:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		role.Msg(2, 0, tips)
	
def SyncRoleOtherData(role, param):
	global StartFlag
	if not StartFlag: return
	
	global EndTime, ActDict
	role.SendObj(TLS_EndTime, EndTime)
	
	role.SendObj(TLS_Data, ActDict)

if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		LinkTLSFun()
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TLS_Reward", "请求领取限时特供奖励"), RequestTLSReward)
		
	