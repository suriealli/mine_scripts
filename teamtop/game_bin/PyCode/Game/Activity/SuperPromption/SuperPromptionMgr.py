#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SuperPromption.SuperPromptionMgr")
#===============================================================================
# 超值特惠 Mgr
#===============================================================================
import cRoleMgr
import cNetMessage
import cComplexServer
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.SysData import WorldData
from Game.Persistence import Contain
from Game.Activity.SuperPromption import SuperPromptionConfig

if "_HasLoad" not in dir():
	SP_OpenActive_Set = set([])			#缓存当前开启的活动
	
	SuperPromption_OpenSet_S = AutoMessage.AllotMessage("SuperPromption_OpenSet_S", "超值特惠_同步当前开启的活动类型集合")
	SuperPromption_BuyRecord_S = AutoMessage.AllotMessage("SuperPromption_BuyRecord_S", "超值特惠_同步购买记录")
	
	Tra_SuperPromption_BuyGoods = AutoLog.AutoTransaction("Tra_SuperPromption_BuyGoods", "超值特惠_购买商品")
	
def OnStartSuperPromption(calArgv, regparam):
	_, activeType = regparam
	if activeType in SP_OpenActive_Set:
		print "GE_EXC,repeat start SuperPromption activeType(%s)" % activeType
		return
	
	#缓存开启
	SP_OpenActive_Set.add(activeType)
	#同步当前最新活动开启集合
	cNetMessage.PackPyMsg(SuperPromption_OpenSet_S, SP_OpenActive_Set)
	cRoleMgr.BroadMsg()
	
	#同步最新
	for tmpRole in cRoleMgr.GetAllRole():
		tmpRoleId = tmpRole.GetRoleID()
		tmpRole.SendObj(SuperPromption_BuyRecord_S, SUPERPROMTION_BUY_RECORD_PDICT.get(tmpRoleId, {}))
	
def OnEndSuperPromption(calArgv, regparam):
	_, activeType = regparam
	if activeType not in SP_OpenActive_Set:
		print "GE_EXC, end SuperPromption activeType(%s) while not open" % activeType
		return
	
	#移除开启
	SP_OpenActive_Set.discard(activeType)
	#同步当前最新活动开启集合
	cNetMessage.PackPyMsg(SuperPromption_OpenSet_S, SP_OpenActive_Set)
	cRoleMgr.BroadMsg()
	
	#清除活动的所有玩家购买记录
	hasChange = False
	toDelRoleSet = set([])
	global SUPERPROMTION_BUY_RECORD_PDICT
	for tmpRoleId, tmpBuyRecord in SUPERPROMTION_BUY_RECORD_PDICT.iteritems():
		if activeType in tmpBuyRecord:
			hasChange = True
			del tmpBuyRecord[activeType]
			if len(tmpBuyRecord) < 1:
				toDelRoleSet.add(tmpRoleId)
				
	for tmpRoleId in toDelRoleSet:
		if tmpRoleId in SUPERPROMTION_BUY_RECORD_PDICT:
			hasChange = True
			del SUPERPROMTION_BUY_RECORD_PDICT[tmpRoleId]
	
	if hasChange:
		SUPERPROMTION_BUY_RECORD_PDICT.HasChange()

#### 请求 start
def OnOpenPanel(role, msg = None):
	'''
	超值特惠_请求打开面板
	'''
	if len(SP_OpenActive_Set) < 1:
		return
	
	#购买记录
	role.SendObj(SuperPromption_BuyRecord_S, SUPERPROMTION_BUY_RECORD_PDICT.get(role.GetRoleID(), {}))

def OnBuyGood(role, msg):
	'''
	超值特惠_请求购买商品
	@param msg: goodsType, cnt 商品类型 
	'''
	goodsType, cnt = msg
	if cnt < 1:
		return
	
	#未开启该类特惠礼包
	if goodsType not in SP_OpenActive_Set:
		return
	
	#没有对应配置
	goodsCfg = SuperPromptionConfig.GetCfgByTypeAndKaiFuDay(goodsType, WorldData.GetWorldKaiFuDay())
	if not goodsCfg:
		return
	
	#等级不足
	if role.GetLevel() < goodsCfg.needLevel:
		return
	
	#今日充值神石数不足解锁商品购买条件
	if role.GetDayBuyUnbindRMB_Q() < goodsCfg.dayBuyRMBLimit:
		return
	
	#剩余充值神石不足
	needUnbindRMB = goodsCfg.needUnbindRMB * cnt
	if role.GetUnbindRMB_Q() < needUnbindRMB:
		return
	
	#此次请求是否导致限购超标
	roleId = role.GetRoleID()
	limitCnt = goodsCfg.limitCnt
	if limitCnt:
		global SUPERPROMTION_BUY_RECORD_PDICT
		buyRecordDict = SUPERPROMTION_BUY_RECORD_PDICT.get(roleId, {})
		boughtCnt = buyRecordDict.get(goodsType, 0)
		if boughtCnt + cnt > limitCnt:
			return
		else:
			buyRecordDict[goodsType] = boughtCnt + cnt
		
	with Tra_SuperPromption_BuyGoods:
		#更新购买记录
		if limitCnt:
			SUPERPROMTION_BUY_RECORD_PDICT[roleId] = buyRecordDict
		#扣除神石
		role.DecUnbindRMB_Q(needUnbindRMB)
		#发物品
		for itemCoding, itemCnt in goodsCfg.realItems:
			role.AddItem(itemCoding, itemCnt * cnt)
		#发金币
		rewardMoney = goodsCfg.rewardMoney
		if rewardMoney:
			rewardMoney *= cnt
			role.IncMoney(rewardMoney)
		#发奖励神石
		rewardRMB = goodsCfg.rewardRMB
		if rewardRMB:
			rewardRMB *= cnt
			role.IncUnbindRMB_S(rewardRMB)
		#记个购买log
		AutoLog.LogObj(roleId, AutoLog.eveSuperPromptionBuy, 0, goodsCfg.goodsId, cnt, 0)
		#AutoLog.LogBase(roleId, AutoLog.eveSuperPromptionBuy, (goodsCfg.goodsId, cnt))
	
	#同步最新购买记录
	role.SendObj(SuperPromption_BuyRecord_S, buyRecordDict)
	#出购买成功提示
	role.Msg(2, 0, GlobalPrompt.SuperPromption_Tips_Success)
	
#### 事件
def OnRoleOtherData(role, param = None):
	'''
	玩家上线 同步当前开启的活动类型集合 和 购买记录
	'''
	#开启集合
	role.SendObj(SuperPromption_OpenSet_S, SP_OpenActive_Set)
	#购买记录
	role.SendObj(SuperPromption_BuyRecord_S, SUPERPROMTION_BUY_RECORD_PDICT.get(role.GetRoleID(), {}))

def AfterNewDay():
	'''
	新的一天  同步购买记录
	'''
	for tmpRole in cRoleMgr.GetAllRole():
		tmpRoleId = tmpRole.GetRoleID()
		tmpRole.SendObj(SuperPromption_BuyRecord_S, SUPERPROMTION_BUY_RECORD_PDICT.get(tmpRoleId, {}))
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#超值特惠玩家购买记录 {roleId:{goodsType:cnt},}
		SUPERPROMTION_BUY_RECORD_PDICT = Contain.Dict("SuperPromption_Buy_Record", (2038, 1, 1))
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnRoleOtherData)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
				
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SuperPromption_OnOpenPanel", "超值特惠_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SuperPromption_OnBuyGood", "超值特惠_请求购买商品"), OnBuyGood)	
