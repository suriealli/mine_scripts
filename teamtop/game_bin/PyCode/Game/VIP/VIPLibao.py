#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.VIP.VIPLibao")
#===============================================================================
# VIP礼包
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj, EnumTempObj
from Game.VIP import VIPConfig
from Game.Hero import HeroConfig
from Game.Role import Event

def RequestGetVIPLibao(role, param):
	'''
	客户端请求领取VIP礼包
	@param role:
	@param param:
	'''
	vip, index = param
	
	if index not in (1, 2): return	#参数有问题
	
	if role.GetVIP() < vip:
		return
	
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	getedstate = VIPLibaoData.setdefault(vip, 0)
	
	if getedstate >= index:
		return
	
	if index == 2 and getedstate == 0:#未领取免费礼包就买付费礼包，不正常！！
		print "GE_EXC,VIPLibao, player not get free viplibao but buy next viplibao"
		return
	
	if role.GetLevel() < 20 and vip in (4, 6, 8, 9):
		role.Msg(2, 0, GlobalPrompt.VIPLibaoLevel)
		return
	
	
	cfg = VIPConfig.VIP_REWARD_DICT.get(vip)
	if not cfg:
		print "GE_EXC,can not find vip(%s) in viplibao" % vip
		return
	
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	if index == 1 and cfg.hero1:
		if roleHeroMgr.IsHeroFull():
			role.Msg(2, 0, GlobalPrompt.HERO_IS_FULL)
			return
	if index == 2:
		if cfg.hero2 and roleHeroMgr.IsHeroFull():
			role.Msg(2, 0, GlobalPrompt.HERO_IS_FULL)
			return
		if role.GetUnbindRMB_Q() < cfg.reward2RMB:
			return
	with GetOrBuyVIPLibao:
		VIPLibaoData[vip] = index
		if index == 1:
			PayReward(role, cfg.serverReward1, cfg.gold1, cfg.bindRMB1, cfg.hero1, cfg.tarot1, vip)
		else:
			role.DecUnbindRMB_Q(cfg.reward2RMB)
			PayReward(role, cfg.serverReward2, cfg.gold2, cfg.bindRMB2, cfg.hero2, cfg.tarot2, vip)
		
		role.SendObj(Sync_Vip_Libao_Data, VIPLibaoData)
	
def PayReward(role, itemreward, gold, bindRMB, hero, tarot, vip):
	tips = ""
	tips2 = ""
	if itemreward:
		for reward in itemreward:
			role.AddItem(*reward)
			tips += GlobalPrompt.Item_Tips % (reward[0], reward[1])
			tips2 += GlobalPrompt.VIP_ITEM % (reward[0], reward[1])
	if gold:
		role.IncMoney(gold)
		tips += GlobalPrompt.Money_Tips % gold
		tips2 += GlobalPrompt.VIP_GOLD % gold
	if bindRMB:
		role.IncBindRMB(bindRMB)
		tips += GlobalPrompt.BindRMB_Tips % bindRMB
		tips2 += GlobalPrompt.VIP_BINDRMB % bindRMB
	if hero:
		role.AddHero(hero)
		tips2 += GlobalPrompt.VIP_HELO % (hero, 1)
		herocfg = HeroConfig.Hero_Base_Config.get(hero)
		if herocfg:
			name = herocfg.name
			tips += GlobalPrompt.ADD_HERO_MSG % name
	if tarot:
		role.AddTarotCard(tarot, 1)
		tips += GlobalPrompt.Tarot_Tips % (tarot, 1)
		tips2 += GlobalPrompt.VIP_TAROT % (tarot, 1)
	role.Msg(2, 0, tips)
	ctips = GlobalPrompt.VIP_LIBAO_MSG1 + tips2 + GlobalPrompt.VIP_LIBAO_MSG2
	cRoleMgr.Msg(11, 0, ctips % (role.GetRoleName(), vip))
	
def RequestGetCodingReward(role, param):
	'''
	客户端请求领取付费VIP礼盒奖励
	@param role:
	@param param:
	'''
	backId, itemId = param
	
	costItem = role.FindPackProp(itemId)
	if not costItem:
		return
	if costItem.IsDeadTime():
		return
	
	coding = costItem.otype
	cfg = VIPConfig.VIP_LIBAO_DICT.get(coding)
	if not cfg:
		return
	if not cfg.costUnbindRMB:
		return
	
	if role.GetUnbindRMB_Q() < cfg.costUnbindRMB:
		return
	
	if cfg.hero:#有奖励英雄，判断下英雄是否已满
		roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
		if roleHeroMgr.IsHeroFull():
			role.Msg(2, 0, GlobalPrompt.HERO_IS_FULL)
			return
	if role.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.LimitChest_PackageFullTips)
		return
	
	with CostRMBGetVIPReward:
		role.DecUnbindRMB_Q(cfg.costUnbindRMB)
		#扣除道具
		role.DelProp(itemId)
		tips = ""
		if cfg.hero:
			role.AddHero(cfg.hero)
			tips += GlobalPrompt.Hero_Tips % (cfg.hero, 1)
		if cfg.tarot:
			role.AddTarotCard(cfg.tarot, 1)
			tips += GlobalPrompt.Tarot_Tips % (cfg.tarot, 1)
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		if cfg.gold:
			role.IncMoney(cfg.gold)
			tips += GlobalPrompt.Money_Tips % cfg.gold
		if cfg.unbindRMB_S:
			role.IncUnbindRMB_S(cfg.unbindRMB_S)
			tips += GlobalPrompt.UnBindRMB_Tips % cfg.unbindRMB_S
		if cfg.serverReward:
			for coding, cnt in cfg.serverReward:
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
		role.Msg(2, 0, tips)
	role.CallBackFunction(backId, None)
	
def OnRoleLogin(role, param):
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	role.SendObj(Sync_Vip_Libao_Data, VIPLibaoData)
	
def OnSyncRoleOtherData(role, param):
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	role.SendObj(Sync_Vip_Libao_Data, VIPLibaoData)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		#日志
		GetOrBuyVIPLibao = AutoLog.AutoTransaction("GetOrBuyVIPLibao", "玩家领取或购买VIP礼包")
		CostRMBGetVIPReward = AutoLog.AutoTransaction("CostRMBGetVIPReward", "玩家花费神石开vip礼包")
		
		Sync_Vip_Libao_Data = AutoMessage.AllotMessage("Sync_Vip_Libao_Data", "同步VIP礼包领取信息")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Get_VIP_LIBAO", "客户端请求领取VIP礼包"), RequestGetVIPLibao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_CostRMB_Get_VIP_Reward", "客户端请求领取付费VIP礼盒奖励"), RequestGetCodingReward)
		
		