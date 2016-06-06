#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTaoGuan")
#===============================================================================
# 激情活动--欢乐砸陶罐
#===============================================================================
import cRoleMgr
import cProcess
import Environment
from Game.Role import Call, Event
from Game.GlobalData import ZoneName
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Activity.PassionAct import PassionTaoGuanConfig


if "_HasLoad" not in dir():
	IsStart = False
	PassionTaoGuanRecordList = []
	OpenPanelRoleIDSet = set()
	
	#消息
	SyncPassionTaoGuanRecord = AutoMessage.AllotMessage("SyncPassionTaoGuanRecord", "同步激情活动--欢乐砸陶罐获奖记录")
	#日志
	TraPassionTaoGuanOne = AutoLog.AutoTransaction("TraPassionTaoGuanOne", "激情活动一次砸陶罐")
	TraPassionTaoGuanTen = AutoLog.AutoTransaction("TraPassionTaoGuanTen", "激情活动十次砸陶罐")


def Start(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionTaoGuan != circularType:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open CA_PassionTaoGuan"
		return
		
	IsStart = True
	

def End(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionTaoGuan != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end CA_PassionTaoGuan while not start"
		return
		
	IsStart = False


def RequestOpenpanel(role, msg):
	'''
	客户端请求打开面板
	'''
	if not IsStart:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	
	global OpenPanelRoleIDSet
	OpenPanelRoleIDSet.add(role.GetRoleID())
	
	role.SendObj(SyncPassionTaoGuanRecord, PassionTaoGuanRecordList)


def RequestClosePanel(role, msg):
	'''
	客户端请求关闭面板 
	'''
	ClosePanel(role)
	
	
def OnRoleLostOrExit(role, param):
	#角色丢失或者离开时的处理
	ClosePanel(role)


def ClosePanel(role):
	global OpenPanelRoleIDSet
	roleID = role.GetRoleID()
	if roleID not in OpenPanelRoleIDSet:
		return
	OpenPanelRoleIDSet.remove(roleID)
	
	
def RequestTaoGuan(role, msg):
	'''
	客户端请求砸陶罐
	'''
	backID, callType = msg
	if not IsStart:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	
	if callType == 1:
		OneTaoGuan(role, backID)
	elif callType == 10:
		TenTaoGuan(role, backID)


def OneTaoGuan(role, backID):
	#客户端请求砸一次陶罐
	if role.GetUnbindRMB_Q() < EnumGameConfig.PassionTaoGuanOnePrice:
		return
	
	roleLevel = role.GetLevel()
	config = PassionTaoGuanConfig.PassionTaoGuanConfigDict.get(roleLevel)
	if not config:
		print "GE_EXC,error while config = PassionTaoGuanConfig.PassionTaoGuanConfigDict.get(%s) for role(%s)" % (role.GetRoleID, roleLevel)
		return
	
	itemCoding, itemCnt, isBroadcast = config.itemRandomRate.RandomOne()
	taoci = config.taociRandomRate.RandomOne()
	
	tips = GlobalPrompt.PassionTaoGuanOne
	with TraPassionTaoGuanOne:
		role.DecUnbindRMB_Q(EnumGameConfig.PassionTaoGuanOnePrice)
		role.AddItem(itemCoding, itemCnt)
		role.AddItem(*taoci)
		tips += GlobalPrompt.Item_Tips % taoci
		tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)

	if isBroadcast:
		zName = ZoneName.GetZoneName(cProcess.ProcessID)
		Call.ServerCall(0, "Game.Activity.PassionAct.PassionTaoGuan", "TaoGuanServerCall", (zName, role.GetRoleName(), [(itemCoding, itemCnt)]))
		globalTips = GlobalPrompt.PassionTaoGuanGlobalTell % role.GetRoleName() + GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		cRoleMgr.Msg(1, 0, globalTips)
		
	role.CallBackFunction(backID, 1)
	role.Msg(2, 0, tips)


def TenTaoGuan(role, backID):
	#客户端请求砸十次陶罐
	if role.GetUnbindRMB_Q() < EnumGameConfig.PassionTaoGuanTenPrice:
		return

	roleLevel = role.GetLevel()
	config = PassionTaoGuanConfig.PassionTaoGuanConfigDict.get(roleLevel)
	if not config:
		print "GE_EXC,error while config = PassionTaoGuanConfig.PassionTaoGuanConfigDict.get(%s) for role(%s)" % (role.GetRoleID, roleLevel)
		return
	
	itemList = []
	taociList = []
	
	IA = itemList.append
	TA = taociList.append
	CIR = config.itemRandomRate.RandomOne
	CTR = config.taociRandomRate.RandomOne
	for _ in xrange(10):
		IA(CIR())
		TA(CTR())
		
	rewardDict = {}
	broadcastDict = {}
	RG = rewardDict.get
	BG = broadcastDict.get
	globalTips = GlobalPrompt.PassionTaoGuanGlobalTell % role.GetRoleName()
	for itemCoding, itemCnt, isBraodcast in itemList:
		rewardDict[itemCoding] = RG(itemCoding, 0) + itemCnt
		if isBraodcast:
			broadcastDict[itemCoding] = BG(itemCoding, 0) + itemCnt
			
	for taociCoding, taociCnt in taociList:
		rewardDict[taociCoding] = RG(taociCoding, 0) + taociCnt
	
	tips = GlobalPrompt.PassionTaoGuanTen
	with TraPassionTaoGuanTen:
		role.DecUnbindRMB_Q(EnumGameConfig.PassionTaoGuanTenPrice)
		for item in rewardDict.iteritems():
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	if broadcastDict:
		zName = ZoneName.GetZoneName(cProcess.ProcessID)
		Call.ServerCall(0, "Game.Activity.PassionAct.PassionTaoGuan", "TaoGuanServerCall", (zName, role.GetRoleName(), broadcastDict.items()))
		for item in broadcastDict.iteritems():
			globalTips += GlobalPrompt.Item_Tips_1 % item + "    "
		cRoleMgr.Msg(1, 0, globalTips)
	
	role.CallBackFunction(backID, 10)
	role.Msg(2, 0, tips)
	

def TaoGuanServerCall(param):
	#砸陶罐跨服调用
	if not IsStart:
		return
	
	zName, rName, itemList = param
	
	global PassionTaoGuanRecordList
	if len(PassionTaoGuanRecordList) >= 50:
		PassionTaoGuanRecordList.pop(0)
	PassionTaoGuanRecordList.append([zName, rName, itemList])
	
	CF = cRoleMgr.FindRoleByRoleID
	for troleId in OpenPanelRoleIDSet:
		trole = CF(troleId)
		if not trole:
			continue
		trole.SendObj(SyncPassionTaoGuanRecord, PassionTaoGuanRecordList)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleLostOrExit)
		Event.RegEvent(Event.Eve_ClientLost, OnRoleLostOrExit)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionTaoGuan", "客户端请求激情砸陶罐"), RequestTaoGuan)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionTaoGuanOpenPanel", "客户端请求激情砸陶罐打开面板"), RequestOpenpanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionTaoGuanClosePanel", "客户端请求激情砸陶罐关闭面板"), RequestClosePanel)
