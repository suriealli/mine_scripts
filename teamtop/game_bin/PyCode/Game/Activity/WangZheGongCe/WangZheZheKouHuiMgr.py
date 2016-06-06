#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheZheKouHuiMgr")
#===============================================================================
# 公测折扣汇 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Util import Random
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumDayInt8, EnumInt32
from Game.Activity.WangZheGongCe import WangZheZheKouHuiConfig


IDX_BUYRECORD = 4
IDX_GOODS = 5

if "_HasLoad" not in dir():
	IS_START = False
	#日志
	Tra_WangZheZheKouHui_BuyGoods = AutoLog.AutoTransaction("Tra_WangZheZheKouHui_BuyGoods", "公测折扣汇_购买折扣商品")
	Tra_WangZheZheKouHui_RefreshGoods = AutoLog.AutoTransaction("Tra_WangZheZheKouHui_RefreshGoods", "公测折扣汇_刷新折扣商品")

	#格式 [buyDict, goodDict] --> [购买记录, 货架商品]	
	WangZheZheKouHui_Data_S = AutoMessage.AllotMessage("WangZheZheKouHui_Data_S", "公测折扣汇_数据同步")


#活动控制start
def OnStartWangZheZheKouHui(callargv, param):
	'''
	开启活动
	'''
	if param != CircularDefine.CA_WangZheZheKouHui:
		return
	global IS_START
	if IS_START:
		print 'GE_EXC, WangZheZheKouHui is already Start'
	IS_START = True

def OnEndWangZheZheKouHui(callargv, param):
	'''
	关闭活动
	'''
	if param != CircularDefine.CA_WangZheZheKouHui:
		return
	global IS_START
	if not IS_START:
		print 'GE_EXC, WangZheZheKouHui is already End'
	IS_START = False


#客户端请求 start
def OnOpenPanel(role, msg = None):
	'''
	公测折扣汇_请求打开面板
	'''
	if IS_START is False:
		return
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	#更新当天的兼容
	goodDict = role.GetObj(EnumObj.WangZheGongCe).get(IDX_GOODS, {})
	if not goodDict:
		DoRefresh(role)
		
	goodDict = role.GetObj(EnumObj.WangZheGongCe).get(IDX_GOODS, {})
	buyDict = role.GetObj(EnumObj.WangZheGongCe).get(IDX_BUYRECORD, {})
	role.SendObj(WangZheZheKouHui_Data_S, [buyDict, goodDict])

def OnBuyGoods(role, msg):
	'''
	公测折扣汇_请求购买商品
	'''
	if IS_START is False:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	goodId = msg
#	print "GE_EXC, type of goodId(%s,%s)" % (goodId, type(goodId))
	goodDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_GOODS]
	if goodId not in goodDict or goodDict[goodId] is not True:
		#商品字典中不存在此商品或者是存在此商品但是设置了不可购买
		return
	
	config = WangZheZheKouHuiConfig.DiscountConfigDict.get(goodId)
	if config is None:
		return
	
	#购买次数
	buyCntDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_BUYRECORD]
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
	
	#剩余可抵用的今日消耗神石判断
	zheKouHuiUsedUnbindRMB = role.GetI32(EnumInt32.ZheKouHuiUsedUnbindRMB)
	if role.GetDayConsumeUnbindRMB() - zheKouHuiUsedUnbindRMB < config.needConsumeRMB:
		return
	
	prompt = GlobalPrompt.WZZKH_Tips_Head
	with Tra_WangZheZheKouHui_BuyGoods:
		#扣神石
		roleDecUnbindRMB(config.needUnbindRMB)
		#增加抵用今日消费神石数
		role.IncI32(EnumInt32.ZheKouHuiUsedUnbindRMB, config.needConsumeRMB)
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
	role.SendObj(WangZheZheKouHui_Data_S, [buyCntDict, goodDict])

def OnRefreshGoods(role, msg = None):
	'''
	公测折扣汇_请求刷新商品
	'''
	if IS_START is False:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	nowCnt = role.GetDI8(EnumDayInt8.WangZheZheKouHuiRefreshCnt) + 1
	
	#超过最大次数的话都按照最大次数来计算
	tmpCnt = nowCnt
	if nowCnt > WangZheZheKouHuiConfig.MAXREFRESHCNT:
		tmpCnt = WangZheZheKouHuiConfig.MAXREFRESHCNT
		
	price = WangZheZheKouHuiConfig.RefreshConfigDict.get(tmpCnt)
	if price is None:
		return
	
	#玩家的神石不够
	if price < 0 or role.GetUnbindRMB() < price:
		return
	
	with Tra_WangZheZheKouHui_RefreshGoods:
		if nowCnt <= 125:
			role.IncDI8(EnumDayInt8.WangZheZheKouHuiRefreshCnt, 1)
		if price > 0:
			role.DecUnbindRMB(price)
			
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveWangZheZheKouHuiRefresh, price)
		DoRefresh(role)
	#属性成功提示
	role.Msg(2, 0, GlobalPrompt.WangZheZheKouHui_Tips_Refresh % price)
	#最新数据同步
	goodDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_GOODS]
	buyDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_BUYRECORD]
	role.SendObj(WangZheZheKouHui_Data_S, [buyDict, goodDict])


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
	role.GetObj(EnumObj.WangZheGongCe)[IDX_GOODS] = goodDict

def GetRandomItemList(role):
	'''
	获取随机商品列表，这里动态的创建random rate因为每次的条件都会发生变化
	考虑到刷新的次数并不会很多，认为这样是可以接受的
	'''
	roleLevel = role.GetLevel()	
	randomList = WangZheZheKouHuiConfig.LevelRangeRandomDict.get(roleLevel)
	if randomList is None:
		print "GE_EXC,error while randomList = WangZheZheKouHuiConfig.LevelRangeRandomDict.get(roleLevel)(%s)" % roleLevel
		return None
	
	YDG = WangZheZheKouHuiConfig.DiscountConfigDict.get
	ranmRate = Random.RandomRate()
	RA = ranmRate.AddRandomItem
	
	for goodId, rate in randomList:
		config = YDG(goodId)
		if config is None:
			print "GE_EXC,error while role(%s) get random goodId in WangZheZheKouHui, no such goodID (%s) " % (role.GetRoleID(), goodId)
			return None
		buyCnt = role.GetObj(EnumObj.WangZheGongCe).get(IDX_BUYRECORD, {}).get(goodId, 0)
		if config.limitCnt > 0:
			if buyCnt >= config.limitCnt:
				continue
		RA(rate, goodId)
		
	return ranmRate.RandomMany(EnumGameConfig.ZheKouHui_RefreshCnt)


#事件 start
def OnInitRole(role, param = None):
	'''
	角色初始化相关key
	'''
	wangZheGongCeData = role.GetObj(EnumObj.WangZheGongCe)
	if IDX_BUYRECORD not in wangZheGongCeData:
		wangZheGongCeData[IDX_BUYRECORD] = {}
	if IDX_GOODS not in wangZheGongCeData:
		wangZheGongCeData[IDX_GOODS] = {}
	
def RoleDayClear(role, param):
	'''
	角色每日清理
	'''
	#重置抵用今日消费神石记录
	role.SetI32(EnumInt32.ZheKouHuiUsedUnbindRMB, 0)
	
	if IS_START is False:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	DoRefresh(role)
	buyDict = role.GetObj(EnumObj.WangZheGongCe).get(IDX_BUYRECORD, {})
	goodDict = role.GetObj(EnumObj.WangZheGongCe).get(IDX_GOODS, {})	
	role.SendObj(WangZheZheKouHui_Data_S, [buyDict, goodDict])
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartWangZheZheKouHui)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndWangZheZheKouHui)
				
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheZheKouHui_OnOpenPanel", "公测折扣汇_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheZheKouHui_OnBuyGoods", "公测折扣汇_请求购买商品"), OnBuyGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheZheKouHui_OnRefreshGoods", "公测折扣汇_请求刷新商品"), OnRefreshGoods)
