#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TiLi.TiLi")
#===============================================================================
# 体力相关
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Config import RoleBaseConfig
from Game.Role.Data import EnumDayInt8
from Game.VIP import VIPConfig

#所需魔晶：25+已购买次数*25
def OnBuyTiLi(role, msg):
	'''
	购买体力
	@param role:
	@param msg:None
	'''
	#体力已经不能购买了
	if role.GetTiLi() >= RoleBaseConfig.MaxTiLi:
		return
	
	times = role.GetDI8(EnumDayInt8.TiLi_Buy_Times)
	
	#普通玩家只能购买一次
	MaxTimes = EnumGameConfig.TiLi_Buy_Times
	#VIP特权
	vipConfig = VIPConfig._VIP_BASE.get(role.GetVIP())
	if vipConfig:
		MaxTimes = vipConfig.tili
	
	if times >= MaxTimes:
		role.Msg(2, 0, GlobalPrompt.TiLi_Buy_Times)
		return
	
	needRMB = EnumGameConfig.TiLi_Buy_RMB
	#版本判断
	if Environment.EnvIsNA():
		needRMB = EnumGameConfig.TiLi_Buy_RMB_NA
	elif Environment.EnvIsRU():
		needRMB = EnumGameConfig.TiLi_Buy_RMB_RU
		
	if role.GetRMB() < needRMB:
		return
	
	with TraBuyTiLi:
		role.SetDI8(EnumDayInt8.TiLi_Buy_Times, times + 1)
		role.DecRMB(needRMB)
		role.IncTiLi(EnumGameConfig.TiLi_Buy_TiLi)
		
		role.Msg(2, 0, GlobalPrompt.TiLi_Buy_Tips % EnumGameConfig.TiLi_Buy_TiLi)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TiLi_OnBugTiLi", "购买体力"), OnBuyTiLi)
		#日志
		TraBuyTiLi = AutoLog.AutoTransaction("TraBuyTiLi", "购买体力")
	
	
	