#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionChristmasExchangeMgr")
#===============================================================================
# 激情活动，圣诞大兑换 @author GaoShuai 2015
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity.PassionAct.PassionChristmasExchangeConfig import ChristmasExchange_Dict
from Game.Activity.PassionAct.PassionDefine import PassionChristmasExchange

if "_HasLoad" not in dir():
	IsStart = False
	#消息
	ChrestmasExchageData = AutoMessage.AllotMessage("ChrestmasExchageData", "圣诞大兑换数据")
	#日志
	TraChrestmasExchange = AutoLog.AutoTransaction("TraChrestmasExchange", "圣诞大兑换成功")


def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionChristmasExchange:
		return
	if IsStart:
		print 'GE_EXC, CA_PassionChristmasExchange is already start'
	IsStart = True


def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionChristmasExchange:
		return
	if not IsStart:
		print 'GE_EXC, CA_PassionChristmasExchange is already end'
	IsStart = False


def RequestChristmasExchange(role, msg):
	'''
	请求圣诞大兑换
	@param role:
	@param msg: 兑换索引
	'''
	global IsStart
	if not IsStart: return
	#消息参数是否合法
	if msg not in ChristmasExchange_Dict:
		return
	#主角等级是否满足
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	exchangeObj = ChristmasExchange_Dict.get(msg)
	if not exchangeObj:
		return
	for coding, cnt in exchangeObj.needItems:
		if role.ItemCnt(coding) < cnt:
			return
	if exchangeObj.RMB_Q != 0 and role.GetUnbindRMB_Q() < exchangeObj.RMB_Q:
		return
	#添加限购
	exchangeDict = role.GetObj(EnumObj.PassionActData).get(PassionChristmasExchange)
	if exchangeDict == None:
		print "GE_EXC, please update the PassionAct version, before start the activity."		
		return
	allLimit, dayLimit = exchangeDict.get(msg, (0, 0))
	saveAll, saveDay = 0, 0
	if exchangeObj.allLimit != 0:
		if allLimit >= exchangeObj.allLimit:
			return
		saveAll = allLimit + 1
	
	if exchangeObj.dayLimit != 0:
		if dayLimit >= exchangeObj.dayLimit:
			return
		saveDay = dayLimit + 1
	
	
	msgTip = GlobalPrompt.Item_Exchang_Tips
	
	#圣诞大兑换成功
	with TraChrestmasExchange:
		#删除物品及其他操作
		if exchangeObj.allLimit or exchangeObj.dayLimit:		
			exchangeDict[msg] = (saveAll, saveDay)
		for coding, cnt in exchangeObj.needItems:
			role.DelItem(coding, cnt)
		if exchangeObj.RMB_Q:
			role.DecUnbindRMB_Q(exchangeObj.RMB_Q)
		
		#道具
		if exchangeObj.rewards:
			coding, cnt = exchangeObj.rewards
			role.AddItem(coding, cnt)
			msgTip += GlobalPrompt.Item_Tips % (coding, cnt)
		#金币
		elif exchangeObj.Money:
			role.IncMoney(exchangeObj.Money)
			msgTip += GlobalPrompt.Money_Tips % exchangeObj.Money
		#魔晶
		elif exchangeObj.MoJing:
			role.IncBindRMB(exchangeObj.MoJing)
			msgTip += GlobalPrompt.BindRMB_Tips % exchangeObj.MoJing
		#奖励神石
		elif exchangeObj.RMB:
			role.IncUnbindRMB_S(exchangeObj.RMB)
			msgTip += GlobalPrompt.UnBindRMB_Tips % exchangeObj.RMB
	role.SendObj(ChrestmasExchageData, exchangeDict)
	role.Msg(2, 0, msgTip)


def SyncRoleData(role, param):
	global IsStart
	if not IsStart: return
	
	if role.GetObj(EnumObj.PassionActData).get(PassionChristmasExchange):
		role.SendObj(ChrestmasExchageData, role.GetObj(EnumObj.PassionActData).get(PassionChristmasExchange))


def RoleDayClear(role, param):
	global IsStart
	if not IsStart: return
	exchangeDict = role.GetObj(EnumObj.PassionActData).get(PassionChristmasExchange)
	if not exchangeDict:
		return
	for key, (allCnt, _) in exchangeDict.items():
		exchangeDict[key] = (allCnt, 0)
	role.SendObj(ChrestmasExchageData, exchangeDict)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChristmasExchange", "请求圣诞大兑换"), RequestChristmasExchange)
