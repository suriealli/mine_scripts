#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActD12OptionShopMgr")
#===============================================================================
# 双十二自选商城
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from Game.Activity.PassionAct.PassionDefine import PassionD12Shop
from Game.Activity.PassionAct.PassionActD12OptionShopConfig import D12ShopConfig_Dict,D12ShopDisCountConfig

if "_HasLoad" not in dir():
	IsOpen = False

	NeedRoleLevel = 30	#活动需要角色等级

	#日志
	D12ShopBalance = AutoLog.AutoTransaction("D12ShopBalance", "双十二自选商城结算")
	#消息
	D12ShopData = AutoMessage.AllotMessage("D12ShopData", "双十二自选商城数据")

def StartActivity(param1, param2):
	if param2 != CircularDefine.CA_PassionD12Shop:
		return
	
	global IsOpen
	if IsOpen:
		print "GE_EXC, D12Shop is already open"
		return
	
	IsOpen = True

def EndActivity(param1, param2):
	if param2 != CircularDefine.CA_PassionD12Shop:
		return
	
	global IsOpen
	if not IsOpen:
		print "GE_EXC, D12Shop is already close"
		return
	
	IsOpen = False

def Balance(role,msg):
	'''
	购物车结算
	'''
	
	global IsOpen
	if not IsOpen:
		return
	#需要购物的商品{goods : cnt}列表
	if not msg:
		return
	goodsDict = msg
	
	limitDict 		 = role.GetObj(EnumObj.PassionActData)[PassionD12Shop][1]	#活动期间限购
	limitDayDict	 = role.GetObj(EnumObj.PassionActData)[PassionD12Shop][2]	#每日限购
	
	totalNeedUnbindRMB = 0		#需要的神石总数

	buylimitDict = {}
	daybuylimitDict = {}

	goodCfgs = []
	flag_RMB_Q = False   #是否消耗充值神石
	for tradeId, cnt in goodsDict.iteritems():
		if cnt < 1:
			return

		cfg = D12ShopConfig_Dict.get(tradeId)
		if not cfg:
			return
		#购买等级不符
		if role.GetLevel() < cfg.needLevel[0] or role.GetLevel() > cfg.needLevel[1]:
			return

		#活动内限购
		if cfg.totallimitCnt:
			buylimitDict[cfg.index] = nowtotalcnt = buylimitDict.get(cfg.index, 0) + cnt
			if cfg.totallimitCnt < limitDict.get(cfg.index, 0) + nowtotalcnt:
				return
			
		#每日限购
		if cfg.daylimitCnt:
			daybuylimitDict[cfg.index] = nowtotalcnt = daybuylimitDict.get(cfg.index, 0) + cnt
			if cfg.daylimitCnt < limitDayDict.get(cfg.index, 0) + nowtotalcnt:
				return
		
		goodCfgs.append((cfg, cnt))
		
		if cfg.isRMB_Q:
			flag_RMB_Q = True
		totalNeedUnbindRMB += cfg.needRMB * cnt
	
	
	#打折
	discountCfg = D12ShopDisCountConfig.GetDiscount(totalNeedUnbindRMB)
	if discountCfg:
		totalNeedUnbindRMB = (totalNeedUnbindRMB * discountCfg.discount + 99) / 100
	
	
	if flag_RMB_Q:
		if role.GetUnbindRMB_Q() < totalNeedUnbindRMB:
			return
	else:
		if role.GetUnbindRMB() < totalNeedUnbindRMB:
			return
	
	#增加限购数量
	if buylimitDict:
		for tradeId, cnt in buylimitDict.iteritems():
			limitDict[tradeId] = limitDict.get(tradeId, 0) + cnt
	
	if daybuylimitDict:
		for tradeId, cnt in daybuylimitDict.iteritems():
			limitDayDict[tradeId] = limitDayDict.get(tradeId, 0) + cnt
	
	with D12ShopBalance:
		#扣钱
		if flag_RMB_Q:
			role.DecUnbindRMB_Q(totalNeedUnbindRMB)
		else:
			role.DecUnbindRMB(totalNeedUnbindRMB)

		for cfg, cnt in goodCfgs:
			role.AddItem(cfg.items[0], cfg.items[1] * cnt)
		
	role.SendObj(D12ShopData, {1:limitDict, 2:limitDayDict})

	
def OpenPane(role,msg):
	global IsOpen
	if not IsOpen:
		return
	if role.GetLevel() < NeedRoleLevel:
		return
	
	role.SendObj(D12ShopData, role.GetObj(EnumObj.PassionActData)[PassionD12Shop])
	
def RoleDayClear(role, param):
	##清理每日限购数量
	global IsOpen
	if not IsOpen: return
	if role.GetLevel() < NeedRoleLevel:
		return
	role.GetObj(EnumObj.PassionActData)[PassionD12Shop][2] = {}


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, StartActivity)
		Event.RegEvent(Event.Eve_EndCircularActive, EndActivity)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionActD12Shop_RequestOpenPane", "请求打开自选商城面板"), OpenPane)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionActD12Shop_RequestBalance", "请求购物车结算"), Balance)
