#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheExchangeMgr")
#===============================================================================
# 兑换由我定 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from Game.Activity.WangZheGongCe import WangZheExchangeConfig

IDX_EXCHANGE = 2

if "_HasLoad" not in dir():
	IS_START = False
	
	#格式 ｛coding:cnt,｝
	WangZheExchange_ExchangeRecord_S = AutoMessage.AllotMessage("WangZheExchange_ExchangeRecord_S", "兑换由我定_兑换记录同步")
	
	Tra_WangZheExchange_Exchange = AutoLog.AutoTransaction("Tra_WangZheExchange_Exchange", "兑换由我定_兑换")
	
#### 活动控制 start
def OnStartWangZheExchange(*param):
	'''
	兑换由我定_开启
	'''
	_, circularType = param
	if CircularDefine.CA_WangZheExchange != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open WangZheExchange"
		return 
	
	IS_START = True

def OnEndWangZheExchange(*param):
	'''
	兑换由我定_结束
	'''
	_, circularType = param
	if CircularDefine.CA_WangZheExchange != circularType:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC,end WangZheExchange while not start"
	IS_START = False
	
def OnExchange(role, msg):
	'''
	请求兑换道具
	@param role:
	@param msg:
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	targetCoding, targetCnt = msg
	if not targetCoding or targetCnt < 1:
		return
	
	exchangeCfg = WangZheExchangeConfig.WZE_GoodsConfig_Dict.get(targetCoding)
	if not exchangeCfg:
		return
	
	#角色等级
	if roleLevel < exchangeCfg.needLevel:
		return
	
	#兑换资本判断
	if role.ItemCnt(exchangeCfg.needCoding) < targetCnt * exchangeCfg.needItemCnt:
		return
	
	#限购判断
	if exchangeCfg.isLimit:
		exchangeRecordDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_EXCHANGE]
		exchangedCnt = exchangeRecordDict.get(targetCoding, 0)
		if exchangedCnt + targetCnt > exchangeCfg.limitCnt:
			return
	
	prompt = GlobalPrompt.WZE_Tips_Head
	with Tra_WangZheExchange_Exchange:
		#限购记录
		if exchangeCfg.isLimit:
			exchangeRecordDict[targetCoding] = (exchangedCnt + targetCnt)
		#扣除兑换所需道具
		role.DelItem(exchangeCfg.needCoding, (exchangeCfg.needItemCnt * targetCnt))
		#获得物品
		role.AddItem(targetCoding, targetCnt)
		prompt += GlobalPrompt.Item_Tips % (targetCoding, targetCnt)
	
	#获得提示
	role.Msg(2, 0, prompt)
	#同步最新兑换记录
	if exchangeCfg.isLimit:
		role.SendObj(WangZheExchange_ExchangeRecord_S, exchangeRecordDict)

def OnInitRole(role, param = None):
	'''
	角色初始化相关key
	'''
	wangZheGongCeData = role.GetObj(EnumObj.WangZheGongCe)
	if IDX_EXCHANGE not in wangZheGongCeData:
		wangZheGongCeData[IDX_EXCHANGE] = {}

def OnSyncOtherData(role, param = None):
	'''
	角色上线同步相关数据
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	role.SendObj(WangZheExchange_ExchangeRecord_S, role.GetObj(EnumObj.WangZheGongCe)[IDX_EXCHANGE])

def AfterLevelUp(role, param = None):
	'''
	玩家升级 解锁玩法 同步相关数据
	'''
	if not IS_START:
		return
	
	if role.GetLevel() != EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	role.SendObj(WangZheExchange_ExchangeRecord_S, role.GetObj(EnumObj.WangZheGongCe)[IDX_EXCHANGE])
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
	
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartWangZheExchange)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndWangZheExchange)

		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheExchange_OnExchange", "兑换由我定_请求兑换"), OnExchange)
