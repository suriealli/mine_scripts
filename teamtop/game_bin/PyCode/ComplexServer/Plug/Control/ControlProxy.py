#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.Control.ControlProxy")
#===============================================================================
# 全局控制代理模块
# 注意，这里如果控制和逻辑在一个进程，要注意深拷贝一份消息，因为双方逻辑有可能是直接保存消息
#===============================================================================
import copy
import traceback
import cComplexServer
from Common import CValue
from Common.Connect import Who
from ComplexServer import Connect, BigMessage

def IsLocal():
	return CONTROL_SESSION is None

def SendControlMsg(msgtype, msg):
	'''
	给控制进程发消息
	@param msgtype:消息类型
	@param msg:消息
	'''
	if CONTROL_SESSION is None:
		fun = cComplexServer.GetDistribute(msgtype)
		if fun is None:
			print "GE_EXC, can't find distribute by msg(%s)" % msgtype
			return
		try:
			fun(CValue.MAX_UINT32, copy.deepcopy(msg))
		except:
			traceback.print_exc()
	else:
		cComplexServer.SendPyMsg(CONTROL_SESSION, msgtype, msg)
	


def SendControlBigMsg(msgtype, msg):
	'''
	给控制进程发消息
	@param msgtype:消息类型
	@param msg:消息
	'''
	if CONTROL_SESSION is None:
		fun = cComplexServer.GetDistribute(msgtype)
		if fun is None:
			print "GE_EXC, can't find distribute by msg(%s)" % msgtype
			return
		try:
			fun(CValue.MAX_UINT32, copy.deepcopy(msg))
		except:
			traceback.print_exc()
	else:
		BigMessage.Send(CONTROL_SESSION, msgtype, msg)


def SendControlMsgAndBack(msgtype, msg, backfun, regparam):
	'''
	给控制进程发消息并且等待回调
	@param msgtype:消息类型
	@param msg:消息
	@param backfun:回调函数
	@param regparam:注册参数
	'''
	if CONTROL_SESSION is None:
		fun = cComplexServer.GetDistribute(msgtype)
		if fun is None:
			print "GE_EXC, can't find distribute by msg(%s)" % msgtype
			return
		try:
			fun(CValue.MAX_UINT32, ((backfun, regparam), copy.deepcopy(msg)))
		except:
			traceback.print_exc()
	else:
		cComplexServer.SendPyMsgAndBack(CONTROL_SESSION, msgtype, msg, 60, backfun, regparam)

def SendLogicMsg(sessionid, msgtype, msg):
	'''
	给逻辑进程发消息
	@param sessionid:连接id
	@param msgtype:消息类型
	@param msg:消息体
	'''
	if CONTROL_SESSION is None:
		fun = cComplexServer.GetDistribute(msgtype)
		if fun is None:
			print "GE_EXC, can't find distribute by msg(%s)" % msgtype
			return
		try:
			fun(sessionid, copy.deepcopy(msg))
		except:
			traceback.print_exc()
	else:
		cComplexServer.SendPyMsg(sessionid, msgtype, msg)



def SendLogicBigMsg(sessionid, msgtype, msg):
	'''
	给逻辑进程发消息 大消息
	@param sessionid:连接id
	@param msgtype:消息类型
	@param msg:消息体
	'''
	if CONTROL_SESSION is None:
		fun = cComplexServer.GetDistribute(msgtype)
		if fun is None:
			print "GE_EXC, can't find distribute by msg(%s)" % msgtype
			return
		try:
			fun(sessionid, copy.deepcopy(msg))
		except:
			traceback.print_exc()
	else:
		BigMessage.Send(sessionid, msgtype, msg)



def SendLogicMsgAndBack(sessionid, msgtype, msg, backfun, regparam):
	'''
	给控制进程发消息并且等待回调
	@param msgtype:消息类型
	@param msg:消息
	@param backfun:回调函数
	@param regparam:注册参数
	'''
	if CONTROL_SESSION is None:
		fun = cComplexServer.GetDistribute(msgtype)
		if fun is None:
			print "GE_EXC, can't find distribute by msg(%s)" % msgtype
			return
		try:
			fun(sessionid, ((backfun, regparam), copy.deepcopy(msg)))
		except:
			traceback.print_exc()
	else:
		cComplexServer.SendPyMsgAndBack(sessionid, msgtype, msg, 60, backfun, regparam)

def CallBackFunction(sessionid, functionid, callargv):
	'''
	控制进程和逻辑进程之间触发回调函数
	@param sessionid:连接id
	@param functionid:函数id
	@param callargv:呼叫参数
	'''
	if CONTROL_SESSION is None:
		try:
			backfun, regparam = functionid
			backfun(copy.deepcopy(callargv), regparam)
		except:
			traceback.print_exc()
	else:
		cComplexServer.CallBackFunction(sessionid, functionid, callargv)

def NetMethod(pid, ip, port):
	'''
	逻辑进程以网络模式连接控制进程
	@param ip:连接的ip
	@param port:连接的端口
	'''
	global CONTROL_SESSION, CONTROL_IP, CONTROL_PORT, ControlApply
	CONTROL_SESSION = CValue.MAX_UINT32
	CONTROL_IP = ip
	CONTROL_PORT = port
	ConnectControlServer()

def IAMControlServer():
	'''
	我是控制进程服务器
	'''
	global CONTROL_SESSION
	CONTROL_SESSION = CValue.MAX_UINT32

def ConnectControlServer(argv = None, param = None):
	'''
	真正的连接远程代理
	@param argv:兼容tick系统的占位参数
	@param param:连接参数
	'''
	global CONTROL_SESSION
	CONTROL_SESSION = cComplexServer.Connect(CONTROL_IP, CONTROL_PORT, Who.enWho_Control, 1000, CValue.MAX_UINT16, 1000, CValue.MAX_UINT16)
	if CONTROL_SESSION == CValue.MAX_UINT32:
		#连接不上15秒之后尝试再次连接
		cComplexServer.RegTick(15, ConnectControlServer)
	
	
def OnLost(sessionid):
	'''
	当远程代理断开连接的时候，自动重连
	@param sessionid:
	'''
	# 如果是关服状态，就不要断线重连了
	from ComplexServer import Init
	if Init.IsStopState:
		return
	global CONTROL_SESSION
	CONTROL_SESSION = CValue.MAX_UINT32
	cComplexServer.RegTick(5, ConnectControlServer)

if "_HasLoad" not in dir():
	CONTROL_SESSION = None
	CONTROL_IP = None
	CONTROL_PORT = None
	# 设置远程代理端口连接的时候重连机制
	Connect.LostConnectCallBack.RegCallbackFunction(Who.enWho_Control, OnLost)

