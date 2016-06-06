#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ToSky.ToSky")
#===============================================================================
# 冲上云霄
#===============================================================================
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDayInt8, EnumObj
from Game.Activity.ToSky import ToSkyConfig
from Game.Role import Event
from Game.Activity import CircularDefine

if "_HasLoad" not in dir():
	ToSkyRewardIndex = AutoMessage.AllotMessage("ToSkyRewardIndex", "冲上云霄翻牌奖励索引")
	ToSkyRewardRecord = AutoMessage.AllotMessage("ToSkyRewardRecord", "冲上云霄翻牌奖励记录")
	
	ToSky_RewardLog = AutoLog.AutoTransaction("ToSky_RewardLog", "冲上云霄翻牌")
	
	ToSkyIsOpen = False
	
def OpenToSky(role, param):
	'''
	开启冲上云霄活动
	@param role:
	@param msg:
	'''
	if param != CircularDefine.CA_ToSky:
		return
	
	global ToSkyIsOpen
	if ToSkyIsOpen:
		print "GE_EXC, ToSky is already open"
		return
	
	ToSkyIsOpen = True
	
def CloseToSky(role, param):
	'''
	关闭冲上云霄活动
	@param role:
	@param msg:
	'''
	if param != CircularDefine.CA_ToSky:
		return
	
	global ToSkyIsOpen
	if not ToSkyIsOpen:
		print "GE_EXC, ToSky is already close"
		return
	
	ToSkyIsOpen = False
	
def RequestTurnCard(role, msg):
	'''
	请求翻牌
	@param role:
	@param msg:
	'''
	global ToSkyIsOpen
	#活动没有开启
	if not ToSkyIsOpen:
		return
	#等级不够
	if role.GetLevel() < EnumGameConfig.ToSkyLevelLimit:
		return
	#背包空间不够 -- 需要预留3个格子
	if role.PackageEmptySize() < EnumGameConfig.ToSkyNeedPackageSize:
		return
	#计算需要的神石是否足够
	nowCnt = role.GetDI8(EnumDayInt8.ToSkyCnt)
	if not nowCnt:
		needRMB = EnumGameConfig.ToSkyFirstNeedRMB
		#版本判断
		if Environment.EnvIsNA():
			needRMB = EnumGameConfig.ToSkyFirstNeedRMB_NA
		elif Environment.EnvIsRU():
			needRMB = EnumGameConfig.ToSkyFirstNeedRMB_RU
	elif nowCnt == 1:
		needRMB = EnumGameConfig.ToSkySecondNeedRMB
		#版本判断
		if Environment.EnvIsNA():
			needRMB = EnumGameConfig.ToSkySecondNeedRMB_NA
		elif Environment.EnvIsRU():
			needRMB = EnumGameConfig.ToSkySecondNeedRMB_RU
	elif nowCnt >= 2:
		needRMB = EnumGameConfig.ToSkyThirdNeedRMB
		#版本判断
		if Environment.EnvIsNA():
			needRMB = EnumGameConfig.ToSkyThirdNeedRMB_NA
		elif Environment.EnvIsRU():
			needRMB = EnumGameConfig.ToSkyThirdNeedRMB_RU
	else:
		return
	
	if role.GetUnbindRMB() < needRMB:
		return
	
	#随机索引
	index = ToSkyConfig.ToSkyRandomIndex.RandomOne()
	if not index:
		return
	cfg = ToSkyConfig.ToSky_Dict.get(index)
	if not cfg:
		print "GE_EXC, ToSky can not find index (%s) in ToSky_Dict" % index
		return
	
	with ToSky_RewardLog:
		#加次数, 扣神石
		if nowCnt <= 2:
			role.IncDI8(EnumDayInt8.ToSkyCnt, 1)
		role.DecUnbindRMB(needRMB)
	
	#同步客户端随机到的索引, 客户端回调后发奖
	role.SendObjAndBack(ToSkyRewardIndex, index, 5, CallBackFun, cfg)
	
def CallBackFun(role, callargv, regparam):
	cfg = regparam
	
	with ToSky_RewardLog:
		#发放奖励
		for item in cfg.items:
			role.AddItem(*item)
	
	#记录获得奖励记录
	recordList = role.GetObj(EnumObj.ToSkyRecord_List)
	if not recordList:
		recordList = [[cDateTime.Month(), cDateTime.Day(), cfg.items]]
	elif len(recordList) < EnumGameConfig.ToSkyMaxRecordCnt:
		recordList.append([cDateTime.Month(), cDateTime.Day(), cfg.items])
	else:
		recordList.pop(0)
		recordList.append([cDateTime.Month(), cDateTime.Day(), cfg.items])
	role.SetObj(EnumObj.ToSkyRecord_List, recordList)
	#同步客户端
	role.SendObj(ToSkyRewardRecord, recordList)
	
def RequestOpenPanel(role, msg):
	'''
	请求打开冲上云霄面板
	@param role:
	@param msg:
	'''
	global ToSkyIsOpen
	#活动未开启
	if not ToSkyIsOpen:
		return
	#等级不够
	if role.GetLevel() < EnumGameConfig.ToSkyLevelLimit:
		return
	
	role.SendObj(ToSkyRewardRecord, role.GetObj(EnumObj.ToSkyRecord_List))
	
def AfterLogin(role, param):
	if not role.GetObj(EnumObj.ToSkyRecord_List):
		role.SetObj(EnumObj.ToSkyRecord_List, [])

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
	
		Event.RegEvent(Event.Eve_StartCircularActive, OpenToSky)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseToSky)
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ToSky_OpenPanel", "请求打开冲上云霄面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ToSky_TurnCard", "请求翻牌"), RequestTurnCard)
	