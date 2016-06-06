#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQXinShouCard.QQXinShouCard")
#===============================================================================
# QQ新手卡
#===============================================================================
import Environment
import cRoleDataMgr
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt1, EnumTempInt64


#app_custom=xinshouka
def SyncRoleOtherData(role, param):
	role.SetTI64(EnumTempInt64.QQXinShouCardFlag, 0)
	loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	app_custom = loginInfo.get("app_custom", "")
	if not app_custom:
		return
	
	if app_custom != "xinshouka":
		return
	
	if role.GetI1(EnumInt1.baiyinxinshouka) and role.GetI1(EnumInt1.huangjinxinshouka) and role.GetI1(EnumInt1.zhizunka):
		#3个CDKEY都领取了
		return
	
	role.SetTI64(EnumTempInt64.QQXinShouCardFlag, 1)


def AfterGetCDKEY(role, oldValue, newValue):
	role.SetTI64(EnumTempInt64.QQXinShouCardFlag, 0)


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop) and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleDataMgr.SetInt1Fun(EnumInt1.baiyinxinshouka, AfterGetCDKEY)
		cRoleDataMgr.SetInt1Fun(EnumInt1.huangjinxinshouka, AfterGetCDKEY)
		cRoleDataMgr.SetInt1Fun(EnumInt1.zhizunka, AfterGetCDKEY)
		
		