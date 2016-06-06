#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQRoleBack.MyRoleBack")
#===============================================================================
# 国服角色回流(注意区别腾讯第三方的回流活动)
#===============================================================================
import Environment
from ComplexServer.API import GlobalHttp
from Game.Role import Event
from Game.Role.Data import EnumTempObj


adtag = "CLIENT.QQ.5389_.0"

def FirstInitRole(role, param):
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	#adtagparam = login_info.get("adtag")
	#if not adtagparam:
	#	return
	#if adtagparam != adtag:
	#	return
	GlobalHttp.CheckMyRoleBack(login_info["account"], CheckBack, role)


def CheckBack(callargv, regparam):
	#print "CheckBack", callargv
	role = regparam
	if role.IsKick():
		return
	if not callargv:
		return
	code, body = callargv
	if code != 200:
		return
	viplevel = eval(body)
	if viplevel is None:
		return
	
	Event.TriggerEvent(Event.Eve_RoleBackVIPLevel, role, viplevel)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop) and (not Environment.IsCross):
		Event.RegEvent(Event.Eve_FirstInitRole, FirstInitRole)
