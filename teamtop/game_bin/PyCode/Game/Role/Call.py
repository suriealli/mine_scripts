#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Call")
#===============================================================================
# 角色呼叫(离线命令)
# 注意： 1 角色函数呼叫并不是马上执行，除数据库角色函数呼叫外，其他的函数呼叫都有可能不会执行。
#     2 角色函数呼叫是一个不可逆的状态，请尽量让呼叫的函数执行成功。
#     3 在角色登录触发AfterLogin事件后会触发向数据库异步查询离线命令等待返回执行
#     4 如果是别的进程发送这个角色的离线命令，会直接写到数据库，DB会每秒检测在线玩家的离线命令是否有更新，并且驱动执行
#     5 已经呼叫的函数，会把这个函数的模块名，函数名保存的数据库，请已经更新到外网的离线命令调用函数都不能删除和修改参数语义
#     6 如果要修改离线命令，最好就是新定义一个新的函数。原来的函数尽量不要修改
#===============================================================================
import sys
import cRoleMgr
import cComplexServer
from Common.Message import PyMessage
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.API import GlobalHttp
from Game.Role import Command

def LocalCall(roleid, fun, param):
	'''
	本地角色函数呼叫
	@param roleid:角色id
	@param fun:函数 def(role, param):
	@param param:函数参数
	'''
	role = cRoleMgr.FindRoleByRoleID(roleid)
	if not role: return False
	fun(role, param)
	return True

def DBCall(roleid, fun, param):
	'''
	数据库角色函数呼叫
	1 一定会尽快的呼叫且呼叫1次
	2 支持进程
	@param roleid:角色id
	@param fun:函数 def(role, param):
	@param param:函数参数
	'''
	Command.SendRoleCommand(roleid, repr((fun.__module__, fun.__name__, param)))

def LocalDBCall(roleid, fun, param):
	'''
	先尝试本地角色函数呼叫，如果不行再进行数据库角色函数呼叫
	@param roleid:角色id
	@param fun:函数 def(role, param):
	@param param:函数参数
	'''
	if not LocalCall(roleid, fun, param):
		DBCall(roleid, fun, param)

def ControlCall(roleid, fun, param):
	'''
	跨服角色函数呼叫
	@param roleid:角色id
	@param fun:函数 def(role, param):
	@param param:函数参数
	'''
	ControlProxy.SendControlMsg(PyMessage.Control_RoleCall, (roleid, fun.__module__, fun.__name__, param))


def RemoteCall(roleid, fun, param):
	'''
	远程角色函数呼叫
	@param roleid:角色id
	@param fun:函数 def fun(role, param):
	@param param:函数参数
	'''
	GlobalHttp.RoleCall(roleid, repr((fun.__module__, fun.__name__, param)))

def OnRoleCall(sessionid, msg):
	roleid, moduleName, funName, param = msg
	role = cRoleMgr.FindRoleByRoleID(roleid)
	if not role:
		return
	module = sys.modules.get(moduleName)
	if not module:
		print "GE_EXC, role(%s) OnRoleCall not find module(%s)." % (roleid, moduleName)
		return
	fun = getattr(module, funName, None)
	if not fun:
		print "GE_EXC, role(%s) OnRoleCall module(%s) not find fun(%s)." % (roleid, moduleName, funName)
		return
	fun(role, param)


def ServerCall(serverId, moduleName, funName, param):
	'''
	服务器call
	@param serverId: 如果serverid 为 0 时， 呼叫所有的逻辑进程(不包括跨服逻辑进程), 可以直接call跨服进程
	@param moduleName:
	@param funName:
	@param param:
	'''
	ControlProxy.SendControlMsg(PyMessage.Control_ServerCall, (serverId, moduleName, funName, param))

def SuperServerCall(serverId, moduleName, funName, param):
	'''
	服务器call 大消息
	@param serverId:
	@param moduleName:
	@param funName:
	@param param:
	'''
	ControlProxy.SendControlBigMsg(PyMessage.Control_SuperServerCall, (serverId, moduleName, funName, param))

	

def OnServerCall(sessionid, msg):
	moduleName, funName, param = msg
	module = sys.modules.get(moduleName)
	if not module:
		print "GE_EXC, OnServerCall not find module(%s)." % moduleName
		return
	fun = getattr(module, funName, None)
	if not fun:
		print "GE_EXC, OnServerCall module(%s) not find fun(%s)." % (moduleName, funName)
		return
	fun(param)

def OnSuperServerCall(sessionid, msg):
	moduleName, funName, param = msg
	module = sys.modules.get(moduleName)
	if not module:
		print "GE_EXC, OnSuperServerCall not find module(%s)." % moduleName
		return
	fun = getattr(module, funName, None)
	if not fun:
		print "GE_EXC, OnSuperServerCall module(%s) not find fun(%s)." % (moduleName, funName)
		return
	fun(param)


def ControlServerCall(moduleName, funName, param):
	'''
	呼叫控制进程调用某个函数
	@param fun:
	@param param:
	'''
	ControlProxy.SendControlMsg(PyMessage.Control_ControlServerCall, (moduleName, funName, param))


if "_HasLoad" not in dir():
	cComplexServer.RegDistribute(PyMessage.Control_OnRoleCall, OnRoleCall)
	cComplexServer.RegDistribute(PyMessage.Control_OnServerCall, OnServerCall)
	
	cComplexServer.RegDistribute(PyMessage.Control_OnSuperServerCall, OnServerCall)
	
	
