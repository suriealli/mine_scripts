#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionMarketMgr")
#===============================================================================
# 激情卖场 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Util import Random
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumDayInt8
from Game.Activity.PassionAct import PassionMarketConfig, PassionDefine


if "_HasLoad" not in dir():
	IS_START = False
	#日志
	Tra_PassionMarket_BuyGoods = AutoLog.AutoTransaction("Tra_PassionMarket_BuyGoods", "激情卖场_购买折扣商品")
	Tra_PassionMarket_RefreshGoods = AutoLog.AutoTransaction("Tra_PassionMarket_RefreshGoods", "激情卖场_刷新折扣商品")

	#格式 [buyDict, goodDict] --> [购买记录, 货架商品]	
	PassionMarket_Data_S = AutoMessage.AllotMessage("PassionMarket_Data_S", "激情卖场_数据同步")


#活动控制start
def OnStartPassionMarket(callargv, param):
	'''
	开启活动
	'''
	if param != CircularDefine.CA_PassionMarket:
		return
	global IS_START
	if IS_START:
		print 'GE_EXC, PassionMarket is already Start'
	IS_START = True
	

def OnEndPassionMarket(callargv, param):
	'''
	关闭活动
	'''
	if param != CircularDefine.CA_PassionMarket:
		return
	global IS_START
	if not IS_START:
		print 'GE_EXC, PassionMarket is already End'
	IS_START = False


#客户端请求 start
def OnOpenPanel(role, msg = None):
	'''
	激情卖场_请求打开面板
	'''
	if IS_START is False:
		return
	if role.GetLevel() < EnumGameConfig.PassionMarket_NeedLevel:
		return
	
	#更新当天的兼容
	goodDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMarket_GOODS, {})
	if not goodDict:
		DoRefresh(role)
		
	goodDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMarket_GOODS, {})
	buyDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMarket_BUYRECORD, {})
	role.SendObj(PassionMarket_Data_S, [buyDict, goodDict])

def OnBuyGoods(role, msg):
	'''
	激情卖场_请求购买商品
	'''
	if IS_START is False:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionMarket_NeedLevel:
		return
	
	goodId = msg
	goodDict = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMarket_GOODS]
	if goodId not in goodDict or goodDict[goodId] is not True:
		#商品字典中不存在此商品或者是存在此商品但是设置了不可购买
		return
	
	config = PassionMarketConfig.DiscountConfigDict.get(goodId)
	if config is None:
		return
	
	#购买次数
	buyCntDict = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMarket_BUYRECORD]
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
	
	
	prompt = GlobalPrompt.PassionMarket_Tips_Head
	with Tra_PassionMarket_BuyGoods:
		#扣神石
		roleDecUnbindRMB(config.needUnbindRMB)
		#增加购买次数
		buyCntDict[goodId] = buyCntDict.get(goodId, 0) + 1
		#物品id设置为不可购买（已购买)
		goodDict[goodId] = False
		#购买获得
		coding, cnt = config.item
		role.AddItem(coding, cnt)
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#购买提示
	role.Msg(2, 0, prompt)
	#同步最新记录数据和货架商品状态
	role.SendObj(PassionMarket_Data_S, [buyCntDict, goodDict])

def OnRefreshGoods(role, msg = None):
	'''
	激情卖场_请求刷新商品
	'''
	if IS_START is False:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionMarket_NeedLevel:
		return
	
	nowCnt = role.GetDI8(EnumDayInt8.PassionMarketRefreshCnt) + 1
	
	#超过最大次数的话都按照最大次数来计算
	if nowCnt > PassionMarketConfig.MAXREFRESHCNT:
		nowCnt = PassionMarketConfig.MAXREFRESHCNT
		
	price = PassionMarketConfig.RefreshConfigDict.get(nowCnt)
	if price is None:
		return
	
	#玩家的神石不够
	if role.GetUnbindRMB() < price:
		return
	
	with Tra_PassionMarket_RefreshGoods:
		if nowCnt < 125:
			role.IncDI8(EnumDayInt8.PassionMarketRefreshCnt, 1)
		if price > 0:
			role.DecUnbindRMB(price)
			
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePassionMarketRefresh, price)
		DoRefresh(role)
	#属性成功提示
	role.Msg(2, 0, GlobalPrompt.PassionMarket_Tips_Refresh % price)
	#最新数据同步
	goodDict = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMarket_GOODS]
	buyDict = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMarket_BUYRECORD]
	role.SendObj(PassionMarket_Data_S, [buyDict, goodDict])


# 辅助 start
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
	role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMarket_GOODS] = goodDict

def GetRandomItemList(role):
	'''
	获取随机商品列表，这里动态的创建random rate因为每次的条件都会发生变化
	考虑到刷新的次数并不会很多，认为这样是可以接受的
	'''
	roleLevel = role.GetLevel()	
	randomList = PassionMarketConfig.LevelRangeRandomDict.get(roleLevel)
	if randomList is None:
		print "GE_EXC,error while randomList = PassionMarketConfig.LevelRangeRandomDict.get(roleLevel)(%s)" % roleLevel
		return None
	
	YDG = PassionMarketConfig.DiscountConfigDict.get
	ranmRate = Random.RandomRate()
	RA = ranmRate.AddRandomItem
	
	for goodId, rate in randomList:
		config = YDG(goodId)
		if config is None:
			print "GE_EXC,error while role(%s) get random goodId in PassionMarket, no such goodID (%s) " % (role.GetRoleID(), goodId)
			return None
		buyCnt = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMarket_BUYRECORD, {}).get(goodId, 0)
		if config.limitCnt > 0:
			if buyCnt >= config.limitCnt:
				continue
		RA(rate, goodId)
		
	return ranmRate.RandomMany(EnumGameConfig.PassionMarket_RefreshCnt)


#事件 start
def OnInitRole(role, param = None):
	'''
	角色初始化相关key
	'''
	passionActData = role.GetObj(EnumObj.PassionActData)
	if PassionDefine.PassionMarket_BUYRECORD not in passionActData:
		passionActData[PassionDefine.PassionMarket_BUYRECORD] = {}
	if PassionDefine.PassionMarket_GOODS not in passionActData:
		passionActData[PassionDefine.PassionMarket_GOODS] = {}
	
def RoleDayClear(role, param):
	'''
	角色每日清理
	'''
	if IS_START is False:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionMarket_NeedLevel:
		return
	
	DoRefresh(role)
	buyDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMarket_BUYRECORD, {})
	goodDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionMarket_GOODS, {})	
	role.SendObj(PassionMarket_Data_S, [buyDict, goodDict])
	

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartPassionMarket)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndPassionMarket)
				
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionMarket_OnOpenPanel", "激情卖场_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionMarket_OnBuyGoods", "激情卖场_请求购买商品"), OnBuyGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionMarket_OnRefreshGoods", "激情卖场_请求刷新商品"), OnRefreshGoods)
