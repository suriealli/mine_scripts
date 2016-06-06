#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TiLiActivity.TiLiActivity")
#===============================================================================
# 开服体力活动，只有繁体版本有这个活动
#===============================================================================
import cDateTime
import cRoleMgr
import cNetMessage
import Environment
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from Game.SysData import WorldData
from Game.Role.Data import EnumDayInt1
from Game.Role import Event

if "_HasLoad" not in dir():
	#消息
	LevelNeeded = 20
	TiLiToInc = 150
	#消息
	Sync_TiLiActivity_IsStart = AutoMessage.AllotMessage("Sync_TiLiActivity_IsStart", "同步开服体力活动是否开启")
	#日志
	Tra_TiLiActivityGetTiLi = AutoLog.AutoTransaction("Tra_TiLiActivityGetTiLi", "玩家在开服体力活动 获得体力")

def RequestGetTiLi(role, msg):
	'''玩家请求获取体力
	@param role
	@param msg
	'''
	#只在繁体环境下开启
	if not Environment.EnvIsFT():
		return
	if cDateTime.Hour() != 12:
		return
	if role.GetLevel() < LevelNeeded:
		return
	#如果已经超出开服天数 
	if WorldData.GetWorldKaiFuDay() > 3:
		return
	#如果当日已经领取过
	if role.GetDI1(EnumDayInt1.FT_KaifuTili):
		return
	with Tra_TiLiActivityGetTiLi:
		role.SetDI1(EnumDayInt1.FT_KaifuTili, 1)
		role.IncTiLi(TiLiToInc)
	role.Msg(2, 0, GlobalPrompt.TiLi_Tips % TiLiToInc)

def IsActivityStart():
	#只在繁体环境下开启
	if not Environment.EnvIsFT():
		return
	if WorldData.GetWorldKaiFuDay() > 3:
		return
	if cDateTime.Hour() == 12:
		isStart = 1
	else:
		isStart = 0
	cNetMessage.PackPyMsg(Sync_TiLiActivity_IsStart, isStart)
	cRoleMgr.BroadMsg()

def AfterLogin(role, param):
	#只在繁体环境下开启
	if not Environment.EnvIsFT():
		return
	if WorldData.GetWorldKaiFuDay() > 3:
		return
	if cDateTime.Hour() != 12:
		return
	role.SendObj(Sync_TiLiActivity_IsStart, 1)

if "_HasLoad" not in dir():
	if Environment.HasLogic and Environment.EnvIsFT() and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, AfterLogin)
		
		
		Cron.CronDirveByHour((2038, 1, 1), IsActivityStart, H="H in (12,13)")
		#客户端请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetTiLi_TiLiActivity", "开服体力活动客户端请求获得体力"), RequestGetTiLi)
