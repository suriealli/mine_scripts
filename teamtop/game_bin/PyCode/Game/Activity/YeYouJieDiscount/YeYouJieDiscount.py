#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.YeYouJieDiscount.YeYouJieDiscount")
#===============================================================================
# 页游节折扣汇
#===============================================================================
import cRoleMgr
import Environment
from Util import Random
from Game.Role import Event
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumDayInt8
from Game.Activity.YeYouJieDiscount import YeYouJieDiscountConfig

if "_HasLoad" not in dir():
	StoreCnt = 6
	NeedLevel = 30
	IsStart = False
	#日志
	TraYeYouJieDiscountExchange = AutoLog.AutoTransaction("TraYeYouJieDiscountExchange", "页游节折扣汇交易")
	TraYeYouJieDiscountRefresh = AutoLog.AutoTransaction("TraYeYouJieDiscountRefresh", "页游节折扣汇刷新商品")
	#消息
	SyncYeYouJieDiscountData = AutoMessage.AllotMessage("SyncYeYouJieDiscountData", "同步页游节折扣汇数据")


def Start(callargv, param):
	'''
	开启活动
	'''
	if param != CircularDefine.CA_YeYouJieDiscount:
		return
	global IsStart
	if IsStart:
		print 'GE_EXC, YeYouJieDiscount is already Start'
	IsStart = True


def End(callargv, param):
	'''
	关闭活动
	'''
	if param != CircularDefine.CA_YeYouJieDiscount:
		return
	global IsStart
	if not IsStart:
		print 'GE_EXC, YeYouJieDiscount is already End'
	IsStart = False


def GetRandomItemList(role):
	'''
	获取随机商品列表，这里动态的创建random rate因为每次的条件都会发生变化
	考虑到刷新的次数并不会很多，认为这样是可以接受的
	'''
	roleLevel = role.GetLevel()
	
	randomList = YeYouJieDiscountConfig.LevelRangeRandomDict.get(roleLevel)
	if randomList is None:
		print "GE_EXC,error while randomList = YeYouJieDiscountConfig.LevelRangeRandomDict.get(roleLevel)(%s)" % roleLevel
		return None
	
	YDG = YeYouJieDiscountConfig.DiscountConfigDict.get
	ranmRate = Random.RandomRate()
	RA = ranmRate.AddRandomItem
	
	for goodId, rate in randomList:
		config = YDG(goodId)
		if config is None:
			print "GE_EXC,error while role(%s) get random goodId in YeYouJieDiscount, no such goodID (%s) " % (role.GetRoleID(), goodId)
			return None
		buyCnt = role.GetObj(EnumObj.YeYouJieWarmup).get(2, {}).get(goodId, 0)
		if config.limitCnt > 0:
			if buyCnt >= config.limitCnt:
				continue
		RA(rate, goodId)
	return ranmRate.RandomMany(StoreCnt)


def DoRefresh(role):
	'''
	真正的刷新商品
	'''
	goodList = GetRandomItemList(role)
	if goodList is None:
		return
	goodDict = {}
	for goodId in goodList:
		goodDict[goodId] = True
	role.GetObj(EnumObj.YeYouJieWarmup)[3] = goodDict


def RequestExchange(role, msg):
	'''
	请求交易
	'''
	if IsStart is False:
		return
	if role.GetLevel() < NeedLevel:
		return
	
	goodId = msg
	goodDict = role.GetObj(EnumObj.YeYouJieWarmup).setdefault(3, {})
	
	if not goodDict.get(goodId):
		#商品字典中不存在此商品或者是存在此商品但是设置了不可购买
		return
	
	config = YeYouJieDiscountConfig.DiscountConfigDict.get(goodId)
	if config is None:
		return
	
	#购买次数
	buyCntDict = role.GetObj(EnumObj.YeYouJieWarmup).setdefault(2, {})
	buyCnt = buyCntDict.get(goodId, 0)
	if config.limitCnt > 0:
		if buyCnt + 1 > config.limitCnt:
			return
	
	#限定充值神石
	if config.RMBType == 1:
		roleDecUnbindRMB = role.DecUnbindRMB_Q
		if role.GetUnbindRMB_Q() < config.needUnbindRMB:
			return
	#不限定神石
	elif config.RMBType == 0:
		roleDecUnbindRMB = role.DecUnbindRMB
		if role.GetUnbindRMB() < config.needUnbindRMB:
			return
	#限定不明
	else:
		return
	
	with TraYeYouJieDiscountExchange:
		#扣神石
		roleDecUnbindRMB(config.needUnbindRMB)
		#增加购买次数
		buyCntDict[goodId] = buyCntDict.get(goodId, 0) + 1
		#物品id设置为不可购买（已购买)
		goodDict[goodId] = False
		role.AddItem(*config.item)
	
	goodDict = role.GetObj(EnumObj.YeYouJieWarmup).get(3, {})
	buyDict = role.GetObj(EnumObj.YeYouJieWarmup).get(2, {})
	role.SendObj(SyncYeYouJieDiscountData, [buyDict, goodDict])
	
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % config.item)


def RequestRefesh(role, msg):
	'''
	请求刷新商品
	'''
	if IsStart is False:
		return
	
	if role.GetLevel() < NeedLevel:
		return
	
	oldCnt = role.GetDI8(EnumDayInt8.YeYouJieDiscountRefreshCnt)
	nowCnt = oldCnt + 1
	
	#超过最大次数的话都按照最大次数来计算
	maxCnt = max(YeYouJieDiscountConfig.RefreshConfigDict.keys())
	if nowCnt > maxCnt:
		nowCnt = maxCnt
		
	price = YeYouJieDiscountConfig.RefreshConfigDict.get(nowCnt)
	if price is None:
		return
	
	#玩家的神石不够
	if role.GetUnbindRMB() < price:
		return
	
	with TraYeYouJieDiscountRefresh:
		if nowCnt < 125:
			role.IncDI8(EnumDayInt8.YeYouJieDiscountRefreshCnt, 1)
		if price > 0:
			role.DecUnbindRMB(price)
			
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveYeYouJieDiscountRefresh, price)
		DoRefresh(role)
	
	goodDict = role.GetObj(EnumObj.YeYouJieWarmup).get(3, {})
	buyDict = role.GetObj(EnumObj.YeYouJieWarmup).get(2, {})
	role.SendObj(SyncYeYouJieDiscountData, [buyDict, goodDict])
	role.Msg(2, 0, GlobalPrompt.YeYouJieDiscountRefreshTips % price)


def RequestOpenPanel(role, msg):
	'''
	客户端请求打开面板
	'''
	if IsStart is False:
		return
	if role.GetLevel() < NeedLevel:
		return
	
	#更新当天的兼容
	goodDict = role.GetObj(EnumObj.YeYouJieWarmup).get(3, {})
	if not goodDict:
		DoRefresh(role)
		
	goodDict = role.GetObj(EnumObj.YeYouJieWarmup).get(3, {})
	buyDict = role.GetObj(EnumObj.YeYouJieWarmup).get(2, {})
	role.SendObj(SyncYeYouJieDiscountData, [buyDict, goodDict])


def RoleDayClear(role, param):
	'''
	角色每日清理
	'''
	if IsStart is False:
		return
	if role.GetLevel() < NeedLevel:
		return
	
	DoRefresh(role)
	goodDict = role.GetObj(EnumObj.YeYouJieWarmup).get(3, {})	
	buyDict = role.GetObj(EnumObj.YeYouJieWarmup).get(2, {})
	role.SendObj(SyncYeYouJieDiscountData, [buyDict, goodDict])


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		if Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsQQUnion():
			Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
			if not Environment.IsCross:
				Event.RegEvent(Event.Eve_StartCircularActive, Start)
				Event.RegEvent(Event.Eve_EndCircularActive, End)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenPanelYeYouJieDiscount", "客户端请求打开面板_页游节折扣汇"), RequestOpenPanel)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestExchangeYeYouJieDiscount", "客户端请求购物_页游节折扣汇"), RequestExchange)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestRefeshYeYouJieDiscount", "客户端请求刷新商品_页游节折扣汇"), RequestRefesh)
			
