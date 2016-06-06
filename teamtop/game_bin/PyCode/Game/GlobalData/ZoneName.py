#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.GlobalData.ZoneName")
#===============================================================================
# 游戏区名字
#===============================================================================
import cProcess
import Environment
from Common.Other import EnumSysData
from ComplexServer.API import GlobalHttp, Define
from Game.Role import Event
from Game.SysData import WorldData
from Game.Role import KuaFu


if "_HasLoad" not in dir():
	ZoneNameDict = {}
	ZoneName = cProcess.ProcessID


def AfterBack(response, regparam):
	if not response:
		print "GE_EXC ZoneName back error"
		return
	code, body = response
	if code != 200:
		print "GE_EXC, zoneName code error ", code
		return
	if body == Define.Error:
		print "GE_EXC, zoneName body error ", body
		return
	global ZoneNameDict
	if ZoneNameDict:
		return
	
	ZoneNameDict = eval(body)
	
	#初始化当前服务器名字
	global ZoneName
	ZoneName = GetZoneName(cProcess.ProcessID)
	#更新世界数据中的游戏服名字
	WorldData.WD[EnumSysData.ServerName] = ZoneName

def GetZoneName(zoneId):
	name = ZoneNameDict.get(zoneId)
	if not name:
		#没有找到，默认使用s + 区ID的形式 
		return "s" + str(zoneId)
	return name

def GetRoleZoneName(role):
	pid = KuaFu.GetPid(role)
	name = ZoneNameDict.get(pid)
	if not name:
		#没有找到，默认使用s + 区ID的形式 
		return "s" + str(pid)
	return name

def AfterLoadWorldData(param1, param2):
	#GlobalHttp.GetZoneName(AfterBack, None)
	#在更新之前暂时使用旧的名字
	global ZoneName
	ZoneName = WorldData.WD.get(EnumSysData.ServerName, cProcess.ProcessID)
	GetZoneNameEx()
	
def GetZoneNameEx():
	#只获取本服相关的名字
	from ComplexServer.Plug import Switch
	GlobalHttp.GetZoneNameEx(Switch.LocalServerIDs, AfterBack, None)


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)

