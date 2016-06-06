#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Limit")
#===============================================================================
# 角色限制模块
# 这个模块对应于数据库进程的角色保存权限管理，用于管理角色在多个进程上的载入和保存。
#===============================================================================
import cComplexServer
import cRoleMgr
from Common.Message import PyMessage
from Common.Other import EnumKick

T_MAY_REPLACK = "你的角色在其他地方登录了！"
def OnRequestSaveRole(sessionid, msg):
	backfunid, roleid = msg
	role = cRoleMgr.FindRoleByRoleID(roleid)
	if role:
		role.Kick(True, EnumKick.RepeatLogin)
	cComplexServer.CallBackFunction(sessionid, backfunid, True)

def OnRequestKickRole(sessionid, msg):
	role = cRoleMgr.FindRoleByRoleID(msg)
	if role:
		role.Kick(False, EnumKick.RepeatLogin)

if "_HasLoad" not in dir():
	cComplexServer.RegDistribute(PyMessage.DB_MustSaveRole, OnRequestSaveRole)
	cComplexServer.RegDistribute(PyMessage.DB_MustKickRole, OnRequestKickRole)

