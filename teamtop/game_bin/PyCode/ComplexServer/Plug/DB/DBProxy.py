#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.DB.DBProxy")
#===============================================================================
# DB访问代理
#===============================================================================
import copy
import cComplexServer
from Common import CValue
from Common.Connect import Who
from Common.Message import PyMessage
from Util import Trace, Callback
from ComplexServer import Connect, BigMessage
from ComplexServer.Plug.DB import DBWork, DBHelp

BesideCls = set(["SaveRole", "TimeOutUnSale", "SendMail", "SaveCommand", "TimeOutUnSale"])
TraceEmptyTransaction = False

def __DBVisit_Local(dbid, channel, classname, arg = None, backfun = None, regparam = None):
	'''
	DB本地直接访问
	@param dbid:数据库ID（没用）
	@param channel:数据访问线程 None:公共队列
	@param classname:数据访问类名
	@param arg:参数
	@param backfun:回调函数 def fun(ret, regparam)
	@param regparam:回调参数
	'''
	#if cComplexServer.IsTimeDriver() and classname not in BesideCls:
	#	print "BLUE, db visit(%s) in time driver." % classname
	DBWork.OnDBVisit_MainThread(channel, classname, copy.deepcopy(arg), (backfun, regparam))


def __DBVisit_Big_Local(dbid, channel, classname, arg = None):
	'''
	DB本地直接访问(大数据)
	@param dbid:数据库ID（没用）
	@param channel:数据访问线程 None:公共队列
	@param classname:数据访问类名
	@param arg:参数
	'''
	DBWork.OnDBVisit_MainThread(channel, classname, copy.deepcopy(arg), (None, None))


def __DBLogBase_Local(logid, roleid, transaction, event, content):
	'''
	基本日志（本地）
	@param logid:日志ID
	@param roleid:角色ID
	@param transaction:事务
	@param event:事件
	@param content:内容
	'''
	if TraceEmptyTransaction and transaction == 0:
		Trace.StackWarn("empty transaction.")
	DBWork.OnDBVisit_MainThread(None, "LogBase", (logid, roleid, transaction, event, content), (None, None))

def __DBLogObj_Local(logid, roleid, transaction, event, obj_id, obj_type, obj_int, obj_data, content):
	'''
	对象日志（本地）
	@param logid:日志ID
	@param roleid:角色ID
	@param transaction:事务
	@param event:事件
	@param obj_id:对象ID
	@param obj_type:对象类型
	@param obj_int:对象个数
	@param obj_data:对象数据
	@param content:内容
	'''
	if TraceEmptyTransaction and transaction == 0:
		Trace.StackWarn("empty transaction.")
	DBWork.OnDBVisit_MainThread(None, "LogObj", (logid, roleid, transaction, event, obj_id, obj_type, obj_int, obj_data, content), (None, None))

def __DBLogValue_Local(logid, roleid, transaction, event, old, new, content):
	'''
	数值日志（本地）
	@param logid:日志ID
	@param roleid:角色ID
	@param transaction:事务
	@param event:事件
	@param old:旧值
	@param new:新值
	@param content:内容
	'''
	if TraceEmptyTransaction and transaction == 0:
		Trace.StackWarn("empty transaction.")
	DBWork.OnDBVisit_MainThread(None, "LogValue", (logid, roleid, transaction, event, old, new, content), (None, None))

#===============================================================================
#网络模式
#===============================================================================
def __DBVisit_Net(dbid, channel, classname, arg = None, backfun = None, regparam = None):
	'''
	DB远程代理访问
	@param dbid:数据库ID
	@param channel:数据访问线程 None:公共队列
	@param classname:数据访问类名
	@param arg:参数
	@param backfun:回调函数 def fun(ret, regparam)
	@param regparam:回调参数
	'''
	sessionid = DB_INFO.get(dbid)
	if sessionid is None :
		print "GE_EXC, can't find session by dbid(%s) for class(%s)." % (dbid, classname)
		Trace.StackWarn("__DBVisit_Net can't find session." + str(arg))
		return
	if backfun:
		cComplexServer.SendPyMsgAndBack(sessionid, PyMessage.DB_VisitAndBack, (channel, classname, arg), WAIT_TIME, backfun, regparam)
	else:
		cComplexServer.SendPyMsg(sessionid, PyMessage.DB_Visit, (channel, classname, arg))

def __DBVisit_Big_Net(dbid, channel, classname, arg = None):
	'''
	DB远程代理访问(大数据)
	@param dbid:数据库ID
	@param channel:数据访问线程 None:公共队列
	@param classname:数据访问类名
	@param arg:参数
	'''
	sessionid = DB_INFO.get(dbid)
	if sessionid is None :
		print "GE_EXC, can't find session by dbid(%s) for class(%s)." % (dbid, classname)
		Trace.StackWarn("__DBVisit_Big_Net can't find session.")
		return
	BigMessage.Send(sessionid, PyMessage.DB_Visit, (channel, classname, arg))


def __DBLogBase_Net(logid, roleid, transaction, event, content):
	'''
	基本日志（网络）
	@param logid:日志ID
	@param roleid:角色ID
	@param transaction:事务
	@param event:事件
	@param content:内容
	'''
	dbid = DBHelp.GetDBIDByRoleID(roleid)
	sessionid = DB_INFO.get(dbid)
	if sessionid is None :
		print "GE_EXC, can't find session by dbid(%s) for LogBase." % dbid
		Trace.StackWarn("__DBLogBase_Net can't find session.")
		return
	cComplexServer.SendPyMsg(sessionid, PyMessage.DB_LogBase, (logid, roleid, transaction, event, content))

def __DBLogObj_Net(logid, roleid, transaction, event, obj_id, obj_type, obj_int, obj_data, content):
	'''
	对象日志（网络）
	@param logid:日志ID
	@param roleid:角色ID
	@param transaction:事务
	@param event:事件
	@param obj_id:对象ID
	@param obj_type:对象类型
	@param obj_int:对象个数
	@param obj_data:对象数据
	@param content:内容
	'''
	dbid = DBHelp.GetDBIDByRoleID(roleid)
	sessionid = DB_INFO.get(dbid)
	if sessionid is None :
		print "GE_EXC, can't find session by dbid(%s) for LogObj." % dbid
		Trace.StackWarn("__DBLogObj_Net can't find session.")
		return
	cComplexServer.SendPyMsg(sessionid, PyMessage.DB_LogObj, (logid, roleid, transaction, event, obj_id, obj_type, obj_int, obj_data, content))

def __DBLogValue_Net(logid, roleid, transaction, event, old, new, content):
	'''
	数值日志（网络）
	@param logid:日志ID
	@param roleid:角色ID
	@param transaction:事务
	@param event:事件
	@param old:旧值
	@param new:新值
	@param content:内容
	'''
	dbid = DBHelp.GetDBIDByRoleID(roleid)
	sessionid = DB_INFO.get(dbid)
	if sessionid is None :
		print "GE_EXC, can't find session by dbid(%s) for LogValue." % dbid
		Trace.StackWarn("__DBLogValue_Net can't find session.")
		return
	cComplexServer.SendPyMsg(sessionid, PyMessage.DB_LogValue, (logid, roleid, transaction, event, old, new, content))

def OnDBVisit_Net(sessionid, msg):
	'''
	DB远程代理收到访问消息，真正访问
	@param sessionid:连接的sessionid
	@param msg:请求访问消息
	'''
	channel, classname, arg = msg
	DBWork.OnDBVisit_MainThread(channel, classname, arg, (sessionid, 0))

def OnDBVisitAndBack_Net(sessionid, msg):
	'''
	DB远程代理收到访问消息并回调，真正访问
	@param sessionid:连接的sessionid
	@param msg:请求访问消息
	'''
	backfunid, (channel, classname, arg) = msg
	DBWork.OnDBVisit_MainThread(channel, classname, arg, (sessionid, backfunid))

def OnDBLogBase_Net(sessionid, msg):
	'''
	收到基本日志
	@param sessionid:连接的sessionid
	@param msg:基本日志
	'''
	DBWork.OnDBVisit_MainThread(None, "LogBase", msg, (0, 0))

def OnDBLogObj_Net(sessionid, msg):
	'''
	收到对象日志
	@param sessionid:连接的sessionid
	@param msg:对象日志
	'''
	DBWork.OnDBVisit_MainThread(None, "LogObj", msg, (0, 0))

def OnDBLogValue_Net(sessionid, msg):
	'''
	收到数值日志
	@param sessionid:连接的sessionid
	@param msg:数值日志
	'''
	DBWork.OnDBVisit_MainThread(None, "LogValue", msg, (0, 0))

def NetMethod():
	'''
	设置DB访问模式为远程代理访问
	'''
	global DBVisit, DBLogBase, DBLogObj, DBLogValue, DBBigVisit
	DBVisit = __DBVisit_Net
	DBLogBase = __DBLogBase_Net
	DBLogObj = __DBLogObj_Net
	DBLogValue = __DBLogValue_Net
	DBBigVisit = __DBVisit_Big_Net

def ConnectDBServer(argv = None, param = None):
	'''
	真正的连接远程代理
	@param argv:兼容tick系统的占位参数
	@param param:连接参数
	'''
	dbid, ip, port = param
	sessionid = cComplexServer.Connect(ip, port, Who.enWho_Logic, 1000, CValue.MAX_UINT16, 1000, CValue.MAX_UINT16)
	if sessionid == CValue.MAX_UINT32:
		cComplexServer.RegTick(5, ConnectDBServer, param)
	else:
		DB_INFO[dbid] = sessionid
		DB_SESSION[sessionid] = (dbid, ip, port)
		# 触发连接数据库的回调
		ConnectDBServerCallBack.CallAllFunctions(sessionid, dbid, ip, port)

def OnLost(sessionid):
	'''
	当远程代理断开连接的时候，自动重连
	@param sessionid:
	'''
	# 如果是关服状态，就不要断线重连了
	from ComplexServer import Init
	if Init.IsStopState:
		return
	cComplexServer.RegTick(5, ConnectDBServer, DB_SESSION[sessionid])
	if sessionid in DB_SESSION: del DB_SESSION[sessionid]
	
	print "GE_EXC, DB Lost"

def IAMDBServer():
	'''
	对于远程代理，注册好DB代理请求的处理函数
	'''
	cComplexServer.RegDistribute(PyMessage.DB_Visit, OnDBVisit_Net)
	cComplexServer.RegDistribute(PyMessage.DB_VisitAndBack, OnDBVisitAndBack_Net)
	cComplexServer.RegDistribute(PyMessage.DB_LogBase, OnDBLogBase_Net)
	cComplexServer.RegDistribute(PyMessage.DB_LogObj, OnDBLogObj_Net)
	cComplexServer.RegDistribute(PyMessage.DB_LogValue, OnDBLogValue_Net)
	DBWork.NetModel()

def DBRoleVisit(roleid, classname, arg = None, backfun = None, regparam = None):
	'''
	某个角色访问DB
	@param roleid:角色ID
	@param classname:访问名
	@param arg:参数
	@param backfun:回调函数 def(result, regparam)
	@param regparam:回调参数
	'''
	dbid = DBHelp.GetDBIDByRoleID(roleid)
	channel = DBHelp.GetDBChannelByRoleID(roleid)
	DBVisit(dbid, channel, classname, arg, backfun, regparam)

def CanDBVisit(dbid):
	'''
	能否访问某个DB
	@param dbid:数据库ID
	'''
	if DBVisit == __DBVisit_Local:
		return True
	elif DBVisit == __DBVisit_Net:
		return dbid in DB_INFO
	else:
		return False

if "_HasLoad" not in dir():
	WAIT_TIME = 60
	DB_INFO = {}
	DB_SESSION = {}
	DBVisit = __DBVisit_Local
	DBBigVisit = __DBVisit_Big_Local
	DBLogBase = __DBLogBase_Local
	DBLogObj = __DBLogObj_Local
	DBLogValue = __DBLogValue_Local
	ConnectDBServerCallBack = Callback.LocalCallback()
	# 设置远程代理端口连接的时候重连机制
	Connect.LostConnectCallBack.RegCallbackFunction(Who.enWho_Logic, OnLost)

