#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TimeLimitGoods.TimeLimitGoods")
#===============================================================================
# 限时商城
#===============================================================================
import cRoleMgr
import Environment
import cDateTime
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity.TimeLimitGoods import TimeLimitGoodsConfig
from Game.Role.Data import EnumObj

GOODS_TYPE_CODING = 1	#道具
GOODS_TYPE_PET = 2		#宠物
GOODS_TYPE_HERO = 3		#英雄

def RequestBuyTimeLimitGoods(role, param):
	'''
	客户端请求购买限时商品
	@param role:
	@param param:
	'''
	goodsId, cnt = param
	
	if not goodsId:
		return
	
	cfg = TimeLimitGoodsConfig.TIME_LIMIT_GOODS_DICT.get(goodsId)
	if not cfg:
		print "GE_EXC, can not find goodsId(%s) in TimeLimitGoods" % goodsId
		return
	
	now = cDateTime.Now()
	if now < cfg.startTime or now > cfg.endTime:#过期
		return
	
	if role.GetLevel() < cfg.needLevel:#等级不足
		return
		
	if cfg.needQ:
		if role.GetUnbindRMB_Q() < cfg.needUnbindRMB * cnt:
			return
	else:
		if role.GetUnbindRMB() < cfg.needUnbindRMB * cnt:
			return
	
	TimeLimitDict = role.GetObj(EnumObj.NATimeLimitBuyData)
	if cfg.buyLimit:
		buyType, maxcnt = cfg.buyLimit
		buyData = {}
		if buyType == 1:#每日清理
			buyData = TimeLimitDict.get(1, {})
		else:
			buyData = TimeLimitDict.get(2, {})
			
		buy_cnt = buyData.get(goodsId, 0)
		if buy_cnt + cnt > maxcnt:
			return
		else:
			buyData[goodsId] = buyData.get(goodsId, 0) + cnt
			
	with BuyTimeLimitGoods:
		if cfg.needQ:
			role.DecUnbindRMB_Q(cfg.needUnbindRMB * cnt)
		else:
			role.DecUnbindRMB(cfg.needUnbindRMB * cnt)
		if cfg.goodsType == GOODS_TYPE_CODING:
			role.AddItem(cfg.coding, cnt)
		elif cfg.goodsType == GOODS_TYPE_PET:
			for _ in xrange(cnt):
				role.AddPet(cfg.coding)
		elif cfg.goodsType == GOODS_TYPE_HERO:
			for _ in xrange(cnt):
				role.AddHero(cfg.coding)
		if cfg.buyLimit:
			role.SendObj(Syn_TimeLimit_data, TimeLimitDict)
			
		role.Msg(2, 0, GlobalPrompt.MallBuyOk )
			
def RequestOpenTimeLimitGoods(role, param):
	'''
	客户端请求打开限时商品界面
	@param role:
	@param param:
	'''
	TimeLimitDict = role.GetObj(EnumObj.NATimeLimitBuyData)
	role.SendObj(Syn_TimeLimit_data, TimeLimitDict)
	
def AfterLogin(role, param):
	#玩家登录
	TimeLimitDict = role.GetObj(EnumObj.NATimeLimitBuyData)
	if 1 not in TimeLimitDict:
		TimeLimitDict[1] = {}
	if 2 not in TimeLimitDict:
		TimeLimitDict[2] = {}
	
def RoleDayClear(role, param):
	#每日清理
	TimeLimitDict = role.GetObj(EnumObj.NATimeLimitBuyData)
	TimeLimitDict[1] = {}
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsNA() or Environment.IsDevelop):
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		#日志
		BuyTimeLimitGoods = AutoLog.AutoTransaction("BuyTimeLimitGoods", "限时商城购买")
		
		Syn_TimeLimit_data = AutoMessage.AllotMessage("Syn_TimeLimit_data", "同步限时商城已购买信息")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Buy_TimeLimitGoods", "客户端请求购买限时商品"), RequestBuyTimeLimitGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Opne_TimeLimitGoods", "客户端请求打开限时商品界面"), RequestOpenTimeLimitGoods)
		
	