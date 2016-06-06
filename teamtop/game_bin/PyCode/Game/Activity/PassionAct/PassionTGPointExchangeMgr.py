#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTGPointExchangeMgr")
#===============================================================================
# 感恩节积分兑换控制  @author liujia 2015
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumObj
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity.PassionAct.PassionDefine import PassionTGExchange
from Game.Activity.PassionAct.PassionTGPointExchangeConfig import PassionActTGPointExchange_Dict, PassionActTGPointPointControlList

if "_HasLoad" not in dir():
	IsStart = False
	IsStart_Rechange = False
	IsStart_Consume = False
	#消息
	
	TGExchangeData = AutoMessage.AllotMessage("TGPointExchangeData", "感恩节积分兑换个人数据")
	TGExchangeRecordData = AutoMessage.AllotMessage("TGPointExchangeRecordData", "感恩节兑换兑本服记录")
	#日志
	TraPointItemUsed = AutoLog.AutoTransaction("TraPointItemUsed", "使用积分道具 ")
	TGPointExchangeLog = AutoLog.AutoTransaction("TGPointExchangeLog", "感恩节积分兑换成功 ")
	
	rewardList = []
	openPanelRoleID_Set = set()
	itemCodingList = PassionActTGPointPointControlList
	
	fresh_everyday = 0  #每日刷新
	fresh_forever = 1  #永久刷新


def StartCircularActive(param1, param2):
	global IsStart_Consume, IsStart_Rechange
	if param2 == CircularDefine.CA_PassionTGPointExchange:
		IsStart_Rechange = True
	elif param2 == CircularDefine.CA_PassionConsumePointExchange:
		IsStart_Consume = True
	else:
		return
	
	global IsStart
	#充值积分与消费积分为互斥活动
	if IsStart_Rechange and IsStart_Consume:
		IsStart_Consume = False
		IsStart_Rechange = False
		IsStart = False
		print 'GE_EXC, ConsumePointExchange and RechargePointExchange can not start at one time.'
		return
	
	if IsStart:
		print 'GE_EXC, PassionActPointExchange is already start'
	IsStart = True


def EndCircularActive(param1, param2):
	if param2 == CircularDefine.CA_PassionTGPointExchange:
		global IsStart_Rechange
		IsStart_Rechange = False
	elif param2 == CircularDefine.CA_PassionConsumePointExchange:
		global IsStart_Consume
		IsStart_Consume = False
	else:
		return
	
	global IsStart
	if not IsStart:
		print 'GE_EXC, PassionActPointExchange is already end'
	IsStart = False
	global openPanelRoleID_Set, rewardList
	rewardList = []
	openPanelRoleID_Set.clear()


def RequestPointExchange(role, msg):
	'''
	请求积分兑换物品
	@param role:
	@param msg: (物品索引，物品兑换数量)
	'''
	global IsStart
	if not IsStart:
		return
	#消息参数是否合法
	
	index, requestCnt = msg
	if requestCnt <= 0:
		return
	if index not in itemCodingList:
		print "GE_EXC, can't find the itemObj in today's PassionActTGPointPointControl_Dict index = %s, roleId = %s" % (index, role.GetRoleID())
		return
	itemObj = PassionActTGPointExchange_Dict.get(index)
	if not itemObj:
		print "GE_EXC, can't find the itemObj in PassionActTGPointExchange_Dict index = %s" % index
		return
	#等级
	if role.GetLevel() < itemObj.minLevel:
		return
	
	#物品数量超过限购
	exchangeDict = role.GetObj(EnumObj.PassionActData)[PassionTGExchange]
	maxNum = itemObj.limitCnt - exchangeDict[2].get(index, 0)
	
	#积分不够
	if itemObj.needPoint * requestCnt > exchangeDict[1]:
		return
	#超过限购个数
	
	if itemObj.limitCnt != 0 and maxNum < requestCnt:
		return
	
	coding, cnt = itemObj.items
	
	if role.PackageEmptySize() < cnt * requestCnt:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips2)
		return
	#双十一积分兑换成功
	with TGPointExchangeLog:
		#记录玩家兑换数据
		if itemObj.limitCnt != 0:
			exchangeDict[2][index] = exchangeDict[2].get(index, 0) + requestCnt
		exchangeDict[1] -= itemObj.needPoint * requestCnt
		role.AddItem(coding, cnt * requestCnt)
	
	role.SendObj(TGExchangeData, exchangeDict)
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
			roleTmp.SendObj(TGExchangeRecordData, rewardList)
			
		openPanelRoleID_Set -= oldRoleSet
	#普通道具获取提示
	msgTip = GlobalPrompt.Item_Exchang_Tips + GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt * requestCnt)
	role.Msg(2, 0, msgTip)


def AfterChangeUnbindRMB_Q(role, param):
	'''
	@param role:
	@param param: None 
	'''
	global IsStart_Rechange
	if not IsStart_Rechange: return
	oldValue, newValue = param
	if oldValue > newValue:
		return
	newCharge = newValue - oldValue
	point = newCharge / 10

	exchangeDict = role.GetObj(EnumObj.PassionActData).get(PassionTGExchange, {})
	exchangeDict[1] = exchangeDict.get(1, 0) + point

	#同步积分兑换个人数据
	role.SendObj(TGExchangeData, exchangeDict)


def AfterConsumeUnbindRMB_Q(role, param):
	'''
	@param role:
	@param param: None 
	'''
	global IsStart_Consume
	if not IsStart_Consume: return
	oldValue, newValue = param
	if oldValue >= newValue:
		return
	costValue = newValue - oldValue
	point = costValue / 10
	exchangeDict = role.GetObj(EnumObj.PassionActData).get(PassionTGExchange, {})
	exchangeDict[1] = exchangeDict.get(1, 0) + point
	
	#同步积分兑换个人数据
	role.SendObj(TGExchangeData, exchangeDict)


def RequestOpenPanel(role, param=None):
	'''
	积分兑换商店打开面板
	@param role:
	@param param: None
	'''
	global IsStart
	if not IsStart:
		return
	
	global rewardList
	if len(rewardList) > 100:
		rewardList = rewardList[-100:]
	exchangeDict = role.GetObj(EnumObj.PassionActData).get(PassionTGExchange)
	role.SendObj(TGExchangeData, exchangeDict)
	role.SendObj(TGExchangeRecordData, rewardList)
	openPanelRoleID_Set.add(role.GetRoleID())


def RequestClosePanel(role, param=None):
	'''
	积分兑换商店关闭面板
	@param role:
	@param param: None
	'''
	global IsStart
	if not IsStart:
		return
	
	global openPanelRoleID_Set
	openPanelRoleID_Set.discard(role.GetRoleID())


def RoleDayClear(role, param):
	#玩家数据每日清理
	global IsStart
	if not IsStart: return
	
	exchangeDict = role.GetObj(EnumObj.PassionActData)[PassionTGExchange]
	for key in exchangeDict[2].keys():
		itemObj = PassionActTGPointExchange_Dict.get(key)
		if not itemObj:
			print "GE_EXC, can't find the itemObj in PassionActTGPointExchange_Dict index = %s" % key
			continue
		#刷新机制
		if itemObj.freshType is fresh_everyday:
			exchangeDict[2].pop(key)


def SyncRoleOtherData(role, param):
	global IsStart
	if not IsStart: return
	exchangeDict = role.GetObj(EnumObj.PassionActData).get(PassionTGExchange, {})
	#同步积分兑换个人数据
	role.SendObj(TGExchangeData, exchangeDict)


def PassionRequestAddPoint(role, item, cnt):
	#积分道具使用
	
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	exchangeDict = role.GetObj(EnumObj.PassionActData).get(PassionTGExchange, {})
	global IsStart_Consume, IsStart_Rechange
	#道具过期
	if item is None:
		return
	if  item.IsDeadTime():
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_DEAD_ITEM)
		return
	itemCoding = item.GetItemCoding()
	
	
	if IsStart_Rechange:
		if itemCoding != EnumGameConfig.PointItemRecharge:
			role.Msg(2, 0, GlobalPrompt.ActivityClosed)
			return
	elif IsStart_Consume:
		if itemCoding != EnumGameConfig.PointItemConsume:
			role.Msg(2, 0, GlobalPrompt.ActivityClosed)
			return
	else:
		role.Msg(2, 0, GlobalPrompt.ActivityClosed)
		return
	
	if role.ItemCnt(itemCoding) < cnt:
		return
	with TraPointItemUsed:
		role.DelItem(itemCoding, cnt)
		exchangeDict[1] = exchangeDict.get(1, 0) + cnt
	
	role.SendObj(TGExchangeData, exchangeDict)
	
	if itemCoding == EnumGameConfig.PointItemRecharge:
		role.Msg(2, 0, GlobalPrompt.RechargePointItemUsed % cnt)
	elif itemCoding == EnumGameConfig.PointItemConsume:
		role.Msg(2, 0, GlobalPrompt.ConsumePointItemUsed % cnt)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_AfterChangeDayConsumeUnbindRMB_Q, AfterConsumeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Passion_TGPointExchangeOpenPanel", "感恩节兑换商店打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Passion_TGPointExchangeClosePanel", "感恩节积分兑换商店关闭面板"), RequestClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Passion_TGRequestPointExchange", "感恩节请求积分兑换物品"), RequestPointExchange)
		
