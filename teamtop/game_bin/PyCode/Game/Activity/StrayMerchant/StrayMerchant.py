#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.StrayMerchant.StrayMerchant")
#===============================================================================
# 流浪商人
#===============================================================================
import cDateTime
import cRoleMgr
import Environment
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role import Event
from Game.Role.Data import EnumInt16, EnumObj, EnumInt32, EnumDayInt8
from Game.Activity.StrayMerchant import StrayMerchantConfig

if "_HasLoad" not in dir():
	
	RANDOM_LIST_TYPE_1 = [4, 2]	#1类随机2个，2类随机4个，这个适用于系统刷新
	RANDOM_LIST_TYPE_2 = [2, 4]	#1类随机4个，2类随机2个，这个适用于手动刷新
	
	MIN_ACT_LEVEL = 30	#活动开启的等级
	FRESH_HOUR = 12	#每日刷新时间
	MAX_FRESH_TIMES = 5	#最大刷新次数
	
	BUY_PLAYER_INFO = []
	SAVE_MAX_LENGTH = 10
	#消息
	Syn_Stray_Goods = AutoMessage.AllotMessage("Syn_Stray_Goods", "同步流浪商人商品列表")
	Syn_Treasures_Goods = AutoMessage.AllotMessage("Syn_Treasures_Goods", "同步流浪商人珍品记录")
	Notice_Stray = AutoMessage.AllotMessage("Notice_Stray", "通知客户端流浪商人闪")
	#日志
	StrayMerchantCost = AutoLog.AutoTransaction("StrayMerchantCost", "流浪商人购买消耗")
	StrayMerFreshCost = AutoLog.AutoTransaction("StrayMerFreshCost", "流浪商人手动刷新消耗")
	
def FreshGoods(role, freshType):
	'''
	刷新
	@param role:
	@param freshType:1为系统刷新，2为手动刷新
	'''
	if freshType not in [1, 2]:
		return
	
	global RANDOM_LIST_TYPE_1
	global RANDOM_LIST_TYPE_2

	goodsType1_cnt = 0	#刷新1类物品数量
	goodsType2_cnt = 0	#刷新2类物品数量
	
	if freshType == 1:#根据是系统还是手动刷，刷新的物品不同
		goodsType1_cnt, goodsType2_cnt = RANDOM_LIST_TYPE_1
	else:
		goodsType1_cnt, goodsType2_cnt = RANDOM_LIST_TYPE_2
	
	#获取刷新列表
	Fresh_goods = StrayMerchantConfig.GetRandomByLevel(role, goodsType1_cnt, goodsType2_cnt)
	if not Fresh_goods:
		return
	
	goods_dict = dict((i,0) for i in Fresh_goods)
	#设置玩家的新的商品列表
	role.SetObj(EnumObj.StrayMerchantDict, goods_dict)
	if freshType == 1:#系统刷新的需要记录刷新时间
		days = cDateTime.Days()
		role.SetI16(EnumInt16.StrayFreshDays, days)
		role.SendObj(Notice_Stray, 1)
	role.SendObj(Syn_Stray_Goods, role.GetObj(EnumObj.StrayMerchantDict))

def OnSyncRoleOtherData(role, param):
	#是否更新流浪商人
	IsUpdateStray(role)

def IsUpdateStray(role):
	'''
	是否更新流浪商人
	@param role:
	'''
	#等级限制
	if role.GetLevel() < MIN_ACT_LEVEL:
		return False
	
	days = cDateTime.Days()
	lastUpdataDays = role.GetI16(EnumInt16.StrayFreshDays)
	if days <= lastUpdataDays:
		return False
	
	#判断是不是第二天
	if lastUpdataDays + 1 == days:
		#是否超过了14点
		if cDateTime.Hour() < FRESH_HOUR:
			return False
	FreshGoods(role, 1)
	return True

def OperationTick():
	for role in cRoleMgr.GetAllRole():
		if role.GetLevel() < MIN_ACT_LEVEL:
			continue
		#刷新商品
		FreshGoods(role, 1)
#============================================================================
def RequestOpenPanel(role, param):
	'''
	客户端请求打开流浪商人
	@param role:
	@param param:
	'''
	IsState = IsUpdateStray(role)
	if not IsState:
		role.SendObj(Syn_Stray_Goods, role.GetObj(EnumObj.StrayMerchantDict))
	role.SendObj(Syn_Treasures_Goods, BUY_PLAYER_INFO)

def RequestBuyGoods(role, param):
	'''
	客户端请求购买
	@param role:
	@param param:
	'''
	goodsId = param
	
	if role.GetLevel() < MIN_ACT_LEVEL:
		return
	
	goodsDict = role.GetObj(EnumObj.StrayMerchantDict)
	if goodsId not in goodsDict:
		return
	
	state = goodsDict.get(goodsId)
	if state == 1:#已经购买了
		return
	
	strayCfg = StrayMerchantConfig.STRAY_MERCHANT_DICT.get(goodsId)
	if not strayCfg:
		print "GE_EXC,can not find goodsId(%s) in RequestBuyGoods" % goodsId
		return
	
	if role.PackageEmptySize() < 1:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return

	if strayCfg.golds and role.GetMoney() < strayCfg.golds:
		return
	if strayCfg.bindRMB and role.GetBindRMB() < strayCfg.bindRMB:
		return
	if strayCfg.unbindRMB and role.GetUnbindRMB() < strayCfg.unbindRMB:
		return
	if strayCfg.needCoding:
		coding, cnt = strayCfg.needCoding
		if role.ItemCnt(coding) < cnt:
			return
	
	with StrayMerchantCost:
		if strayCfg.golds:
			role.DecMoney(strayCfg.golds)
		if strayCfg.bindRMB:
			role.DecBindRMB(strayCfg.bindRMB)
		if strayCfg.unbindRMB:
			role.DecUnbindRMB(strayCfg.unbindRMB)
		if strayCfg.needCoding:
			role.DelItem(strayCfg.needCoding[0], strayCfg.needCoding[1])
		#设置为已领取
		goodsDict[goodsId] = 1
		
		if strayCfg.rewards:
			role.AddItem(*strayCfg.rewards)
		
		global BUY_PLAYER_INFO
		if len(BUY_PLAYER_INFO) >= SAVE_MAX_LENGTH:
			del BUY_PLAYER_INFO[0]
		BUY_PLAYER_INFO.append([role.GetRoleName(), goodsId])
		
		role.SendObj(Syn_Stray_Goods, goodsDict)
		role.SendObj(Syn_Treasures_Goods, BUY_PLAYER_INFO)
		
#		if strayCfg.isTreasure:
#			cRoleMgr.Msg(2, 0, GlobalPrompt.BUY_LUCKY_MSG % (role.GetRoleName(), strayCfg.rewards[0],strayCfg.rewards[1]))
			
def RequestFreshGoods(role, param):
	'''
	客户端请求刷新流浪商人商品
	@param role:
	@param param:
	'''
	if role.GetLevel() < MIN_ACT_LEVEL:
		return
	FrishTimes = role.GetDI8(EnumDayInt8.StrayFreshCnt)
	if FrishTimes >= MAX_FRESH_TIMES:
		return
	cfg = StrayMerchantConfig.FRESH_COST_DICT.get(FrishTimes + 1)
	if not cfg:
		print "GE_EXC, can not find refreshCnt(%s) in RequestFreshGoods" % FrishTimes
		return
	if role.GetUnbindRMB() < cfg.reFreshUnbindRMB:
		return
	
	with StrayMerFreshCost:
		role.DecUnbindRMB(cfg.reFreshUnbindRMB)
		role.IncDI8(EnumDayInt8.StrayFreshCnt, 1)
		FreshGoods(role, 2)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Cron.CronDriveByMinute((2038, 1, 1), OperationTick, H = "H == 12", M = "M == 0")
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_Open_StrayPanel", "客户端请求打开流浪商人"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_Buy_StrayGoods", "客户端请求购买流浪商人商品"), RequestBuyGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_Fresh_StrayGoods", "客户端请求刷新流浪商人商品"), RequestFreshGoods)
	