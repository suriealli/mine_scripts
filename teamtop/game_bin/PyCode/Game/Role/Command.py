#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Command")
#===============================================================================
# 角色离线命令
# 离线命令的格式有以下两种：
# 1. ("模块名", "函数名", 参数对象) 将调用 模块名.函数名(role, 参数对象)
# 2. Python代码，执行环境有role对象
# 注意，离线命令在执行的时候不要依赖全局数据，因为有可能是跨服执行。
# 故，如果执行的时候需要全局数据，请附带在参数对象或者执行代码中。
#===============================================================================
import traceback
import cProcess
import cComplexServer
import cRoleMgr
from Util import Function
from Common.Message import PyMessage
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.DB import DBProxy
from Game.Role import Event

def SendRoleCommand(roleid, command):
	'''
	发送离线命令
	@param roleid:角色id
	@param command:离线命令
	'''
	DBProxy.DBRoleVisit(roleid, "SaveCommand", (roleid, command))

def CheckCommandOnLogin(role, param):
	roleid = role.GetRoleID()
	command_size, command_index = role.GetCommand()
	if command_size == command_index:
		return
	DBProxy.DBRoleVisit(roleid, "LoadCommand", (roleid, cProcess.ProcessID, command_index), OnCommandReturn, (role, command_index))

def CheckCommand(role):
	roleid = role.GetRoleID()
	_, command_index = role.GetCommand()
	DBProxy.DBRoleVisit(roleid, "LoadCommand", (roleid, cProcess.ProcessID, command_index), OnCommandReturn, (role, command_index))

def OnCommandReturn(result, regparam):
	if result is None:
		print "GE_EXC, OnCommandReturn result is None"
		return
	with AutoLog.AutoTransaction(AutoLog.traRoleCommand):
		role, last_index = regparam
		_, command_index = role.GetCommand()
		# 在此期间，还没有改变过，则执行之
		if last_index != command_index:
			print "GE_EXC, command return error last_index(%s),command_index(%s)" % (last_index, command_index)
			return
		for index, command in result:
			if not role.DoCommand(index):
				return
			try:
				AutoLog.LogBase(role.GetRoleID(), AutoLog.eveRoleCommand, command)
				DoRoleCommand(role, command)
			except:
				print "GE_EXC, role(%s) do command(%s) error." % (role.GetRoleID(), command)
				traceback.print_exc()

def OnNotifyRoleCommand_Net(sessionid, roleids):
	CF = cRoleMgr.FindRoleByRoleID
	for roleid in roleids:
		role = CF(roleid)
		if not role:
			continue
		CheckCommand(role)

def OnNotifyRoleCommand_Local(result):
	CF = cRoleMgr.FindRoleByRoleID
	for row in result:
		roleid = row[0]
		role = CF(roleid)
		if not role:
			continue
		CheckCommand(role)

def DoRoleCommand(role, command):
	if command.startswith("("):
		moduleName, functionName, param = eval(command)
		fun = Function.FunctionUnpack(moduleName, functionName)
		apply(fun, (role, param))
	else:
		exec(command)

if "_HasLoad" not in dir():
	Event.RegEvent(Event.Eve_AfterLogin, CheckCommandOnLogin, (2038, 1, 1), 0)
	cComplexServer.RegDistribute(PyMessage.DB_NotifyCommand, OnNotifyRoleCommand_Net)

