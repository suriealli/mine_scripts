#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.KuaFuJJC.KuaFuShopMgr")
#===============================================================================
# 跨服商店Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.SysData import WorldData
from Game.Role.Data import EnumObj
from Game.KuaFuJJC import KuaFuShopConfig

IDX_KUAFU_SHOP = 1

if "_HasLoad" not in dir():
	#消息同步
	KuaFuShop_ExchangeRecord_S = AutoMessage.AllotMessage("KuaFuShop_ExchangeRecord_S", "跨服商店_同步兑换记录")
	#日志
	Tra_KuaFuShop_ExchangeGood = AutoLog.AutoTransaction("Tra_KuaFuShop_ExchangeGood", "跨服商店_兑换商品")

#### 客户端请求 start
def OnOpenPanel(role, msg = None):
	'''
	跨服商店_请求打开商店面板
	'''
	if role.GetLevel() < EnumGameConfig.KuaFuShop_NeedLevel:
		return
	
	role.SendObj(KuaFuShop_ExchangeRecord_S, role.GetObj(EnumObj.KuaFuJJCData)[IDX_KUAFU_SHOP])
#	print "GE_EXC, OnOpenPanel::KuaFU_ExchangeRecord:: ",role.GetObj(EnumObj.KuaFuJJCData)[IDX_KUAFU_SHOP]

def OnExchangeGood(role, msg):
	'''
	跨服商店_请求兑换商品
	@param msg: goodId, exchangeCnt
	'''
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.KuaFuShop_NeedLevel:
		return
	
	targetGoodId, exchangeCnt = msg
	
	#兑换数量不合法
	if exchangeCnt < 1:
		return 
	#对应商品不存在
	exchangeCfg = KuaFuShopConfig.KuaFuShop_GoodsConfig_Dict.get(targetGoodId)
	if not exchangeCfg:
		return
	
	#玩家等级不够
	if roleLevel < exchangeCfg.needRoleLevel:
		return
	#世界等级不够
	if WorldData.GetWorldLevel() < exchangeCfg.needWorldLevel:
		return
	
	#剩余可兑换数量不足此次兑换请求
	exchangeRecordDict = (role.GetObj(EnumObj.KuaFuJJCData)).get(IDX_KUAFU_SHOP,{})
	if exchangeCfg.isLimit:
		boughtCnt = exchangeRecordDict.get(targetGoodId,0)
		if boughtCnt + exchangeCnt > exchangeCfg.limitCnt:
			return
	
	#兑换道具不足
	if role.ItemCnt(exchangeCfg.needCoding) < (exchangeCfg.needCnt * exchangeCnt):
		return
	
	prompt = GlobalPrompt.KuaFuShop_Tips_Head
	with Tra_KuaFuShop_ExchangeGood:
		#更新限购兑换商品兑换记录
		if exchangeCfg.isLimit:
			boughtCnt = exchangeRecordDict.setdefault(targetGoodId,0)
			exchangeRecordDict[targetGoodId] = boughtCnt + exchangeCnt
			role.GetObj(EnumObj.KuaFuJJCData)[IDX_KUAFU_SHOP] = exchangeRecordDict
		#扣除兑换道具
		role.DelItem(exchangeCfg.needCoding, (exchangeCfg.needCnt * exchangeCnt))
		#兑换获得道具
		coding, cnt = exchangeCfg.item
		prompt += GlobalPrompt.KuaFuShop_Tips_Item % (coding, cnt * exchangeCnt)
		role.AddItem(coding, cnt * exchangeCnt)
	
	#兑换成功提示
	role.Msg(2, 0, prompt)
	
	#同步最新兑换记录
	role.SendObj(KuaFuShop_ExchangeRecord_S, role.GetObj(EnumObj.KuaFuJJCData)[IDX_KUAFU_SHOP])
#	print "GE_EXC, AfterExchange::KuaFU_ExchangeRecord:: ",role.GetObj(EnumObj.KuaFuJJCData)[IDX_KUAFU_SHOP]

#### Event start
def OnRoleInit(role, param):
	'''
	初始化跨服商店兑换字典
	'''
	KuaFuJJCData = role.GetObj(EnumObj.KuaFuJJCData)
	if IDX_KUAFU_SHOP not in KuaFuJJCData:
		KuaFuJJCData[IDX_KUAFU_SHOP] = {}

def OnRoleDayClear(role, param = None):
	'''
	根据配置 每日清理对应购买记录 
	'''
	kuaFuShopData = role.GetObj(EnumObj.KuaFuJJCData)[IDX_KUAFU_SHOP]
	if not len(kuaFuShopData):
		return
	
	kuaFuShopDataNew = {}
	for goodId, boughtCnt in kuaFuShopData.iteritems():
		goodCfg = KuaFuShopConfig.KuaFuShop_GoodsConfig_Dict.get(goodId)
		if not goodCfg:
			continue
		if not goodCfg.isDayClear:
			kuaFuShopDataNew[goodId] = boughtCnt
	
	#更新
	role.GetObj(EnumObj.KuaFuJJCData)[IDX_KUAFU_SHOP] = kuaFuShopDataNew
	#同步最新兑换记录
	role.SendObj(KuaFuShop_ExchangeRecord_S, role.GetObj(EnumObj.KuaFuJJCData)[IDX_KUAFU_SHOP])
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		#消息请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFuShop_OnOpenPanel", "跨服商店_请求打开商店面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFuShop_OnExchangeGood", "跨服商店_请求兑换商品"), OnExchangeGood)