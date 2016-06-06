#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.VIP.SuperVIP")
#===============================================================================
# 超级贵族
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt32
from Game.VIP import VIPConfig
from Game.Activity.Title import Title, TitleConfig

def RequestSuperVIPShopExchange(role, param):
	'''
	客户端请求使用超级vip积分兑换奖励
	@param role:
	@param param:
	'''
	index = param
	if index <= 0: return
	
	cfg = VIPConfig.SUPER_VIP_POINT_SHOP.get(index)
	if not cfg:
		print "GE_EXC, can not find index(%s) in RequestSuperVIPShopExchange" % index
		return
	
	if cfg.needSuperVIP > role.GetVIP():
		return
	
	if cfg.needPoint:
		if role.GetI32(EnumInt32.SuperVIPPoint) < cfg.needPoint:
			return
	
	if cfg.needRMB_Q:
		if role.GetUnbindRMB_Q() < cfg.needRMB_Q:
			return
		
	if cfg.needRMB_S:
		if role.GetUnbindRMB() < cfg.needRMB_S:
			return
	
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	gettedData = VIPLibaoData.setdefault(21, {})
	if cfg.timesLimit > 0:
		if gettedData.get(index, 0) >= cfg.timesLimit:
			return
		
	with ExchangeSuperVIPPoint:
		if cfg.needPoint:
			role.DecI32(EnumInt32.SuperVIPPoint, cfg.needPoint)
		if cfg.needRMB_Q:
			role.DecUnbindRMB_Q(cfg.needRMB_Q)
		if cfg.needRMB_S:
			role.DecUnbindRMB(cfg.needRMB_S)
		if cfg.timesLimit > 0:
			gettedData[index] = gettedData.get(index, 0) + 1
		
		tips = GlobalPrompt.Reward_Tips
		if cfg.codingRewards:
			role.AddItem(cfg.codingRewards[0], cfg.codingRewards[1])
			tips += GlobalPrompt.Item_Tips % (cfg.codingRewards[0], cfg.codingRewards[1])
		if cfg.talentCard:
			role.AddTalentCard(cfg.talentCard)
			tips += GlobalPrompt.Talent_Tips % (cfg.talentCard, 1)
		if cfg.tarotReward:
			role.AddTarotCard(cfg.tarotReward, 1)
			tips += GlobalPrompt.Tarot_Tips % (cfg.tarotReward, 1)
		role.SendObj(Sync_SuperVip_Exchange_Data, gettedData)
		
		role.Msg(2, 0, tips)
		
def RequestGetSuperVIPReward(role, param):
	'''
	客户端请求领取超级VIP奖励
	@param role:
	@param param:
	'''
	index = param
	
	if index <= 0: return
	
	if role.GetVIP() < 10:
		return
	
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	superdata = VIPLibaoData.setdefault(20, set())
	if index in superdata:
		#已经领取过了
		return
	
	super_cfg = VIPConfig.SUPER_VIP_REWARD_DICT.get(index)
	if not super_cfg:
		print "GE_EXC,can not find index(%s) in RequestGetSuperVIPReward" % index
		return
		
	DayBuyRMB_Q = role.GetDayBuyUnbindRMB_Q()
	if DayBuyRMB_Q < super_cfg.needRMB_Q:
		return
	
	with GetSuperVIPRwward:
		VIPLibaoData[20].add(index)
		
		tips = GlobalPrompt.Reward_Tips
		for reward in super_cfg.rewards:
			role.AddItem(*reward)
			tips += GlobalPrompt.Item_Tips % (reward[0], reward[1])
		
		if super_cfg.addExp:
			LevelUpSuperVIP(role, super_cfg.addExp)
			tips += GlobalPrompt.SUPER_VIP_ADD_EXP_MSG % super_cfg.addExp
		
		role.SendObj(Sync_SuperVip_Reward_Data, VIPLibaoData[20])
		
		role.Msg(2, 0, tips)
		
def RequestOpenSuperVIPPanel(role, param):
	'''
	打开超级vip等级界面
	@param role:
	@param param:
	'''
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	role.SendObj(Sync_SuperVip_Reward_Data, VIPLibaoData.get(20, set()))
	
def RequestOpenSuperVIPPointPanel(role, param):
	'''
	打开超级vip积分界面
	@param role:
	@param param:
	'''
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	role.SendObj(Sync_SuperVip_Exchange_Data, VIPLibaoData.get(21, {}))
	
def ActiveSuperVIPTitle(role, param):
	'''
	客户端请求领取超级VIP称号
	@param role:
	@param param:
	'''
	backId, titleId = param
	
	Titlecfg = TitleConfig.Title_Dict.get(titleId)
	if not Titlecfg:
		print "GE_EXC, error in AddTitle not this cfg (%s)" % titleId
		return
	
	cfg = VIPConfig.SUPER_VIP_TITLE_DICT.get(titleId)
	if not cfg:
		print "GE_EXC,can not find titleid(%s) in ActiveSuperVIPTitle" % titleId
		return
	
	if role.GetLevel() < cfg.needRoleLevel:
		return
	
	if role.GetVIP() < cfg.needVIPLevel:
		return
	
	Title.AddTitle(role.GetRoleID(), titleId)
	role.CallBackFunction(backId, 1)
#=============================================================================
def LevelUpSuperVIP(role, exp):
	#增加超级VIP经验，并尝试升级超级vip
	vip = role.GetVIP()
	if vip < 10: return
	
	role.IncI32(EnumInt32.SuperVIPExp, exp)
	
	vipLevel = vip + 1
	next_cfg = VIPConfig._VIP_BASE.get(vipLevel)
	if not next_cfg:
		#可能已经最高级了
		return

	now_exp = role.GetI32(EnumInt32.SuperVIPExp)
	
	if now_exp < next_cfg.needExp:
		return
	
	while 1:
		nextLevelCfg = VIPConfig._VIP_BASE.get(vipLevel + 1)
		if not nextLevelCfg:
			break
		if now_exp < nextLevelCfg.needExp:
			#少于下一级的成长值，暂时不能升级
			break
		vipLevel += 1
	role.SetVIP(vipLevel)
	cRoleMgr.Msg(11, 0, GlobalPrompt.SUPER_VIP_LEVEL_UP % (role.GetRoleName(), vipLevel - 10))
	
def AfterChangeUnbindRMB(role, param):
	#监听Q点神石数值变化
	return
	oldValue, newValue = param
	if newValue >= oldValue:
		return
	
	if role.GetVIP() < 10:
		return
	
	costRMB = oldValue - newValue
	AddSuperVipPoint(role, costRMB)
	
def AfterChangeUnbindRMB_S(role, param):
	return
	#监听系统神石数值变化
	oldValue, newValue = param
	if newValue >= oldValue:
		return
	
	if role.GetVIP() < 10:
		return
	
	costRMB = oldValue - newValue
	AddSuperVipPoint(role, costRMB)
	
def AddSuperVipPoint(role, costRMB):
	#增加超级贵族vip积分
	with IncSuperVIPPoint:
		role.IncI32(EnumInt32.SuperVIPPoint, costRMB * EnumGameConfig.SUPER_VIP_RMB_POINT)
	
def AfterLogin(role, param):
	#玩家登陆
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	if 20 not in VIPLibaoData:
		VIPLibaoData[20] = set()
	if 21 not in VIPLibaoData:
		VIPLibaoData[21] = {}
		
	role.SendObj(Sync_SuperVip_Reward_Data, VIPLibaoData.get(20, set()))
	
def SyncRoleOtherData(role, param):
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	role.SendObj(Sync_SuperVip_Reward_Data, VIPLibaoData.get(20, set()))
	
def RoleDayClear(role, param):
	#每日清理
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	VIPLibaoData[20] = set()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB)
		Event.RegEvent(Event.AfterChangeUnbindRMB_S, AfterChangeUnbindRMB_S)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#日志
		GetSuperVIPRwward = AutoLog.AutoTransaction("GetSuperVIPRwward", "玩家领取超级VIP每日奖励")
		IncSuperVIPPoint = AutoLog.AutoTransaction("IncSuperVIPPoint", "增加玩家超级VIP积分")
		ExchangeSuperVIPPoint = AutoLog.AutoTransaction("ExchangeSuperVIPPoint", "超级贵族积分兑换奖励")
		
		Sync_SuperVip_Reward_Data = AutoMessage.AllotMessage("Sync_SuperVip_Reward_Data", "同步超级vip每日领取记录")
		Sync_SuperVip_Exchange_Data = AutoMessage.AllotMessage("Sync_SuperVip_Exchange_Data", "同步超级vip积分兑换记录")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Open_VIPLevel_Panel", "打开超级vip等级界面"), RequestOpenSuperVIPPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Open_VIPPoint_Panel", "打开超级vip积分界面"), RequestOpenSuperVIPPointPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Get_Super_VIP_Reward", "客户端请求领取超级VIP奖励"), RequestGetSuperVIPReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Get_Super_VIP_ShopExchange", "客户端请求使用超级vip积分兑换奖励"), RequestSuperVIPShopExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Active_SuperVIP_Title", "客户端请求领取超级VIP称号"), ActiveSuperVIPTitle)
		