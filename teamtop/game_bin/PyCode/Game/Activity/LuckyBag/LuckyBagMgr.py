#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LuckyBag.LuckyBagMgr")
#===============================================================================
# 福袋，这个仅繁体版有
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import Environment
import cComplexServer
from Util import Time
from Game.Persistence import Contain
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role import Event
from Game.Activity.LuckyBag import LuckyBagConfig

if "_HasLoad" not in dir():
	
	AvailableBagDict = {}			#可以开启的福袋的coding统统放到这里,{coding:endtime}
	
	#消息
	LuckyBag_MakeAvailable = AutoMessage.AllotMessage("LuckyBagMgr_MakeAvailable", "某个福袋活动开启")
	LuckyBag_MakeUnavailable = AutoMessage.AllotMessage('LuckyBagMgr_MakeUnavailable', "某个福袋活动结束")
	LuckyBag_AllAvailableData = AutoMessage.AllotMessage('LuckyBag_AllAvailableData', "同步所有福袋活动的数据")
	
	LuckyBag_SyncRedHandList = AutoMessage.AllotMessage('LuckyBag_SyncRedHandList', "同步所有红手榜数据")
	LuckyBag_SyncPersonalData = AutoMessage.AllotMessage('LuckyBag_SyncPersonalData', "同步玩家购买的次数 ")
	
	#日志
	Tra_LuckyBag_Buy = AutoLog.AutoTransaction("Tra_LuckyBag_Buy", "购买福袋 ")

#============= 活动控制 ====================
def Initialize():	
	'''
	初始化活动tick
	'''
	nowSeconds = cDateTime.Seconds()
	for LB_Coding, config in LuckyBagConfig.LuckyBag_Config_Dict.iteritems():
		beginSeconds = Time.DateTime2UnitTime(config.BeginTime)
		endSeconds = Time.DateTime2UnitTime(config.EndTime)
		
		if beginSeconds <= nowSeconds < endSeconds:
			#开启 并注册结束tick
			LB_Start(None, (LB_Coding, endSeconds))
			cComplexServer.RegTick(endSeconds - nowSeconds, LB_End, LB_Coding)
			
		elif nowSeconds < beginSeconds:
			#注册开启和结束的tick
			cComplexServer.RegTick(beginSeconds - nowSeconds, LB_Start, (LB_Coding, endSeconds))
			cComplexServer.RegTick(endSeconds - nowSeconds, LB_End, LB_Coding)


def LB_Start(callargv, regparam):
	'''
	使某个福袋变得available
	'''
	LB_Coding, endSeconds = regparam
	global AvailableBagDict
	if LB_Coding in AvailableBagDict:
		return
	AvailableBagDict[LB_Coding] = endSeconds
	#打包并广播消息
	cNetMessage.PackPyMsg(LuckyBag_MakeAvailable, (LB_Coding, endSeconds))
	cRoleMgr.BroadMsg()

def LB_End(callargv, regparam):
	'''
	使某个福袋变得unavailable
	'''
	LB_Coding = regparam
	
	global AvailableBagDict
	if not LB_Coding in AvailableBagDict:
		return
	del AvailableBagDict[LB_Coding]
	#打包并广播消息
	cNetMessage.PackPyMsg(LuckyBag_MakeUnavailable, LB_Coding)
	cRoleMgr.BroadMsg()

def RequestBuyLuckyBag(role, msg):
	'''
	客户端请求购买福袋
	@param role:
	@param msg:
	'''
	if not Environment.EnvIsFT():
		return	
	bag_coding, cnt = msg
	#这个福袋
	if not bag_coding in AvailableBagDict:
		return
	#背包满了
	if role.PackageEmptySize() < cnt:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	bag_cfg = LuckyBagConfig.LuckyBag_Config_Dict.get(bag_coding)
	
	if not bag_cfg:
		return
	
	#玩家等级不满足购买福袋的等级限制
	if role.GetLevel() < bag_cfg.NeedLevel:
		return
	
	roleID = role.GetRoleID()
	roleBuyDict = LuckyBagCntDict.setdefault(roleID, {})
	roleBuyCnt = roleBuyDict.setdefault(bag_coding, 0)
	#超过了购买次数限制 
	if not roleBuyCnt < bag_cfg.BuyLimitCnt:
		return
	
	totalPrice = bag_cfg.Price * cnt
	if role.GetUnbindRMB_Q() < totalPrice:
		return
	
	with Tra_LuckyBag_Buy:
		#扣神石
		role.DecUnbindRMB_Q(totalPrice)
		#增加购买次数
		roleBuyDict[bag_coding] += cnt
		LuckyBagCntDict.HasChange()
		#日志记录购买福袋的个数
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveBuyLuckyBag, cnt)
		#发放福袋
		role.AddItem(bag_coding, cnt)
		
	role.SendObj(LuckyBag_SyncPersonalData, roleBuyDict[bag_coding])
	role.Msg(2, 0, GlobalPrompt.Item_Tips % (bag_coding, cnt))

def RequestOpenLuckyBagPanel(role, msg):
	'''
	客户端请求购买福袋
	@param role:
	@param msg:
	'''	
	if not Environment.EnvIsFT():
		return	
	bag_code = msg
	if not bag_code in AvailableBagDict:
		return
	redHandList = LuckyBagDict.setdefault(bag_code, [])
	roleID = role.GetRoleID()
	roleBuydDict = LuckyBagCntDict.setdefault(roleID, {})
	roleBuyCnt = roleBuydDict.setdefault(bag_code, 0)
	
	
	role.SendObj(LuckyBag_SyncRedHandList, redHandList)
	role.SendObj(LuckyBag_SyncPersonalData, roleBuyCnt)

def SyncRoleOtherData(role, param):
	'''
	客户端请求购买福袋
	@param role:
	@param param:
	'''	
	#角色登录同步数据
	if not Environment.EnvIsFT():
		return
	global AvailableBagDict
	role.SendObj(LuckyBag_AllAvailableData, AvailableBagDict)


def CallAfterNewDay():
	global LuckyBagCntDict
	LuckyBagCntDict.clear()
	

if "_HasLoad" not in dir():
	#仅繁体有这些内容 
	if Environment.EnvIsFT():
		if (Environment.HasLogic or Environment.HasWeb) and not Environment.IsCross:
			#红手榜数据{chestCoding:rewardinfo}
			LuckyBagDict = Contain.Dict("LuckyBagDict", (2038, 1, 1), None, None, isSaveBig=True)
			#玩家每日购买福袋的数据{roleID:{chestCode:cnt}}
			LuckyBagCntDict = Contain.Dict("LuckyBagCntDict", (2038, 1, 1), None, None, isSaveBig=True)
		
		if Environment.HasLogic and not Environment.IsCross:
			Initialize()
			cComplexServer.RegAfterNewDayCallFunction(CallAfterNewDay)

		if Environment.HasLogic and not Environment.IsCross:
			Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestBuyLuckyBag", "客户端请求购买福袋"), RequestBuyLuckyBag)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenLuckyBagPanel", "客户端请求打开福袋面板"), RequestOpenLuckyBagPanel)
