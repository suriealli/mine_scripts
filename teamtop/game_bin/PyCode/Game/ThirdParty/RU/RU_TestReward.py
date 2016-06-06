##!/usr/bin/env python
## -*- coding:UTF-8 -*-
## XRLAM("Game.ThirdParty.RU.RU_TestReward")
##===============================================================================
## 俄罗斯封测登录礼包
##===============================================================================
#import Environment
#from Game.Role import Event
#from Game.Role.Data import EnumDayInt1
#from Game.SysData import WorldData
#from ComplexServer.Log import AutoLog
#from Game.Role.Mail import Mail
#from Game.VIP import VIPConfig, VIPMgr
#
#
##金币，魔晶，系统神石，充值神石，物品列表
#Money = 10000000
#BindRMB = 5000
#UnBindRMB_S = 10000
#UnBindRMB_Q = 30000
#Items = (27536, 8)
#ConsumeQPoint = 5000
#
#if "_HasLoad" not in dir():
#	Tra_FengCe_Day_TestReward = AutoLog.AutoTransaction("Tra_FengCe_Day_TestReward", "封测登录奖励")
#
#
#def CheckTestReward(role, param = None):
#	if role.GetDI1(EnumDayInt1.RuDayReward):
#		return
#	with Tra_FengCe_Day_TestReward:
#		role.SetDI1(EnumDayInt1.RuDayReward, True)
#		if role.GetVIP() < 10:
#			UpdataVIP(role)
#		role.IncMoney(Money)
#		role.IncBindRMB(BindRMB)
#		role.IncUnbindRMB_S(UnBindRMB_S)
#		#role.IncUnbindRMB_Q(UnBindRMB_Q)
#		role.AddItem(*Items)
#
#def UpdataVIP(role):
#	#每天提升一次VIP
##	nowVIP = role.GetVIP()
##	nextVip = nowVIP + 1
##	nextLevelCfg = VIPConfig._VIP_BASE.get(nextVip)
##	if not nextLevelCfg:
##		return
##	ConsumeQPoint = role.GetConsumeQPoint()
##	if ConsumeQPoint > nextLevelCfg.growValue:
##		return
##	needQP = nextLevelCfg.growValue - ConsumeQPoint
##	if needQP > 0:
##		role.IncConsumeQPoint(needQP)
#	role.IncConsumeQPoint(ConsumeQPoint)
#	VIPMgr.VIPLevelUp(role)
#
#
#if "_HasLoad" not in dir():
#	if Environment.HasLogic and (not Environment.IsCross):
#		Event.RegEvent(Event.Eve_RoleDayClear, CheckTestReward)
#
#
