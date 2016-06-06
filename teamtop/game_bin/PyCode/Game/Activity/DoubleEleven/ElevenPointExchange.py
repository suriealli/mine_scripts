#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.ElevenPointExchange")
#===============================================================================
# 双十一积分兑换控制  @author Gaoshuai 2015
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Game.Role import Event
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumObj
from Common.Other import GlobalPrompt
from Game.Activity.DoubleEleven import ElevenActivityDefine
from Game.Activity.DoubleEleven.ElevenPointExchangeConfig import ElevenPointExchange_Dict, ElevenPointControl_Dict
import cComplexServer

if "_HasLoad" not in dir():
	IsStart = False
	#消息
	ElevenPointExchangeData = AutoMessage.AllotMessage("ElevenPointExchangeData", "双十一积分兑换个人数据")
	ElevenPointExchangeRecordData = AutoMessage.AllotMessage("ElevenPointExchangeRecordData", "双十一积分兑换兑本服记录")
	#日志
	ElevenPointExchangeLog = AutoLog.AutoTransaction("ElevenPointExchangeLog", "双十一积分兑换成功 ")
	
	rewardList = []
	openPanelRoleID_Set = set()
	itemCodingList = []

def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_ElevenPointExchange:
		return
	if IsStart:
		print 'GE_EXC, ElevenPointExchange is already start'
	IsStart = True
	
	global itemCodingList
	dataKey = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day())
	itemCodingList = ElevenPointControl_Dict.get(dataKey, [])
def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_ElevenPointExchange:
		return
	if not IsStart:
		print 'GE_EXC, ElevenPointExchange is already end'
	IsStart = False
	global openPanelRoleID_Set, rewardList
	rewardList = []
	openPanelRoleID_Set.clear()
	
def RequestElevenPointExchange(role, msg):
	'''
	双十一请求积分兑换物品
	@param role:
	@param msg: (物品索引，物品兑换数量)
	'''
	global IsStart
	if not IsStart: return
	#消息参数是否合法
	
	index, requestCnt = msg
	if requestCnt <= 0:
		return
	if index not in itemCodingList:
		print "GE_EXC, can't find the itemObj in today's ElevenPointControl_Dict index = %s, roleId = %s" % (index, role.GetRoleID())
		return
	itemObj = ElevenPointExchange_Dict.get(index)
	if not itemObj:
		print "GE_EXC, can't find the itemObj in ElevenPointExchange_Dict index = %s" % index
		return
	#等级
	if role.GetLevel() < itemObj.minLevel:
		return
	
	#物品数量超过限购
	exchangeDict = role.GetObj(EnumObj.ElevenActData)[ElevenActivityDefine.ElevenPointExchange]
	maxNum = itemObj.limitCnt - exchangeDict[2].get(index, 0)
	
	#积分不够
	if itemObj.needPoint * requestCnt > exchangeDict[1]:
		return
	#超过限购个数
	
	if itemObj.limitCnt != 0 and maxNum < requestCnt:
		return
	
	coding, cnt = itemObj.items
	#双十一积分兑换成功
	with ElevenPointExchangeLog:
		#记录玩家兑换数据
		if itemObj.limitCnt != 0:
			exchangeDict[2][index] = exchangeDict[2].get(index, 0) + requestCnt
		exchangeDict[1] -= itemObj.needPoint * requestCnt
		role.AddItem(coding, cnt * requestCnt)
	
	role.SendObj(ElevenPointExchangeData, exchangeDict)
	global rewardList, openPanelRoleID_Set
	#极品道具获奖提示
	if itemObj.special:
		rewardList.append((role.GetRoleName(), coding, cnt * requestCnt))
		#向打开面板的用户推送获奖消息
		oldRoleSet = set()
		for roleId in openPanelRoleID_Set:
			roleTmp = cRoleMgr.FindRoleByRoleID(roleId)
			if not roleTmp :
				oldRoleSet.add(roleId)
				continue
			roleTmp.SendObj(ElevenPointExchangeRecordData, rewardList)
			
		openPanelRoleID_Set -= oldRoleSet
		msgTip = GlobalPrompt.PointChangeTip_special % (role.GetRoleName(), coding, cnt * requestCnt)
		cRoleMgr.Msg(11, 0, msgTip)
	#普通道具获取提示
	msgTip = GlobalPrompt.Item_Exchang_Tips + GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt * requestCnt)
	role.Msg(2, 0, msgTip)
	
def AfterChangeUnbindRMB_Q(role, param=None):
	'''
	@param role:
	@param param: None 
	'''
	global IsStart
	if not IsStart: return
	oldValue, newValue = param
	if oldValue > newValue:
		return
	newCharge = newValue - oldValue
	point = newCharge / 10
	exchangeDict = role.GetObj(EnumObj.ElevenActData).get(ElevenActivityDefine.ElevenPointExchange, {})
	
	exchangeDict[1] = exchangeDict.get(1, 0) + point
	
	#同步双十一积分兑换个人数据
	role.SendObj(ElevenPointExchangeData, exchangeDict)
	
def RequestOpenPanel(role, param=None):
	'''
	双十一积分兑换商店打开面板
	@param role:
	@param param: None
	'''
	global IsStart
	if not IsStart:	return
	
	global rewardList
	if len(rewardList) > 50:
		rewardList = rewardList[-50:]
	exchangeDict = role.GetObj(EnumObj.ElevenActData).get(ElevenActivityDefine.ElevenPointExchange)
	role.SendObj(ElevenPointExchangeData, exchangeDict)
	role.SendObj(ElevenPointExchangeRecordData, rewardList)
	openPanelRoleID_Set.add(role.GetRoleID())
	
def RequestClosePanel(role, param=None):
	'''
	双十一积分兑换商店关闭面板
	@param role:
	@param param: None
	'''
	global IsStart
	if not IsStart:	return
	
	global openPanelRoleID_Set
	openPanelRoleID_Set.discard(role.GetRoleID())

def OnInitRole(role, param=None):
	#初始化数据
	if ElevenActivityDefine.ElevenPointExchange not in role.GetObj(EnumObj.ElevenActData):
		role.GetObj(EnumObj.ElevenActData)[ElevenActivityDefine.ElevenPointExchange] = {1:0, 2:{}}
	
def everyNewDay():
	#缓存本日可兑换的物品
	global IsStart
	if not IsStart:	return
	
	global itemCodingList
	
	dataKey = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day())
	itemCodingList = ElevenPointControl_Dict.get(dataKey, [])
	
def RoleDayClear(role, param):
	#玩家数据每日清理
	global IsStart
	if not IsStart: return
	role.GetObj(EnumObj.ElevenActData)[ElevenActivityDefine.ElevenPointExchange] = {1:0, 2:{}}
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cComplexServer.RegAfterNewDayCallFunction(everyNewDay)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElevenPointExchangeOpenPanel", "双十一积分兑换商店打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElevenPointExchangeClosePanel", "双十一积分兑换商店关闭面板"), RequestClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestElevenPointExchange", "双十一请求积分兑换物品"), RequestElevenPointExchange)
