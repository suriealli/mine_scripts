#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.RoleWeek")
#===============================================================================
# 角色与周相关
#===============================================================================
import cDateTime
from Util import Time
from Game.Role import Event

def OnRoleDayClear(role, param):
	#每日清理调用
	
	#判断时间
	weeks = Time.GetAllWeeks(cDateTime.Now())
	if weeks > role.GetWeek():
		role.SetWeek(weeks)
		AfterChangeWeek(role)

def AfterChangeWeek(role):
	pass
	
	
	
if "_HasLoad" not in dir():
	#每日清理调用
	Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)



