#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.KuaFu")
#===============================================================================
# 跨服相关
#===============================================================================
import cRoleMgr
import Environment
from World import Define
from Util import Function
from Common import CValue
from Common.Message import AutoMessage
from ComplexServer.Time import Cron
from ComplexServer.Plug import Switch
from Game.Role.Data import EnumObj
from Game.SysData import WorldData

SCENE_INFO = 1
BACKFUN = 2
REGPARAM = 3
Env = 4 #1， 本服执行函数， 2， 跨服执行函数


#进行跨服，必须开服天数大于等于10天

def GetPid(role):
	'''获取角色原始进程ID'''
	return role.GetRoleID() / CValue.P2_32

def IsLocalServer(role):
	'''是否是本服(包括合服的角色)'''
	return role.GetPid() in Switch.LocalServerIDs

def IsLocalRoleByRoleID(roleId):
	'''是否是本服角色(没有绑定在role上的)'''
	return roleId / CValue.P2_32 in Switch.LocalServerIDs

Tips = "开服天数小于10天不能进行跨服"
def GotoCrossServer(role, crossid, scene_id, x, y, backfun, regparam):
	#去跨服
	if Environment.IsCross or WorldData.GetWorldKaiFuDay() < 10:
		#自己就是跨服 或者是开服天数小于10天，不能跨服
		role.Msg(2, 0, Tips)
		return
	if crossid is None:
		crossid = Define.GetDefaultCrossID()
		if not crossid:
			print "GE_EXC, GotoCrossServer error not crossid", crossid
			return
	obj = role.GetObj(EnumObj.ReConnect)
	obj[SCENE_INFO] = scene_id, x, y
	if backfun:
		obj[BACKFUN] = Function.FunctionPack(backfun)
		obj[REGPARAM] = repr(regparam)
		obj[Env] = 2#跨服执行函数
	role.SendObj(KuaFu_ReConnect, Define.CrossWorlds[crossid])

def GotoLocalServer(role, backfun, regparam):
	#回去本服
	if IsLocalServer(role):
		return
	obj = role.GetObj(EnumObj.ReConnect)
	if backfun:
		obj[BACKFUN] = Function.FunctionPack(backfun)
		obj[REGPARAM] = repr(regparam)
		obj[Env] = 1#本服环境下的执行函数
	role.SendObj(KuaFu_ReConnect, None)
	
	role.RegTick(60, CrossKick, None)

def CrossKick(role, callargv, regparam):
	#强制踢掉角色
	if role.IsKick():
		return
	role.Kick(True, 0)
	


def TestReConnect(role):
	if IsLocalServer(role):
		role.GotoCrossServer(None, 15, 0, 0, TestOnJoinScene, "from local server")
	else:
		role.GotoLocalServer(TestOnJoinScene, "from cross server")

def TestOnJoinScene(role, regparam):
	print "RED TestOnJoinScene", role.GetRoleID(), regparam


def CrossKickRole():
	#跨服准备跨天的时候把玩家都踢掉
	if not Environment.IsCross:
		return
	
	for role in cRoleMgr.GetAllRole():
		role.Kick(1, 1)

if "_HasLoad" not in dir():
	KuaFu_ReConnect = AutoMessage.AllotMessage("KuaFu_ReConnec", "命令客户端短线重连")
	
	if Environment.IsCross and Environment.HasLogic:
		Cron.CronDriveByMinute((2038, 1, 1), CrossKickRole, H = "H == 23", M = "M == 55")
		