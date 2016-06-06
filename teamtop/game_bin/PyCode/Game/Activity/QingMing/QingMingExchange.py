#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QingMingExchange")
#===============================================================================
# 好礼兑不停
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.SysData import WorldData
from Game.Role.Data import EnumObj
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Game.Activity.QingMing import QingMingConfig

if "_HasLoad" not in dir():
	IsStart = False
	
	SyncQingMingExchangeData = AutoMessage.AllotMessage("SyncQingMingExchangeData", "同步客户端清明节好礼兑不停数据")
	
	TraQingMingExchange = AutoLog.AutoTransaction("TraQingMingExchange", "清明节七活动好礼兑不停")


def Start(*param):
	'''
	活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingExchange != circularType:
		return
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open QingMingExchange"
		return
		
	IsStart = True
	

def End(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingExchange != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end QingMingExchange while not start"
		return
		
	IsStart = False


def RequestExchange(role, msg):
	'''
	 客户端请求积分兑换商店兑换
	 @param role:
	 @param msg: coding, cnt
	'''
	if IsStart is False:
		return
	
	coding, cnt = msg
	
	if not cnt > 0:
		return
	
	config = QingMingConfig.QingMingExchangeConfigDict.get(coding)
	if config is None:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < config.needLevel:
		return
	
	if WorldData.GetWorldLevel() < config.needWorldLevel:
		return
	
	gotDict = role.GetObj(EnumObj.QingMingData).setdefault(7, {})
	
	if config.limitCnt > 0:
		if gotDict.get(coding, 0) + cnt > config.limitCnt:
			return
		
	needItemCnt = config.needItemCnt * cnt
	
	if role.ItemCnt(config.needCoding) < needItemCnt:
		return
	
	with TraQingMingExchange:
		if role.DelItem(config.needCoding, needItemCnt) < needItemCnt:
			return
		gotDict[config.coding] = gotDict.get(config.coding, 0) + cnt
		role.AddItem(config.coding, cnt)
	
	role.SendObj(SyncQingMingExchangeData, gotDict)
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (config.coding, cnt))


def OnSyncRoleOtherData(role, param):
	if IsStart is False:
		return
	gotDict = role.GetObj(EnumObj.QingMingData).get(7, {})
	role.SendObj(SyncQingMingExchangeData, gotDict)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestQingMingExchange", "客户端清明节好礼兑换"), RequestExchange)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
