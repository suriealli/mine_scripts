#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.GMRole")
#===============================================================================
# 内部号管理
#===============================================================================
import Environment
import cRoleDataMgr
from ComplexServer.API import GlobalHttp
from Game.Role.Data import EnumDisperseInt32, EnumInt1


def GMRoleLog(role, oldValue, newValue):
	#记录日志
	if newValue > oldValue:
		GlobalHttp.GMRoleUpdate(role)


def IsLock(role):
	if role.GetDI32(EnumDisperseInt32.GM_UnbindRMB) < 10000:
		return False
	if role.GetI1(EnumInt1.GMRoleLockFlag):
		#上次登录被封号了，但是又解封了，所以这里重新设置一下
		role.SetI1(EnumInt1.GMRoleLockFlag, 0)
		return False
	#封号
	role.SetI1(EnumInt1.GMRoleLockFlag, 1)
	role.SetCanLoginTime(200000000)
	return True



if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.GM_UnbindRMB, GMRoleLog)
	