#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationDay.DailyLiBao")
#===============================================================================
# 国庆每日登陆礼包
#===============================================================================
import datetime
import cRoleMgr
import cDateTime
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity.NationDay import DailyLiBaoConfig
from Game.Activity import CircularDefine, CircularActive

ND_DAILY_OBJ_INDEX = 2
ND_DAILY_MAX_CNT = 8

if "_HasLoad" not in dir():
	IS_START = False	#活动状态标识 初始关闭
	DAY_INDEX = 0		#(0-6)天数索引 及今天是活动的第N天  活动开启初始为1 AfterNewDay增加1 避免每次下推重复计算
	
	ND_DAILYLIBAO_OPEN_ROLES = set()	#当前打开登陆礼包面板的roleID集合 
	
	ND_DailyLiBao_S_Record = AutoMessage.AllotMessage("ND_DailyLiBao_S_Record", "同步国庆登陆礼包记录") #(DAY_INDEX,领取记录set())
	
	Tra_ND_DailyLiBao = AutoLog.AutoTransaction("Tra_ND_DailyLiBao", "国庆登陆礼包领取") 

#============ 状态 ==============	
def ND_DailyLiBaoStart(*param):
	'''
	国庆登陆礼包活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.ND_DailyLiBao:
		return
	
	#重复开启
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open ND_DailyLiBao!"
		return
	
	#更新标志
	IS_START = True
	
	#初始活动开启天数
	global DAY_INDEX
	circularACtiveCfg = CircularActive.CircularActiveConfig_Dict.get(CircularDefine.ND_DailyLiBao)	
	if not circularACtiveCfg:
		print "GE_EXC,config error! cannot get circularACtive config of activeType(%s)" % CircularDefine.ND_DailyLiBao
		DAY_INDEX = 1	#保险起见 找不到就默认1吧
		return
	
	#活动开启时刻 根据当前时间和活动配置startDate初始DAY_INDEX 因为有可能是活动期间重启维护 
	startDate = datetime.datetime(*circularACtiveCfg.startDate)
	#当前日期时间
	nowDate = datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	#活动持续开启的天数
	durableDay = (nowDate - startDate).days 	
	#更新全局DAY_INDEX
	DAY_INDEX = durableDay + 1
	
	#超过8天 强制设置8天
	if DAY_INDEX > ND_DAILY_MAX_CNT:
		DAY_INDEX = ND_DAILY_MAX_CNT	
	
def ND_DailyLiBaoEnd(*param):
	'''
	国庆登陆礼包活动结束
	'''
	_, circularType = param
	if circularType != CircularDefine.ND_DailyLiBao:
		return
	
	#重复关闭
	global IS_START
	if not IS_START:
		print "GE_EXC,repeat close ND_DailyLiBao!"
		return
	
	#更新标志
	IS_START = False

#============= 请求 ================
def OnDailyLiBao(role, msg):
	'''
	@param role: 
	@param msg:dayIndex 领取奖励所对应的天数索引 
	'''
	#活动未开启
	if not IS_START:
		return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.ND_DailyLiBaoNeedLevel:
		return
	
	#已经领取
	dayIndexToGet = msg
	gottenLiBaoSet = (role.GetObj(EnumObj.NationData)).get(ND_DAILY_OBJ_INDEX,set())
	if dayIndexToGet in gottenLiBaoSet:
		return
	
	#活动天数不足 不可以领取
	if dayIndexToGet > DAY_INDEX:
		return
	
	#背包空间不足
	if role.PackageEmptySize() < 1:
		role.Msg(2, 0, GlobalPrompt.ND_DailyLiBao_PackageIsFull)
		return 
	
	#对应礼包配置获取
	LiBaoCfg = DailyLiBaoConfig.ND_DAILY_LIBAO_DICT.get(dayIndexToGet, None)
	if not LiBaoCfg:
		return
	
	#是否补领
	isNotToday = False
	if DAY_INDEX != dayIndexToGet:
		isNotToday = True
	
	#补领RMB是否足够
	if isNotToday:
		if role.GetUnbindRMB() < LiBaoCfg.costRMB:
			return	
	
	#process
	promptMsg = ""
	with Tra_ND_DailyLiBao:
		#更新领取礼包记录
		gottenLiBaoSet.add(dayIndexToGet)
		role.GetObj(EnumObj.NationData)[ND_DAILY_OBJ_INDEX] = gottenLiBaoSet
		
		#补领扣除神石
		if isNotToday:
			role.DecUnbindRMB(LiBaoCfg.costRMB)
		
		#获得礼包
		itemCoding, itemCnt = LiBaoCfg.item
		role.AddItem(itemCoding, itemCnt)
		promptMsg += GlobalPrompt.ND_Tips_DailyLiBao % (itemCoding, itemCnt)
		
		#同步客户端最新数据
		role.SendObj(ND_DailyLiBao_S_Record, (DAY_INDEX,gottenLiBaoSet))
		
		#获得提示
		role.Msg(2, 0, promptMsg)

def OnOpenDailyLiBaoPanel(role, msg):
	'''
	打开国庆登陆礼包面板
	'''
	#国庆登陆礼包未开启
	if not IS_START:
		return
	
	#等级限制
	if role.GetLevel() < EnumGameConfig.ND_DailyLiBaoNeedLevel:
		return
	
	global ND_DAILYLIBAO_OPEN_ROLES
	if role.GetRoleID() not in ND_DAILYLIBAO_OPEN_ROLES:
		ND_DAILYLIBAO_OPEN_ROLES.add(role.GetRoleID())
	
	gottenLiBaoSet = (role.GetObj(EnumObj.NationData)).get(ND_DAILY_OBJ_INDEX,set())
	role.SendObj(ND_DailyLiBao_S_Record, (DAY_INDEX,gottenLiBaoSet))	
	
def OnCloseDailyLiBaoPanel(role, msg):
	'''
	关闭国情登录礼包面板
	'''
	#国庆登陆礼包未开启
	if not IS_START:
		return
	
	#等级限制
	if role.GetLevel() < EnumGameConfig.ND_DailyLiBaoNeedLevel:
		return
	
	global ND_DAILYLIBAO_OPEN_ROLES
	ND_DAILYLIBAO_OPEN_ROLES.discard(role.GetRoleID())
	
#============= 事件 =================
def  AfterNewDay():
	'''
	新的一天 重新下推ND_DailyLiBao_S_Record 因为今日是活动的第几天增加了 23:59:59打开了未领取的 0:0:1变成了补领
	'''
	# 活动未开启
	if not IS_START:
		return
	
	#活动开始的天数
	circularACtiveCfg = CircularActive.CircularActiveConfig_Dict.get(CircularDefine.ND_DailyLiBao)	
	if not circularACtiveCfg:
		print "GE_EXC,config error! cannot get circularACtive config of activeType(%s)" % CircularDefine.ND_DailyLiBao
		return
	
	#活动开启日期时间
	startDate = datetime.datetime(*circularACtiveCfg.startDate)
	#当前日期时间
	nowDate = datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	#活动持续开启的天数
	durableDay = (nowDate - startDate).days 	
	#更新全局DAY_INDEX
	global DAY_INDEX
	DAY_INDEX = durableDay + 1	
	#超过8天 强制设置8天
	if DAY_INDEX > ND_DAILY_MAX_CNT:
		DAY_INDEX = ND_DAILY_MAX_CNT
	
	#重发当前打开面板玩家数据 跨天DAY_INDEX有更新 “可领取”变“补领” 
	invalidRoleID = set()
	global ND_DAILYLIBAO_OPEN_ROLES
	for memberID in ND_DAILYLIBAO_OPEN_ROLES:
		member = cRoleMgr.FindRoleByRoleID(memberID)
		if not member:
			invalidRoleID.add(memberID)
			continue
		
		gottenLiBaoSet = (member.GetObj(EnumObj.NationData)).get(ND_DAILY_OBJ_INDEX,set())
		member.SendObj(ND_DailyLiBao_S_Record, (DAY_INDEX,gottenLiBaoSet))
	
	#剔除不在线的roleID
	for invalidID in invalidRoleID:
		ND_DAILYLIBAO_OPEN_ROLES.discard(invalidID)

def OnClientLost(role, param):
	'''
	角色客户端掉线
	'''
	#国庆登陆礼包未开启
	if not IS_START:
		return
	
	global ND_DAILYLIBAO_OPEN_ROLES
	ND_DAILYLIBAO_OPEN_ROLES.discard(role.GetRoleID())
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#跨天处理
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		#活动控制
		Event.RegEvent(Event.Eve_StartCircularActive, ND_DailyLiBaoStart)
		Event.RegEvent(Event.Eve_EndCircularActive, ND_DailyLiBaoEnd)	
		
		#角色离线
		Event.RegEvent(Event.Eve_ClientLost, OnClientLost)
		Event.RegEvent(Event.Eve_BeforeExit, OnClientLost) 
		
		#玩家请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ND_OnDailyLiBao", "请求领取国庆登陆礼包"), OnDailyLiBao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ND_OnOpenDailyLiBaoPanel", "打开国庆登陆礼包面板"), OnOpenDailyLiBaoPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ND_OnCloseDailyLiBaoPanel", "关闭国庆登陆礼包面板"), OnCloseDailyLiBaoPanel)
		