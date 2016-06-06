#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.GlamourCoinExchangeMgr")
#===============================================================================
# 魅力币兑换Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.SysData import WorldData
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from Game.Activity.ValentineDay import GlamourCoinExchangeConfig

IDX_EXCHANGE = 2
if "_HasLoad" not in dir():
	IS_START = False
	
	GlamourCoinExchange_ExchangeRecord_S = AutoMessage.AllotMessage("GlamourCoinExchange_ExchangeRecord_S", "魅力币兑换_兑换记录同步")
	
	Tra_GlamourCoinExchange_Exchange = AutoLog.AutoTransaction("Tra_GlamourCoinExchange_Exchange", "魅力币兑换_兑换")
	
#### 活动控制  start ####
def OnStartGlamourCoinExchange(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_GlamourCoinExchange != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open GlamourCoinExchange"
		return
		
	IS_START = True

def OnEndGlamourCoinExchange(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_GlamourCoinExchange != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end GlamourCoinExchange while not start"
		return
		
	IS_START = False
	
#### 客户端请求 start 
def OnExchange(role, msg):
	'''
	魅力币兑换_请求兑换
	@param role:
	@param msg:
	'''
	global IS_START
	if not IS_START:
		return
	
	coding, cnt = msg
	cfg = GlamourCoinExchangeConfig.GlamourCoinExchange_ExchangeConfig_Dict.get(coding)
	if not cfg:
		print "GE_EXC, GlamourCoinExchange can not find coding (%s) in GlamourCoinExchange_ExchangeConfig_Dict" % coding
		return
	
	#角色等级不足
	if role.GetLevel() < cfg.needLevel:
		return
	
	#世界等级不足
	if WorldData.GetWorldLevel() < cfg.needWorldLevel:
		return
	
	if not cnt: return
	
	#兑换需要物品不够
	needCnt = cfg.needItemCnt * cnt
	if role.ItemCnt(cfg.needCoding) < needCnt:
		return
	
	if cfg.limitCnt:
		if cnt > cfg.limitCnt:
			#购买个数超过限购
			return
		exchangeRecordDict = role.GetObj(EnumObj.ValentineDayData)[IDX_EXCHANGE]
		if coding not in exchangeRecordDict:
			exchangeRecordDict[coding] = cnt
		elif exchangeRecordDict[coding] + cnt > cfg.limitCnt:
			#超过限购
			return
		else:
			exchangeRecordDict[coding] += cnt
		role.GetObj(EnumObj.ValentineDayData)[IDX_EXCHANGE] = exchangeRecordDict
		#限购的记录购买数量
		role.SendObj(GlamourCoinExchange_ExchangeRecord_S, exchangeRecordDict)
	
	with Tra_GlamourCoinExchange_Exchange:
		#发放兑换物品
		role.DelItem(cfg.needCoding, needCnt)
		role.AddItem(coding, cnt)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
	
def OnOpenPanel(role, param = None):
	'''
	请求打开新年兑不停商店
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.GlamourCoinExchange_NeedLevel:
		return
	
	role.SendObj(GlamourCoinExchange_ExchangeRecord_S, role.GetObj(EnumObj.ValentineDayData)[IDX_EXCHANGE])

def OnRoleInit(role, param):
	'''
	初始角色相关Obj的key
	'''
	valentineDayData = role.GetObj(EnumObj.ValentineDayData)
	if IDX_EXCHANGE not in valentineDayData:
		valentineDayData[IDX_EXCHANGE] = {}
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartGlamourCoinExchange)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndGlamourCoinExchange)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GlamourCoinExchange_OnExchange", "魅力币兑换_请求兑换"), OnExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GlamourCoinExchange_OnOpenPanel", "魅力币兑换_请求打开兑换面板"), OnOpenPanel)
		
