#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.PersistenceTick")
#===============================================================================
# 持久化Tick
#===============================================================================
import cDateTime
from Game.Role.Data import EnumInt32, EnumObj
from Game.Role import Event

def AllotID(role):
	index = EnumInt32.AllotID
	role.IncI32(index, 1)
	return role.GetI32(index)

def BindBackFun(funid, fun):
	if funid in BackFunctions:
		print "GE_EXC, repeat bind back fun id(%s)" % funid
	BackFunctions[funid] = fun

def RegPersistenceTick(role, unix_time, funid, regparam):
	pid = AllotID(role)
	role.GetObj(EnumObj.PersistenceTick)[pid] = unix_time, funid, regparam
	_RegTick(role, pid, unix_time)
	return pid

def _RegTick(role, pid, unix_time):
	now = cDateTime.Seconds()
	if now < unix_time:
		sec = unix_time - now
	else:
		sec = 0
	role.RegTick(sec, OnRoleTick, pid)

def OnRoleTick(role, callargv, pid):
	# 先获取函数id和参数
	info = role.GetObj(EnumObj.PersistenceTick).pop(pid, None)
	if info is None:
		print "GE_EXC, role(%s) persistence tick Error." % (role.GetRoleID())
		return
	_, funid, regparam = info
	# 查找函数
	fun = BackFunctions.get(funid)
	if fun is None:
		print "GE_EXC, role(%) can't find persistence tick fun id(%s)" % (role.GetRoleID(), funid)
		return
	fun(role, regparam)

def AfterLogin(role, param):
	for pid, info in role.GetObj(EnumObj.PersistenceTick).iteritems():
		_RegTick(role, pid, info[0])

# 函数ID定义
TestFunID = 0


if "_HasLoad" not in dir():
	BackFunctions = {}
	Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
	
	def TestBack(role, regparam):
		print "GREEN, persistence tick", role.GetRoleID()
		print regparam
	BindBackFun(TestFunID, TestBack)



