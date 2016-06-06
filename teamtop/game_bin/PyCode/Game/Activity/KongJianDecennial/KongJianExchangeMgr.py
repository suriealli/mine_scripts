#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianExchangeMgr")
#===============================================================================
# 周年纪念币 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumDayInt8
from Game.Activity.KongJianDecennial import KongJianExchangeConfig,\
	KongJianRechargeConfig

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_KongJianExchange_ExchangeReward = AutoLog.AutoTransaction("Tra_KongJianExchange_ExchangeReward", "周年纪念币_兑换奖励")
	
	#格式set([1,2])
	KongJianExchange_ExchangeRecord_S = AutoMessage.AllotMessage("KongJianExchange_ExchangeRecord_S", "周年纪念币_兑换记录同步")

#### 活动控制  start ####
def OnStartKongJianExchange(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianExchange != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open KongJianExchange"
		return
		
	IS_START = True

def OnEndKongJianExchange(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianExchange != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end KongJianExchange while not start"
		return
		
	IS_START = False
	
#客户端请求 start
def OnExchangeReward(role, msg):
	'''
	周年纪念币_请求兑换奖励
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.KJD_NeedLevel:
		return
	
	if not role.IsKongJianDecennialRole():
		return
	
	exchangeIndex = msg
	exchangeRecordDict = role.GetObj(EnumObj.KongJianDecennial)[2]
	if exchangeIndex in exchangeRecordDict:
		return
	
	levelRangeId = KongJianRechargeConfig.GetLevelRangeIdByLevel(roleLevel)
	exchangeCfg = KongJianExchangeConfig.GetCfgByIndexAndLevel(exchangeIndex, roleLevel)
	if not exchangeCfg:
		return
	
	needExchangeCoin = exchangeCfg.needExchangeCoin
	if role.GetDI8(EnumDayInt8.KongJianDecennialExchangeCoin) < needExchangeCoin:
		return
	
	prompt = GlobalPrompt.KJD_Tips_Head
	with Tra_KongJianExchange_ExchangeReward:
		#领奖记录
		exchangeRecordDict[exchangeIndex] = levelRangeId
		#扣除周年纪念币
		role.DecDI8(EnumDayInt8.KongJianDecennialExchangeCoin, needExchangeCoin)
		#奖励魔晶
		rewardBindRMB = exchangeCfg.rewardBindRMB
		if rewardBindRMB > 0:
			role.IncBindRMB(rewardBindRMB)
			prompt += GlobalPrompt.BindRMB_Tips % rewardBindRMB
		#奖励金币
		rewardMoney = exchangeCfg.rewardMoney
		if rewardMoney > 0:
			role.IncMoney(rewardMoney)
			prompt += GlobalPrompt.Money_Tips % rewardMoney
		#奖励纪念币
		rewardExchangeCoin = exchangeCfg.rewardExchangeCoin
		if rewardExchangeCoin > 0:
			prompt += GlobalPrompt.KJDExchangeCoin_Tips % rewardExchangeCoin
			role.IncDI8(EnumDayInt8.KongJianDecennialExchangeCoin, rewardExchangeCoin)
		#奖励道具
		for coding, cnt in exchangeCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#获得提示
	role.Msg(2, 0, prompt)
	#同步领奖记录
	role.SendObj(KongJianExchange_ExchangeRecord_S, exchangeRecordDict)

#事件 start
def OnInitRole(role, param = None):
	'''
	初始化objkey
	'''
	KongJianDecennialData = role.GetObj(EnumObj.KongJianDecennial)
	if 2 not in KongJianDecennialData:
		KongJianDecennialData[2] = {}

def OnSyncRoleOtherData(role, param = None):
	'''
	角色上线 同步活动状态 
	'''
	if not IS_START:
		return
	
	if not role.IsKongJianDecennialRole():
		return
	
	#同步领奖记录
	role.SendObj(KongJianExchange_ExchangeRecord_S, role.GetObj(EnumObj.KongJianDecennial)[2])

def OnRoleDayClear(role, calArgv = None, regparam = None):
	'''
	跨天清理
	'''
	#清空充值领奖记录
	KongJianDecennialData = role.GetObj(EnumObj.KongJianDecennial)
	exchangeRecordDict = KongJianDecennialData[2]
	exchangeRecordDict.clear()
	
	#同步领奖记录
	if role.IsKongJianDecennialRole():
		role.SendObj(KongJianExchange_ExchangeRecord_S, exchangeRecordDict)

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop):
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartKongJianExchange)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndKongJianExchange)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KongJianExchange_OnExchangeReward", "周年纪念币_请求兑换奖励"), OnExchangeReward)
