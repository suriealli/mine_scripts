#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Gua.Gua")
#===============================================================================
# 外挂处理
#===============================================================================
from Common.Message import AutoMessage
import cRoleMgr
import Environment
import cDateTime
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt8, EnumCD
from ComplexServer.API import GlobalHttp
from Game.ThirdParty import GameMsg




if "_HasLoad" not in dir():
	Trap_Bug_1 = AutoMessage.AllotMessage("Trap_Bug_1", "系统处理")
	Trap_Bug_2 = AutoMessage.AllotMessage("Trap_Bug_2", "系统处理")
	Trap_Bug_3 = AutoMessage.AllotMessage("Trap_Bug_3", "系统处理")
	Trap_Bug_4 = AutoMessage.AllotMessage("Trap_Bug_4", "系统处理")
	Trap_Bug_5 = AutoMessage.AllotMessage("Trap_Bug_5", "系统处理")
	Trap_Bug_6 = AutoMessage.AllotMessage("Trap_Bug_6", "系统处理")
	Trap_Bug_7 = AutoMessage.AllotMessage("Trap_Bug_7", "系统处理")
	Trap_Bug_8 = AutoMessage.AllotMessage("Trap_Bug_8", "系统处理")
	Trap_Bug_9 = AutoMessage.AllotMessage("Trap_Bug_9", "系统处理")
	Trap_Bug_10 = AutoMessage.AllotMessage("Trap_Bug_10", "系统处理")
	
	
	Tra_FB_Join = AutoLog.AutoTransaction("Tra_Gua", "使用外挂发封包封号")

OneDay = 60 * 60 * 24

WaiGuaMsg = "警告！根据系统自控程序检测到您的账号存在异常情况，请勿使用第三方软件或其他加速工具。为了您与他人的共同的游戏世界平衡，请您暂停使用。若后续还存在使用情况，我们将进行账号封停处理！"

def TrapBug(role, msg):
	if role.GetCD(EnumCD.WaiGuaChance):
		return
	with Tra_FB_Join:
		role.IncI8(EnumInt8.WaiGua, 1)
		nowCount = role.GetI8(EnumInt8.WaiGua)
		days = 7
		if nowCount == 1:
			role.SetCD(EnumCD.WaiGuaChance, 300)
			role.SendObjAndBack(GameMsg.GS_GameMSG, (WaiGuaMsg, ""), 600, AfterBack, None)
			return
		elif nowCount == 2:
			days = 1
		elif nowCount == 3:
			days = 3
		GlobalHttp.WaiGuaRoleUpdate(role, days, nowCount)
		role.SetCanLoginTime(cDateTime.Seconds() + (days * OneDay))

def AfterBack(role, cArgv, regparam):
	pass


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop):
		cRoleMgr.RegDistribute(Trap_Bug_1, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_2, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_3, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_4, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_5, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_6, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_7, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_8, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_9, TrapBug)
		cRoleMgr.RegDistribute(Trap_Bug_10, TrapBug)
		
		#旧的战斗消息
		Fight_SelectSkill = AutoMessage.AllotMessage("Fight_SelectSkill", "选择技能")
		cRoleMgr.RegDistribute(Fight_SelectSkill, TrapBug)

	
	