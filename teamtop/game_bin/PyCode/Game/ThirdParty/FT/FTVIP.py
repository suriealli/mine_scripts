#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.FT.FTVIP")
#===============================================================================
# 繁體vip
#===============================================================================
import Environment
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumDisperseInt32


def OnLogin(role, param):
	if not Environment.EnvIsFT():
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	#設置繁體VIP
	role.SetDI32(EnumDisperseInt32.FTVIP, int(login_info.get("thirdparty", 0)))


if "_HasLoad" not in dir():
	if Environment.EnvIsFT():
		Event.RegEvent(Event.Eve_AfterLogin, OnLogin)
		#特殊事件触发
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnLogin, index = 0)