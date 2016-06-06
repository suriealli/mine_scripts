#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.KggRoleLevel.KggRoleLevel")
#===============================================================================
# KGG玩家到达指定等级发送数据
#===============================================================================
import Environment
from ComplexServer.API import GlobalHttp
from Game.Role import Event
from Game.Role.Data import EnumTempObj
import cProcess

LEVEL_UP_LEVEL = [2, 25, 35]	#玩家升到指定等级时发送数据

API_KEY = "1c7f71e9-d0c5-49a4-9a9a-15fc424d1470"
	
def KGGRoleLevel(role):
	account = role.GetTempObj(EnumTempObj.LoginInfo).get("account")
#	account = 11878202
	GlobalHttp.KGGRoleUserIDHttp(account, HttpBack, role.GetLevel())
	
def HttpBack(callargv, regparam):
	if not callargv:
		return
	code, userid = callargv
	if code != 200:
		return
	print userid
	level = regparam
	data = {}
	data["user_id"] = int(userid)
	data["api_key"] = API_KEY
	data["PlayerLevel"] = level
	data["server_id"] = cProcess.ProcessID
	GlobalHttp.KGGRoleLevelHttp(data, HttpBack2, None)
	
def HttpBack2(callargv, regparam):
	#print callargv
	pass
	
def SyncRoleOtherData(role, param):
	KGGRoleLevel(role)

def AfterLevelUp(role, param):
	level = role.GetLevel()
	if level not in LEVEL_UP_LEVEL:
		return
	KGGRoleLevel(role)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and Environment.IsKGG:
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)